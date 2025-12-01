"""
Safe-Stop Agent - Prepares safe-stop recommendations
"""
from agent_state import DriverState


def safe_stop_agent(state: DriverState) -> DriverState:
    """
    Determines if safe-stop is needed based on escalation level.
    
    Note: This agent only sets the flag. Actual location finding
    is handled by the /safe-stop endpoint.
    
    Args:
        state: State with escalation_level
        
    Returns:
        Updated state with safe_stop_needed flag
    """
    level = state["escalation_level"]
    
    # Safe stop recommended for level 3 and 4
    safe_stop_needed = level >= 3
    
    # Update state
    state["safe_stop_needed"] = safe_stop_needed
    
    return state
