"""
Timeline Logging Agent - Records event to timeline and history
"""
from agent_state import DriverState
import firebase_store

# References to global stores from main.py
fatigue_history = None
driver_timeline = None
alerts = None


def set_global_stores(history, timeline, alerts_list):
    """Set references to global stores from main.py"""
    global fatigue_history, driver_timeline, alerts
    fatigue_history = history
    driver_timeline = timeline
    alerts = alerts_list


def timeline_logging_agent(state: DriverState) -> DriverState:
    """
    Records the event to all relevant histories and timelines.
    Final agent in the workflow.
    
    Args:
        state: Complete state with all computed values
        
    Returns:
        Final state (unchanged, just logs to stores)
    """
    user_id = state["user_id"]
    
    # Build event record from state
    event_record = {
        "event_id": state["event_id"],
        "timestamp": state["timestamp"],
        "user_id": user_id,
        "mode": state["mode"],
        "fatigue_score": state["fatigue_score"],
        "status": state["status"],
        "event_type": state["event_type"],
        "tags": state["tags"],
        "eye_ratio": state["eye_ratio"],
        "blink_count": state["blink_count"],
        "head_tilt": state["head_tilt"],
        "yawn_ratio": state.get("yawn_ratio"),
        "has_snippet": False,
        "escalation_level": state["escalation_level"],
        "intervention": state["intervention"]
    }
    
    # Append to global histories
    if fatigue_history is not None:
        fatigue_history.append(event_record)
    
    if driver_timeline is not None:
        if user_id not in driver_timeline:
            driver_timeline[user_id] = []
        driver_timeline[user_id].append(event_record)
    
    # Legacy alerts list
    if alerts is not None:
        alerts.append({
            "score": state["fatigue_score"],
            "status": state["status"]
        })
    firebase_store.save_event(user_id, event_record)
    return state
