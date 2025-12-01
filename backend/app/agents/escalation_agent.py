"""
Escalation Agent - Determines escalation level (0-4)
"""
from datetime import datetime
from agent_state import DriverState
from logic import decide_escalation


# Reference to driver_escalation_state from main.py
driver_escalation_state = None


def set_driver_escalation_state(state_dict):
    """Set reference to driver_escalation_state from main.py"""
    global driver_escalation_state
    driver_escalation_state = state_dict


def escalation_agent(state: DriverState) -> DriverState:
    """
    Decides escalation level based on current score and forecast.
    
    Args:
        state: State with user_id, fatigue_score, and forecast
        
    Returns:
        Updated state with escalation_level and old_escalation_level
    """
    user_id = state["user_id"]
    score = state["fatigue_score"]
    forecast = state["forecast"]
    
    if driver_escalation_state is None:
        # Fallback: just use score to determine level
        if score >= 90:
            new_level = 4
        elif score >= 80:
            new_level = 3
        elif score >= 65:
            new_level = 2
        elif score >= 50:
            new_level = 1
        else:
            new_level = 0
        old_level = 0
    else:
        # Get current escalation state
        if user_id not in driver_escalation_state:
            driver_escalation_state[user_id] = {
                "level": 0,
                "last_change": datetime.now().timestamp(),
                "recent_scores": []
            }
        
        user_state = driver_escalation_state[user_id]
        old_level = user_state["level"]
        
        # Decide next escalation level
        new_level = decide_escalation(
            level=old_level,
            score=score,
            forecast=forecast
        )
        
        # Reset escalation if driver recovers
        if score < 45:
            new_level = 0
        
        # Update state if level changed
        if new_level != old_level:
            user_state["level"] = new_level
            user_state["last_change"] = datetime.now().timestamp()
        else:
            user_state["level"] = new_level
    
    # Update state
    state["escalation_level"] = new_level
    state["old_escalation_level"] = old_level
    
    return state
