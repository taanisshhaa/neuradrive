"""
Forecast Agent - Predicts future fatigue trend
"""
from agent_state import DriverState
from logic import forecast_next_scores


# Reference to driver_escalation_state from main.py
driver_escalation_state = None


def set_driver_escalation_state(state_dict):
    """Set reference to driver_escalation_state from main.py"""
    global driver_escalation_state
    driver_escalation_state = state_dict


def forecast_agent(state: DriverState) -> DriverState:
    """
    Maintains rolling window of scores and forecasts future trend.
    
    Args:
        state: State with user_id and fatigue_score
        
    Returns:
        Updated state with forecast array
    """
    user_id = state["user_id"]
    score = state["fatigue_score"]
    
    # Initialize user escalation state if needed
    if driver_escalation_state is not None:
        if user_id not in driver_escalation_state:
            driver_escalation_state[user_id] = {
                "level": 0,
                "last_change": 0.0,
                "recent_scores": []
            }
        
        # Maintain rolling window of last 10 scores
        driver_escalation_state[user_id]["recent_scores"].append(score)
        driver_escalation_state[user_id]["recent_scores"] = \
            driver_escalation_state[user_id]["recent_scores"][-10:]
        
        # Predict future trend using EMA forecast
        recent_scores = driver_escalation_state[user_id]["recent_scores"]
        forecast = forecast_next_scores(recent_scores, steps=5)
    else:
        # Fallback if state not available
        forecast = forecast_next_scores([score], steps=5)
    
    # Update state
    state["forecast"] = forecast
    
    return state
