

from fastapi import FastAPI, UploadFile, File, HTTPException
from models import DriverData, TimelineEvent, SnippetMeta
from datetime import datetime
from typing import List, Dict
import uuid
import os
import secrets

from logic import (
    compute_fatigue_instant,
    compute_fatigue_personalized,
    forecast_next_scores,
    decide_escalation,
    escalation_action
)


from cryptography.fernet import Fernet

from datetime import datetime



# --- ADAPTIVE ESCALATION STATE (per user) ---
driver_escalation_state: Dict[str, dict] = {}

# --- PERSONALIZED PROFILES (in-memory for now) ---
user_profiles: Dict[str, dict] = {}

app = FastAPI(title="NeuroDrive Backend")

# In-memory stores
alerts: List[dict] = []
fatigue_history: List[dict] = []           # legacy / simple list
driver_timeline: Dict[str, List[dict]] = {}  # user_id -> list of events
incident_snippets: Dict[str, dict] = {}      # event_id -> snippet meta


# --- SNIPPET STORAGE / ENCRYPTION ---
SNIPPETS_DIR = "snippets"
os.makedirs(SNIPPETS_DIR, exist_ok=True)

# NOTE: in production, read key from env instead of generating each run
ENCRYPTION_KEY = os.environ.get("NEURODRIVE_SNIPPET_KEY") or Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)




# In-memory store


@app.get("/")
def home():
    return {"message": "NeuroDrive backend running"}
from typing import List

@app.post("/calibrate/{user_id}")
def calibrate(user_id: str, open_ears: List[float], closed_ears: List[float]):
    open_avg = sum(open_ears) / len(open_ears)
    closed_avg = sum(closed_ears) / len(closed_ears)

    blink_low = closed_avg + 0.1 * (open_avg - closed_avg)
    blink_high = open_avg - 0.1 * (open_avg - closed_avg)

    user_profiles[user_id] = {
        "open_ear": open_avg,
        "closed_ear": closed_avg,
        "blink_low": blink_low,
        "blink_high": blink_high,
        "ema_open": open_avg,
        "ema_closed": closed_avg
    }

    return {
        "message": "Calibration complete",
        "profile": user_profiles[user_id]
    }

from logic import compute_fatigue_instant, compute_fatigue_personalized

@app.post("/predict")
def predict(data: DriverData):

    # 1. Compute fatigue score based on mode
    if data.mode == "instant":
        score = compute_fatigue_instant(
            data.eye_ratio,
            data.blink_count,
            data.head_tilt,
            data.yawn_ratio
        )

    elif data.mode == "personalized":
        if data.user_id not in user_profiles:
            raise HTTPException(status_code=400, detail="User not calibrated")

        score = compute_fatigue_personalized(
            user_profiles[data.user_id],
            data.eye_ratio,
            data.blink_count,
            data.head_tilt,
            data.yawn_ratio
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid mode")

    status = "alert" if score > 60 else "normal"

    # 2. Derive event_type and tags (for timeline)
    if score > 80:
        event_type = "critical_fatigue"
    elif score > 60:
        event_type = "fatigue_warning"
    else:
        event_type = "normal"

    tags: list[str] = []
    if event_type != "normal":
        tags.append(event_type)

    if data.yawn_ratio is not None and data.yawn_ratio > 0.6:
        tags.append("yawn")

    if data.blink_count > 10:
        tags.append("high_blink_rate")

    if abs(data.head_tilt) > 15:
        tags.append("head_tilt")

    # 3. Build event record
    event_id = str(uuid.uuid4())
    ts = datetime.now().isoformat()

    event_record = {
        "event_id": event_id,
        "timestamp": ts,
        "user_id": data.user_id,
        "mode": data.mode,
        "fatigue_score": score,
        "status": status,
        "event_type": event_type,
        "tags": tags,
        "eye_ratio": data.eye_ratio,
        "blink_count": data.blink_count,
        "head_tilt": data.head_tilt,
        "yawn_ratio": data.yawn_ratio,
        "has_snippet": False
    }
    

    # 4. Append to global histories
    fatigue_history.append(event_record)

    if data.user_id not in driver_timeline:
        driver_timeline[data.user_id] = []
    driver_timeline[data.user_id].append(event_record)
   

    # 5. Legacy alerts list (optional)
    alerts.append({"score": score, "status": status})

    # ---------- ADAPTIVE ESCALATION SYSTEM ----------

    now_ts = datetime.now().timestamp()

    # Initialize user state if new
    if data.user_id not in driver_escalation_state:
        driver_escalation_state[data.user_id] = {
            "level": 0,
            "last_change": now_ts,
            "recent_scores": []
        }

    state = driver_escalation_state[data.user_id]

    # Maintain rolling window of last 10 scores
    state["recent_scores"].append(score)
    state["recent_scores"] = state["recent_scores"][-10:]

    # Predict future trend using EMA forecast
    forecast = forecast_next_scores(state["recent_scores"], steps=5)

    # Decide next escalation level
    new_level = decide_escalation(
        level=state["level"],
        score=score,
        forecast=forecast
    )

    # Reset escalation if driver recovers
    if score < 45:
        new_level = 0

    # Update state if level changed
    if new_level != state["level"]:
        state["level"] = new_level
        state["last_change"] = now_ts

    # Get physical/system action
    intervention = escalation_action(state["level"])
    event_record["escalation_level"] = driver_escalation_state[data.user_id]["level"]
    event_record["intervention"] = intervention

    return {
        "fatigue_score": score,
        "status": status,
        "intervention": intervention,
        "escalation_level": state["level"],
        "mode": data.mode,
        "event_id": event_id,
        "event_type": event_type,
        "tags": tags,
        "forecast": forecast
    }


@app.get("/escalation/{user_id}")
def get_escalation_state(user_id: str):
    if user_id not in driver_escalation_state:
        return {"message": "No escalation state for this user yet"}

    return driver_escalation_state[user_id]


# ---------- HISTORY ----------
@app.get("/history")
def get_history():
    """
    Returns last 50 fatigue readings for visualization.
    """
    return fatigue_history[-50:]

# ---------- SUMMARY ----------
@app.get("/summary")
def summary():
    """
    Provides quick stats for dashboard cards.
    """
    if not fatigue_history:
        return {
            "avg_score": 0,
            "max_score": 0,
            "alert_events": 0,
            "total_records": 0
        }

    scores = [r["fatigue_score"] for r in fatigue_history]
    alerts_count = sum(1 for r in fatigue_history if r["status"] == "alert")

    return {
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": max(scores),
        "alert_events": alerts_count,
        "total_records": len(scores)
    }


# ---------- OPTIONAL ----------
@app.get("/alerts")
def get_alerts():
    return alerts

@app.get("/timeline/{user_id}")
def get_timeline(user_id: str, limit: int = 50):
    """
    Returns last `limit` events for a given driver.
    This is your 'driver awareness log'.
    """
    events = driver_timeline.get(user_id, [])
    if not events:
        return []
    # return newest last
    return events[-limit:]

@app.get("/timeline/{user_id}/{event_id}")
def get_event(user_id: str, event_id: str):
    """
    Returns a single event with full details, including snippet flag.
    """
    events = driver_timeline.get(user_id, [])
    for e in events:
        if e["event_id"] == event_id:
            return e
    raise HTTPException(status_code=404, detail="Event not found")

@app.post("/timeline/{user_id}/{event_id}/snippet")
async def upload_snippet(
    user_id: str,
    event_id: str,
    file: UploadFile = File(...)
):
    """
    Attach an encrypted video snippet to a specific event.
    - Stores encrypted .enc file on disk
    - Marks event.has_snippet = True
    - Creates snippet metadata with share_token
    """
    # 1. Verify event exists and belongs to this user
    events = driver_timeline.get(user_id, [])
    target_event = None
    for e in events:
        if e["event_id"] == event_id:
            target_event = e
            break

    if target_event is None:
        raise HTTPException(status_code=404, detail="Event not found for user")

    # 2. Read file contents
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    # 3. Encrypt and store file
    encrypted = fernet.encrypt(contents)
    safe_name = f"{event_id}.enc"
    file_path = os.path.join(SNIPPETS_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(encrypted)

    # 4. Generate share token (for future controlled sharing)
    share_token = secrets.token_urlsafe(16)

    # 5. Update in-memory structures
    target_event["has_snippet"] = True

    snippet_meta = {
        "event_id": event_id,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "file_name": safe_name,
        "duration_seconds": None,   # frontend/camera can fill later
        "share_token": share_token
    }
    incident_snippets[event_id] = snippet_meta

    return {
        "message": "Snippet uploaded and encrypted",
        "event_id": event_id,
        "share_token": share_token
    }

@app.get("/snippet/share/{share_token}")
def get_shared_snippet_meta(share_token: str):
    """
    Returns minimal info for a shared incident snippet, identified by share_token.
    Does NOT expose file path (you can later add a secure download endpoint).
    """
    # Find snippet by token
    for event_id, meta in incident_snippets.items():
        if meta.get("share_token") == share_token:
            # Find corresponding event
            user_id = meta["user_id"]
            events = driver_timeline.get(user_id, [])
            event = next((e for e in events if e["event_id"] == event_id), None)
            if not event:
                raise HTTPException(status_code=404, detail="Associated event not found")

            # Return sanitized view
            return {
                "event": {
                    "event_id": event["event_id"],
                    "timestamp": event["timestamp"],
                    "user_id": event["user_id"],
                    "mode": event["mode"],
                    "fatigue_score": event["fatigue_score"],
                    "status": event["status"],
                    "event_type": event["event_type"],
                    "tags": event["tags"],
                },
                "snippet_available": True
            }

    raise HTTPException(status_code=404, detail="Invalid share token")
