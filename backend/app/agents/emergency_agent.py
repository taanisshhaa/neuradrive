"""
Emergency Agent - Triggers emergency SMS at level 4
"""
from agent_state import DriverState


# Reference to send_emergency_sms function from main.py
send_emergency_sms_func = None


def set_emergency_sms_function(func):
    """Set reference to send_emergency_sms from main.py"""
    global send_emergency_sms_func
    send_emergency_sms_func = func


def emergency_agent(state: DriverState) -> DriverState:
    """
    Triggers emergency SMS when escalation level reaches 4.
    
    Args:
        state: State with user_id, escalation_level, old_escalation_level,
               fatigue_score, event_id, and timestamp
        
    Returns:
        Updated state with sms_triggered and sms_info
    """
    level = state["escalation_level"]
    old_level = state["old_escalation_level"]
    
    # Trigger SMS if we just entered level 4
    sms_triggered = False
    sms_message = None
    
    if level == 4 and old_level < 4:
        if send_emergency_sms_func is not None:
            sms_triggered, sms_message = send_emergency_sms_func(
                user_id=state["user_id"],
                score=state["fatigue_score"],
                event_id=state["event_id"],
                timestamp=state["timestamp"]
            )
        else:
            # Fallback if function not available
            sms_triggered = False
            sms_message = "SMS function not configured"
    
    # Update state
    state["sms_triggered"] = sms_triggered
    state["sms_info"] = sms_message
    
    return state
