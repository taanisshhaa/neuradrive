"""
LangGraph Workflow - Orchestrates the 8-agent pipeline
"""
from langgraph.graph import StateGraph, END
from agent_state import DriverState

# Import all agent functions
from agents.input_agent import input_agent
from agents.fatigue_scoring_agent import fatigue_scoring_agent
from agents.forecast_agent import forecast_agent
from agents.escalation_agent import escalation_agent
from agents.intervention_agent import intervention_agent
from agents.safe_stop_agent import safe_stop_agent
from agents.emergency_agent import emergency_agent
from agents.timeline_logging_agent import timeline_logging_agent


def create_workflow():
    """
    Creates and compiles the LangGraph workflow.
    
    Returns:
        Compiled StateGraph ready for invocation
    """
    # Create the graph
    workflow = StateGraph(DriverState)
    
    # Add all agent nodes
    workflow.add_node("input_agent", input_agent)
    workflow.add_node("fatigue_scoring_agent", fatigue_scoring_agent)
    workflow.add_node("forecast_agent", forecast_agent)
    workflow.add_node("escalation_agent", escalation_agent)
    workflow.add_node("intervention_agent", intervention_agent)
    workflow.add_node("safe_stop_agent", safe_stop_agent)
    workflow.add_node("emergency_agent", emergency_agent)
    workflow.add_node("timeline_logging_agent", timeline_logging_agent)
    
    # Define sequential edges (linear pipeline)
    workflow.add_edge("input_agent", "fatigue_scoring_agent")
    workflow.add_edge("fatigue_scoring_agent", "forecast_agent")
    workflow.add_edge("forecast_agent", "escalation_agent")
    workflow.add_edge("escalation_agent", "intervention_agent")
    workflow.add_edge("intervention_agent", "safe_stop_agent")
    workflow.add_edge("safe_stop_agent", "emergency_agent")
    workflow.add_edge("emergency_agent", "timeline_logging_agent")
    workflow.add_edge("timeline_logging_agent", END)
    
    # Set entry point
    workflow.set_entry_point("input_agent")
    
    # Compile the workflow
    app = workflow.compile()
    
    return app


# Create the compiled workflow (singleton)
driver_workflow = create_workflow()
