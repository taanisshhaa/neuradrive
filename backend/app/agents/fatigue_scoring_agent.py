"""
Fatigue Scoring Agent - Computes fatigue score based on mode
"""
from agent_state import DriverState
from logic import compute_fatigue_instant, compute_fatigue_personalized


# Reference to user_profiles from main.py (will be imported)
user_profiles = None


def set_user_profiles(profiles):
    """Set reference to user_profiles from main.py"""
    global user_profiles
    user_profiles = profiles


def fatigue_scoring_agent(state: DriverState) -> DriverState:
    """
    Computes fatigue score using instant or personalized mode.
    
    Args:
        state: State with mode and sensor readings
        
    Returns:
        Updated state with fatigue_score and status
    """
    mode = state["mode"]
    eye_ratio = state["eye_ratio"]
    blink_count = state["blink_count"]
    head_tilt = state["head_tilt"]
    yawn_ratio = state.get("yawn_ratio")
    
    if mode == "instant":
        score = compute_fatigue_instant(
            eye_ratio=eye_ratio,
            blink_count=blink_count,
            head_tilt=head_tilt,
            yawn_ratio=yawn_ratio
        )
    elif mode == "personalized":
        user_id = state["user_id"]
        
        # Check if user is calibrated
        if user_profiles is None or user_id not in user_profiles:
            raise ValueError(f"User {user_id} not calibrated. Please calibrate first.")
        
        score = compute_fatigue_personalized(
            user_profile=user_profiles[user_id],
            eye_ratio=eye_ratio,
            blink_count=blink_count,
            head_tilt=head_tilt,
            yawn_ratio=yawn_ratio
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")
    
    # Determine status
    status = "alert" if score > 60 else "normal"
    
    # Update state
    state["fatigue_score"] = score
    state["status"] = status
    
    return state
