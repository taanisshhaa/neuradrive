import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore
from firebase_store import db

from fastapi import Depends
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException
from models import DriverData, TimelineEvent, SnippetMeta, EmergencyContact
from datetime import datetime
from typing import List, Dict
import uuid
import time
import os
import secrets
from cryptography.fernet import Fernet
from twilio.rest import Client 
from logic import (
    compute_fatigue_instant,
    compute_fatigue_personalized,
    forecast_next_scores,
    decide_escalation,
    escalation_action
)
from dotenv import load_dotenv
load_dotenv()
FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS")

firebase_app = None
db = None

if FIREBASE_CREDENTIALS_PATH and os.path.exists(FIREBASE_CREDENTIALS_PATH):
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_app = firebase_admin.initialize_app(cred, {
        "projectId": os.environ.get("FIREBASE_PROJECT_ID")
    })
    db = firestore.client()
else:
    # You can log or print a warning here; for now we just skip
    print("WARNING: Firebase credentials not configured; running without Firestore.")
import firebase_store 

# after db is created:
if db is not None:
    from firebase_store import init_firestore
    init_firestore(db)

print("🔥 Firebase DB object:", db)


# Import LangGraph workflow
from workflow import driver_workflow

# Initialize agent references to global state
from agents import fatigue_scoring_agent, forecast_agent, escalation_agent
from agents import emergency_agent, timeline_logging_agent



from cryptography.fernet import Fernet
import requests

from datetime import datetime
from models import (
    DriverData,
    TimelineEvent,
    SnippetMeta,
    EmergencyContact,
    SafeStopRequest,
    SafeStopPlace,
)



# --- ADAPTIVE ESCALATION STATE (per user) ---
driver_escalation_state: Dict[str, dict] = {}

# --- PERSONALIZED PROFILES (in-memory for now) ---
user_profiles: Dict[str, dict] = {}

app = FastAPI(title="NeuroDrive Backend")
# --- EMERGENCY CONTACTS (per user) ---
emergency_contacts: Dict[str, List[dict]] = {}   # user_id -> list of {phone_number, name}
last_emergency_sms: Dict[str, float] = {}        # user_id -> last-sent timestamp
EMERGENCY_COOLDOWN_SECONDS = 5                 # 5 minutes cooldown between SMS for same user

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

# --- SNIPPET STORAGE / ENCRYPTION ---
SNIPPETS_DIR = "snippets"
os.makedirs(SNIPPETS_DIR, exist_ok=True)

ENCRYPTION_KEY = os.environ.get("NEURODRIVE_SNIPPET_KEY") or Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)

# --- TWILIO CONFIG ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception:
        twilio_client = None  # Fail safe: app should still run without SMS

# --- GOOGLE MAPS CONFIG ---
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
from fastapi import Depends, Header

class CurrentUser(BaseModel):
    uid: str
    email: str | None = None
    name: str | None = None

def get_current_user(authorization: str = Header(None)) -> CurrentUser:
    """
    Validates Firebase ID token from Authorization: Bearer <token>.
    Returns CurrentUser with uid/email/name.
    """
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    if firebase_app is None:
        raise HTTPException(status_code=500, detail="Firebase not initialized on backend")

    try:
        decoded = firebase_auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase ID token: {str(e)}")

    return CurrentUser(
        uid=decoded.get("uid"),
        email=decoded.get("email"),
        name=decoded.get("name") or decoded.get("displayName")
    )

@app.get("/debug/firestore-events/{user_id}")
def debug_firestore_events(user_id: str):
    if db is None:
        return {"error": "Firestore not initialized"}

    docs = db.collection("users").document(user_id).collection("events").stream()
    return [doc.to_dict() for doc in docs]


def find_safe_stops(
    lat: float,
    lng: float,
    max_distance_m: int = 5000,
    max_results: int = 5,
) -> List[SafeStopPlace]:
    """
    Uses Google Places Nearby Search to find safe pull-over locations
    like parking lots, rest areas, or gas stations.
    Falls back to dummy data if API key is missing or request fails.
    """
    # If no API key, return dummy suggestions near given lat/lng (for local testing)
    if not GOOGLE_MAPS_API_KEY:
        return [
            SafeStopPlace(
                name="Demo Rest Stop",
                lat=lat + 0.001,
                lng=lng + 0.001,
                address="Demo Street 1",
                type="demo_rest_area",
                rating=4.5,
                user_ratings_total=120,
                maps_url=f"https://www.google.com/maps/search/?api=1&query={lat+0.001},{lng+0.001}",
            ),
            SafeStopPlace(
                name="Demo Parking Area",
                lat=lat - 0.001,
                lng=lng - 0.001,
                address="Demo Street 2",
                type="demo_parking",
                rating=4.2,
                user_ratings_total=80,
                maps_url=f"https://www.google.com/maps/search/?api=1&query={lat-0.001},{lng-0.001}",
            ),
        ]

    # 1. Try to find parking areas first
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": max_distance_m,
        "type": "parking",
        "key": GOOGLE_MAPS_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json() if resp.status_code == 200 else {}
    except Exception:
        data = {}

    results = data.get("results", [])

    # 2. If no parking found, broaden search (gas station, rest area)
    if not results:
        alt_params = {
            "location": f"{lat},{lng}",
            "radius": max_distance_m,
            "keyword": "rest area OR lay-by OR highway stop",
            "key": GOOGLE_MAPS_API_KEY,
        }
        try:
            resp = requests.get(url, params=alt_params, timeout=5)
            data = resp.json() if resp.status_code == 200 else {}
        except Exception:
            data = {}
        results = data.get("results", [])

    safe_stops: List[SafeStopPlace] = []
    for r in results[:max_results]:
        loc = r.get("geometry", {}).get("location", {})
        place_id = r.get("place_id")
        maps_url = (
            f"https://www.google.com/maps/search/?api=1"
            f"&query={loc.get('lat')},{loc.get('lng')}"
        )
        if place_id:
            maps_url += f"&query_place_id={place_id}"

        safe_stops.append(
            SafeStopPlace(
                name=r.get("name", "Unknown"),
                lat=loc.get("lat", lat),
                lng=loc.get("lng", lng),
                address=r.get("vicinity"),
                place_id=place_id,
                type=(r.get("types", ["unknown"])[0] if r.get("types") else None),
                rating=r.get("rating"),
                user_ratings_total=r.get("user_ratings_total"),
                maps_url=maps_url,
            )
        )

    return safe_stops

def send_emergency_sms(user_id: str, score: int, event_id: str, timestamp: str):
    """
    Sends SMS to all registered emergency contacts for the given user.
    Respects a per-user cooldown to avoid spamming.
    """
    # 1. Check Twilio configuration
    if twilio_client is None or not TWILIO_FROM_NUMBER:
        return False, "Twilio not configured"

    contacts = emergency_contacts.get(user_id, [])
    if not contacts:
        return False, "No emergency contacts configured for this user"

    now = time.time()
    last = last_emergency_sms.get(user_id, 0)
    if now - last < EMERGENCY_COOLDOWN_SECONDS:
        return False, "Cooldown active, not sending duplicate SMS"

    # 2. Build message
    msg_body = (
        f"NeuroDrive ALERT: Critical driver fatigue detected for user '{user_id}' "
        f"at {timestamp}. Score: {score}. Event ID: {event_id}. "
        "Please contact the driver and ensure they stop driving safely."
    )

    # 3. Send SMS to each contact
    any_sent = False
    for contact in contacts:
        to_number = contact.get("phone_number")
        if not to_number:
            continue
        try:
            twilio_client.messages.create(
                body=msg_body,
                from_=TWILIO_FROM_NUMBER,
                to=to_number
            )
            any_sent = True
        except Exception as e:
            # For now we silently ignore individual failures; you can log them later
            continue

    if any_sent:
        last_emergency_sms[user_id] = now
        return True, "SMS sent"
    else:
        return False, "Failed to send to all contacts"

# --- AGENT INITIALIZATION ---
# Connect agents to global state stores (must be after function definitions)
fatigue_scoring_agent.set_user_profiles(user_profiles)
forecast_agent.set_driver_escalation_state(driver_escalation_state)
escalation_agent.set_driver_escalation_state(driver_escalation_state)
emergency_agent.set_emergency_sms_function(send_emergency_sms)
timeline_logging_agent.set_global_stores(fatigue_history, driver_timeline, alerts)

# In-memory store



@app.get("/")
def home():
    return {"message": "NeuroDrive backend running"}
from typing import List

@app.post("/calibrate/{user_id}")
def calibrate(
    user_id: str,
    open_ears: List[float],
    closed_ears: List[float],
    current_user: CurrentUser = Depends(get_current_user),  # can be optional while testing
):
    # Optionally assert that user_id == current_user.uid
    if current_user and current_user.uid != user_id:
        raise HTTPException(status_code=403, detail="user_id does not match authenticated user")

    open_avg = sum(open_ears) / len(open_ears)
    closed_avg = sum(closed_ears) / len(closed_ears)

    blink_low = closed_avg + 0.1 * (open_avg - closed_avg)
    blink_high = open_avg - 0.1 * (open_avg - closed_avg)

    profile = {
        "open_ear": open_avg,
        "closed_ear": closed_avg,
        "blink_low": blink_low,
        "blink_high": blink_high,
        "ema_open": open_avg,
        "ema_closed": closed_avg,
    }

    user_profiles[user_id] = profile

    # Persist to Firestore
    firebase_store.ensure_user_doc(user_id, email=current_user.email, name=current_user.name)
    firebase_store.save_calibration(user_id, profile)

    return {
        "message": "Calibration complete",
        "profile": profile,
    }

@app.post("/users/{user_id}/emergency-contacts")
def set_emergency_contacts(
    user_id: str,
    contacts: List[EmergencyContact],
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.uid != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    contacts_list = [c.dict() for c in contacts]

    # Update in-memory for SMS agent
    emergency_contacts[user_id] = contacts_list

    # Persist to Firestore
    firebase_store.ensure_user_doc(user_id, email=current_user.email, name=current_user.name)
    firebase_store.save_emergency_contacts(user_id, contacts_list)

    return {
        "user_id": user_id,
        "contacts": contacts_list,
    }



@app.get("/users/{user_id}/emergency-contacts")
def get_emergency_contacts(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.uid != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Prefer in-memory; if empty, try Firestore
    contacts = emergency_contacts.get(user_id)
    if contacts is None and db is not None:
        contacts = firebase_store.load_emergency_contacts(user_id)
        emergency_contacts[user_id] = contacts

    return {
        "user_id": user_id,
        "contacts": contacts or [],
    }


from logic import compute_fatigue_instant, compute_fatigue_personalized

@app.post("/predict")
def predict(data: DriverData):

    initial_state = {
        "user_id": data.user_id,
        "mode": data.mode,
        "eye_ratio": data.eye_ratio,
        "blink_count": data.blink_count,
        "head_tilt": data.head_tilt,
        "yawn_ratio": data.yawn_ratio
    }

    try:
        # ✅ Run the LangGraph workflow
        final_state = driver_workflow.invoke(initial_state)

        # ✅ BUILD FIRESTORE EVENT OBJECT
        event_record = {
            "user_id": final_state["user_id"],
            "timestamp": final_state.get("timestamp"),
            "mode": final_state["mode"],

            "fatigue_score": final_state["fatigue_score"],
            "status": final_state["status"],
            "escalation_level": final_state["escalation_level"],
            "safe_stop_needed": final_state["safe_stop_needed"],

            "event_id": final_state["event_id"],
            "event_type": final_state["event_type"],
            "tags": final_state["tags"],

            "eye_ratio": data.eye_ratio,
            "blink_count": data.blink_count,
            "head_tilt": data.head_tilt,
            "yawn_ratio": data.yawn_ratio,

            "forecast": final_state["forecast"],

            "sms_triggered": final_state["sms_triggered"],
            "sms_info": final_state["sms_info"]
        }

        # ✅ SAVE TO FIRESTORE (THIS WAS MISSING)
        if db is not None:
            print("✅ Saving prediction to Firestore")

            db.collection("users") \
              .document(data.user_id) \
              .collection("events") \
              .document(final_state["event_id"]) \
              .set(event_record)

            # also update escalation state
            db.collection("users") \
              .document(data.user_id) \
              .collection("state") \
              .document("escalation") \
              .set({
                  "level": final_state["escalation_level"],
                  "last_update": final_state.get("timestamp"),
                  "safe_stop_needed": final_state["safe_stop_needed"]
              })

            print("✅ Prediction stored in Firestore")

        else:
            print("❌ Firestore DB is None inside /predict")

        # ✅ RETURN RESPONSE TO CLIENT
        return {
            "fatigue_score": final_state["fatigue_score"],
            "status": final_state["status"],
            "intervention": final_state["intervention"],
            "escalation_level": final_state["escalation_level"],
            "safe_stop_needed": final_state["safe_stop_needed"],
            "mode": final_state["mode"],
            "event_id": final_state["event_id"],
            "event_type": final_state["event_type"],
            "tags": final_state["tags"],
            "forecast": final_state["forecast"],
            "sms_triggered": final_state["sms_triggered"],
            "sms_info": final_state["sms_info"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")


@app.post("/safe-stop")
def safe_stop(req: SafeStopRequest):
    """
    Safe-Stop Assistant:
    - Uses current escalation level & trend to decide if we should suggest a safe stop
    - Returns nearby safe pull-over places (parking / rest area)
    - Returns 'infotainment actions' (dim lights, reduce volume, etc.)
    - Logs a 'safe_stop_suggestion' event into the driver's timeline
    """
    # 1. Make sure we have escalation data for this user
    state = driver_escalation_state.get(req.user_id)
    if state is None or not state.get("recent_scores"):
        raise HTTPException(status_code=400, detail="No escalation data available for this user yet")

    level = state["level"]
    last_change = state.get("last_change", time.time())
    now_ts = time.time()

    # Persistency: has the driver been at level 3+ for > 60 seconds?
    persistent_high_fatigue = level >= 3 and (now_ts - last_change) > 60.0

    # We recommend safe stop for level 3 and 4
    safe_stop_recommended = level >= 3

    # 2. Find safe stops via Google Maps / dummy fallback
    safe_stops: List[SafeStopPlace] = []
    if safe_stop_recommended:
        safe_stops = find_safe_stops(
            lat=req.lat,
            lng=req.lng,
            max_distance_m=req.max_distance_m or 5000,
            max_results=5,
        )

    # 3. Decide infotainment actions
    # (Frontend / car system will implement these; backend just suggests)
    infotainment_actions = {
        "lower_media_volume_to": 0.3 if level >= 3 else 0.5,
        "ambient_light_mode": "calm_dim" if level >= 3 else "normal",
        "suppress_notifications": level >= 3,
        "voice_prompt": (
            "High fatigue detected. Please pull over at a safe location."
            if level >= 3 else
            "Monitoring driver state."
        ),
    }

    # 4. Log this as a timeline event
    last_score = state["recent_scores"][-1]
    event_id = str(uuid.uuid4())
    ts = datetime.now().isoformat()

    event_record = {
        "event_id": event_id,
        "timestamp": ts,
        "user_id": req.user_id,
        "mode": "unknown",
        "fatigue_score": last_score,
        "status": "alert" if level >= 3 else "normal",
        "event_type": "safe_stop_suggestion",
        "tags": [
            "safe_stop",
            f"escalation_level_{level}",
        ] + (["persistent_high_fatigue"] if persistent_high_fatigue else []),
        "eye_ratio": None,
        "blink_count": None,
        "head_tilt": None,
        "yawn_ratio": None,
        "has_snippet": False,
        "escalation_level": level,
        "intervention": "Safe-stop assistant invoked",
    }

    fatigue_history.append(event_record)
    if req.user_id not in driver_timeline:
        driver_timeline[req.user_id] = []
    driver_timeline[req.user_id].append(event_record)

    return {
        "user_id": req.user_id,
        "escalation_level": level,
        "persistent_high_fatigue": persistent_high_fatigue,
        "safe_stop_recommended": safe_stop_recommended,
        "safe_stops": [s.dict() for s in safe_stops],
        "infotainment_actions": infotainment_actions,
        "event_id": event_id,
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
    firebase_store.save_snippet_meta(snippet_meta)

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

    meta = firebase_store.get_snippet_meta_by_token(share_token)
    if meta:
        user_id = meta["user_id"]
        events = driver_timeline.get(user_id, [])
        event = next((e for e in events if e["event_id"] == meta["event_id"]), None)
        # If not in memory, you can also load from Firestore later
        return {
            "event": {
                "event_id": meta["event_id"],
                "timestamp": event["timestamp"] if event else meta["created_at"],
                "user_id": user_id,
                "mode": event["mode"] if event else "unknown",
                "fatigue_score": event["fatigue_score"] if event else None,
                "status": event["status"] if event else "alert",
                "event_type": event["event_type"] if event else "critical_fatigue",
                "tags": event["tags"] if event else [],
            },
            "snippet_available": True,
        }
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
