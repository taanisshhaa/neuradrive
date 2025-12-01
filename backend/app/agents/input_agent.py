"""
Input Agent - Validates and normalizes input data
First agent in the workflow pipeline
"""
from datetime import datetime
import uuid
from agent_state import DriverState


def input_agent(state: DriverState) -> DriverState:
    """
    Validates input data and initializes the state.
    
    Args:
        state: Initial state with user_id, mode, and sensor readings
        
    Returns:
        Updated state with event_id, timestamp, and validated inputs
    """
    # Generate unique event ID and timestamp
    state["event_id"] = str(uuid.uuid4())
    state["timestamp"] = datetime.now().isoformat()
    
    # Validate required fields (basic validation)
    if not state.get("user_id"):
        raise ValueError("user_id is required")
    
    if state.get("mode") not in ["instant", "personalized"]:
        raise ValueError("mode must be 'instant' or 'personalized'")
    
    # Ensure numeric fields are present
    if state.get("eye_ratio") is None:
        raise ValueError("eye_ratio is required")
    
    if state.get("blink_count") is None:
        raise ValueError("blink_count is required")
    
    if state.get("head_tilt") is None:
        raise ValueError("head_tilt is required")
    
    # yawn_ratio is optional, so we don't validate it
    
    return state
