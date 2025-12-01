"""
Quick test script to verify the LangGraph workflow works correctly
"""
import sys
import os
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
print("Testing imports...")
try:
    from agent_state import DriverState
    print("✓ agent_state imported")
    
    from agents.input_agent import input_agent
    print("✓ input_agent imported")
    
    from agents.fatigue_scoring_agent import fatigue_scoring_agent
    print("✓ fatigue_scoring_agent imported")
    
    from agents.forecast_agent import forecast_agent
    print("✓ forecast_agent imported")
    
    from agents.escalation_agent import escalation_agent
    print("✓ escalation_agent imported")
    
    from agents.intervention_agent import intervention_agent
    print("✓ intervention_agent imported")
    
    from agents.safe_stop_agent import safe_stop_agent
    print("✓ safe_stop_agent imported")
    
    from agents.emergency_agent import emergency_agent
    print("✓ emergency_agent imported")
    
    from agents.timeline_logging_agent import timeline_logging_agent
    print("✓ timeline_logging_agent imported")
    
    from workflow import driver_workflow
    print("✓ workflow imported")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test workflow with sample data
print("\n" + "="*50)
print("Testing workflow with sample data...")
print("="*50)

# Initialize global stores for testing
from agents import fatigue_scoring_agent, forecast_agent, escalation_agent
from agents import emergency_agent, timeline_logging_agent

user_profiles = {}
driver_escalation_state = {}
fatigue_history = []
driver_timeline = {}
alerts = []

def mock_send_emergency_sms(user_id, score, event_id, timestamp):
    print(f"  [MOCK SMS] Would send SMS for user {user_id}, score {score}")
    return False, "Mock SMS (not configured)"

# Set up agent references
fatigue_scoring_agent.set_user_profiles(user_profiles)
forecast_agent.set_driver_escalation_state(driver_escalation_state)
escalation_agent.set_driver_escalation_state(driver_escalation_state)
emergency_agent.set_emergency_sms_function(mock_send_emergency_sms)
timeline_logging_agent.set_global_stores(fatigue_history, driver_timeline, alerts)

# Test 1: Instant mode with low fatigue
print("\nTest 1: Instant mode - Low fatigue")
test_state_1 = {
    "user_id": "test_user_1",
    "mode": "instant",
    "eye_ratio": 0.30,
    "blink_count": 3,
    "head_tilt": 2.0,
    "yawn_ratio": 0.2
}

try:
    result_1 = driver_workflow.invoke(test_state_1)
    print(f"  ✓ Fatigue Score: {result_1['fatigue_score']}")
    print(f"  ✓ Status: {result_1['status']}")
    print(f"  ✓ Escalation Level: {result_1['escalation_level']}")
    print(f"  ✓ Intervention: {result_1['intervention']}")
    print(f"  ✓ Event ID: {result_1['event_id']}")
except Exception as e:
    print(f"  ❌ Test 1 failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Instant mode with high fatigue
print("\nTest 2: Instant mode - High fatigue")
test_state_2 = {
    "user_id": "test_user_2",
    "mode": "instant",
    "eye_ratio": 0.18,
    "blink_count": 12,
    "head_tilt": 18.0,
    "yawn_ratio": 0.7
}

try:
    result_2 = driver_workflow.invoke(test_state_2)
    print(f"  ✓ Fatigue Score: {result_2['fatigue_score']}")
    print(f"  ✓ Status: {result_2['status']}")
    print(f"  ✓ Escalation Level: {result_2['escalation_level']}")
    print(f"  ✓ Intervention: {result_2['intervention']}")
    print(f"  ✓ Safe Stop Needed: {result_2['safe_stop_needed']}")
    print(f"  ✓ Tags: {result_2['tags']}")
except Exception as e:
    print(f"  ❌ Test 2 failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check timeline logging
print("\nTest 3: Timeline logging verification")
print(f"  ✓ Fatigue history entries: {len(fatigue_history)}")
print(f"  ✓ Driver timeline users: {list(driver_timeline.keys())}")
print(f"  ✓ Alerts count: {len(alerts)}")

print("\n" + "="*50)
print("✅ All tests completed!")
print("="*50)
