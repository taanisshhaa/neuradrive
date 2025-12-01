from typing import TypedDict, Optional, List


class DriverState(TypedDict, total=False):
    """
    Shared state that flows through all agents in the LangGraph workflow.
    Each agent reads from and writes to this state.
    """
    # Input data (from API request)
    user_id: str
    mode: str  # "instant" or "personalized"
    eye_ratio: float
    blink_count: int
    head_tilt: float
    yawn_ratio: Optional[float]
    
    # Generated metadata
    event_id: str
    timestamp: str
    
    # Computed by fatigue_scoring_agent
    fatigue_score: int
    status: str  # "normal" or "alert"
    
    # Computed by forecast_agent
    forecast: List[float]
    
    # Computed by escalation_agent
    escalation_level: int
    old_escalation_level: int  # For detecting level transitions
    
    # Computed by intervention_agent
    intervention: str
    event_type: str
    tags: List[str]
    
    # Computed by safe_stop_agent
    safe_stop_needed: bool
    
    # Computed by emergency_agent
    sms_triggered: bool
    sms_info: Optional[str]
