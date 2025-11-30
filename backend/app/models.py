from pydantic import BaseModel
from typing import Optional, List

class DriverData(BaseModel):
    user_id: str                     # track driver
    mode: str                        # "instant" or "personalized"
    eye_ratio: float
    blink_count: int
    head_tilt: float
    yawn_ratio: Optional[float] = None


class TimelineEvent(BaseModel):
    event_id: str
    timestamp: str
    user_id: str
    mode: str
    fatigue_score: int
    status: str          # "normal" / "alert"
    event_type: str      # e.g. "normal", "fatigue_warning", "critical_fatigue"
    tags: List[str]      # e.g. ["yawn", "high_blink_rate"]
    eye_ratio: Optional[float] = None
    blink_count: Optional[int] = None
    head_tilt: Optional[float] = None
    yawn_ratio: Optional[float] = None
    has_snippet: bool = False


class SnippetMeta(BaseModel):
    event_id: str
    user_id: str
    created_at: str
    file_name: str
    duration_seconds: Optional[float] = None
    share_token: Optional[str] = None

class EmergencyContact(BaseModel):
    phone_number: str         # E.164 format recommended: +91xxxxxxxxxx
    name: Optional[str] = None

class SafeStopRequest(BaseModel):
    user_id: str
    lat: float
    lng: float
    max_distance_m: Optional[int] = 5000   # search radius, default 5km


class SafeStopPlace(BaseModel):
    name: str
    lat: float
    lng: float
    address: Optional[str] = None
    place_id: Optional[str] = None
    type: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    maps_url: Optional[str] = None
