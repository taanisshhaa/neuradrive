# firebase_store.py

from typing import List, Dict, Any
from datetime import datetime

from google.cloud.firestore_v1.base_query import FieldFilter

from models import EmergencyContact, SnippetMeta  # adjust import if needed

db = None  # will be set from main.py

def init_firestore(firestore_client):
    global db
    db = firestore_client


def ensure_user_doc(uid: str, email: str | None = None, name: str | None = None):
    if db is None:
        return
    user_ref = db.collection("users").document(uid)
    user_ref.set(
        {
            "email": email,
            "name": name,
            "updated_at": datetime.utcnow().isoformat()
        },
        merge=True,
    )


def save_calibration(uid: str, profile: dict):
    if db is None:
        return
    calib_ref = (
        db.collection("users")
        .document(uid)
        .collection("calibration")
        .document("ear_profile")
    )
    calib_ref.set(profile)


def load_calibration(uid: str) -> dict | None:
    if db is None:
        return None
    doc = (
        db.collection("users")
        .document(uid)
        .collection("calibration")
        .document("ear_profile")
        .get()
    )
    if doc.exists:
        return doc.to_dict()
    return None


def save_emergency_contacts(uid: str, contacts: List[dict]):
    if db is None:
        return
    col_ref = db.collection("users").document(uid).collection("emergency_contacts")

    # Overwrite: delete existing, then add new
    # (for simplicity, you can later optimize)
    for doc in col_ref.stream():
        doc.reference.delete()

    for c in contacts:
        col_ref.add(c)


def load_emergency_contacts(uid: str) -> List[dict]:
    if db is None:
        return []
    col_ref = db.collection("users").document(uid).collection("emergency_contacts")
    return [doc.to_dict() for doc in col_ref.stream()]


def save_escalation_state(uid: str, state: dict):
    if db is None:
        return
    state_ref = db.collection("users").document(uid).collection("state").document("escalation")
    state_ref.set(state)


def load_escalation_state(uid: str) -> dict | None:
    if db is None:
        return None
    doc = db.collection("users").document(uid).collection("state").document("escalation").get()
    if doc.exists:
        return doc.to_dict()
    return None


def save_event(uid: str, event: dict):
    if db is None:
        return
    ev_ref = db.collection("users").document(uid).collection("events").document(event["event_id"])
    ev_ref.set(event)


def load_events(uid: str, limit: int = 50) -> List[dict]:
    if db is None:
        return []
    col = (
        db.collection("users")
        .document(uid)
        .collection("events")
        .order_by("timestamp", direction="DESCENDING")
        .limit(limit)
    )
    return [doc.to_dict() for doc in col.stream()]


def save_snippet_meta(meta: dict):
    if db is None:
        return
    uid = meta["user_id"]
    event_id = meta["event_id"]
    ref = db.collection("users").document(uid).collection("snippets").document(event_id)
    ref.set(meta)


def get_snippet_meta_by_token(share_token: str) -> dict | None:
    if db is None:
        return None
    # Search in all users' snippets by share_token
    # Not super efficient but fine for hackathon scale
    coll_group = db.collection_group("snippets")
    q = coll_group.where(filter=FieldFilter("share_token", "==", share_token))
    for doc in q.stream():
        data = doc.to_dict()
        return data
    return None
