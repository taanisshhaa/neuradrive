# from fastapi import FastAPI
# from app.models import DriverData
# from app.logic import compute_fatigue_score

# app = FastAPI(title="NeuroDrive Backend")

# alerts = []  # temporary store

# @app.get("/")
# def home():
#     return {"message": "NeuroDrive backend running"}

# @app.post("/predict")
# def predict(data: DriverData):
#     score = compute_fatigue_score(data.eye_ratio, data.blink_count, data.head_tilt)
#     status = "alert" if score > 60 else "normal"
#     alerts.append({"score": score, "status": status})
#     return {"fatigue_score": score, "status": status}

# @app.get("/alerts")
# def get_alerts():
#     return alerts
from fastapi import FastAPI
from app.models import DriverData
from app.logic import compute_fatigue_score
from datetime import datetime

app = FastAPI(title="NeuroDrive Backend")

# In-memory store
alerts = []
fatigue_history = []

@app.get("/")
def home():
    return {"message": "NeuroDrive backend running"}

# ---------- CORE PREDICTION ----------
@app.post("/predict")
def predict(data: DriverData):
    score = compute_fatigue_score(data.eye_ratio, data.blink_count, data.head_tilt)
    status = "alert" if score > 60 else "normal"

    record = {
        "timestamp": datetime.now().isoformat(),
        "eye_ratio": data.eye_ratio,
        "blink_count": data.blink_count,
        "head_tilt": data.head_tilt,
        "fatigue_score": score,
        "status": status
    }

    fatigue_history.append(record)
    alerts.append({"score": score, "status": status})

    # Simple intervention suggestion
    if score > 80:
        intervention = "⚠️ Trigger loud alert or seat vibration"
    elif score > 60:
        intervention = "💡 Change ambient lighting or play soft cue"
    else:
        intervention = "✅ Driver normal"

    return {"fatigue_score": score, "status": status, "intervention": intervention}

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
