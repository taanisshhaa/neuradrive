from pydantic import BaseModel
from typing import Optional

class DriverData(BaseModel):
    eye_ratio: float
    blink_count: int
    head_tilt: float
    yawn_ratio: Optional[float] = None
    sustained_closed: Optional[bool] = False  # eyes closed >3 seconds
