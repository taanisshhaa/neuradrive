"""
Intervention Agent - Maps escalation level to intervention action
"""
from agent_state import DriverState
from logic import escalation_action


def intervention_agent(state: DriverState) -> DriverState:
    """
    Determines intervention action and derives event metadata.
    
    Args:
        state: State with escalation_level, fatigue_score, and sensor data
        
    Returns:
        Updated state with intervention, event_type, and tags
    """
    level = state["escalation_level"]
    score = state["fatigue_score"]
    
    # Get physical/system action
    intervention = escalation_action(level)
    
    # Derive event_type based on score
    if score > 80:
        event_type = "critical_fatigue"
    elif score > 60:
        event_type = "fatigue_warning"
    else:
        event_type = "normal"
    
    # Build tags based on event type and sensor readings
    tags = []
    
    if event_type != "normal":
        tags.append(event_type)
    
    # Add sensor-specific tags
    yawn_ratio = state.get("yawn_ratio")
    if yawn_ratio is not None and yawn_ratio > 0.6:
        tags.append("yawn")
    
    if state["blink_count"] > 10:
        tags.append("high_blink_rate")
    
    if abs(state["head_tilt"]) > 15:
        tags.append("head_tilt")
    
    # Update state
    state["intervention"] = intervention
    state["event_type"] = event_type
    state["tags"] = tags
    
    return state
