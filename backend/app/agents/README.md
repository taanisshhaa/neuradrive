# NeuroDrive Agents

This directory contains the 8 specialized agents that form the LangGraph workflow for driver fatigue detection.

## Agent Pipeline

The agents process driver data in the following sequence:

```
Input → Fatigue Scoring → Forecast → Escalation → Intervention → Safe-Stop → Emergency → Timeline Logging
```

## Agent Descriptions

### 1. Input Agent (`input_agent.py`)
**Purpose**: Validates and normalizes input data  
**Inputs**: Raw driver data (user_id, mode, sensor readings)  
**Outputs**: Validated state with event_id and timestamp  
**Key Functions**:
- Validates required fields
- Generates unique event ID
- Initializes workflow state

### 2. Fatigue Scoring Agent (`fatigue_scoring_agent.py`)
**Purpose**: Computes fatigue score  
**Inputs**: Validated driver data  
**Outputs**: Fatigue score (0-100) and status  
**Key Functions**:
- Calls `compute_fatigue_instant()` or `compute_fatigue_personalized()`
- Checks user calibration for personalized mode
- Determines alert status (score > 60)

### 3. Forecast Agent (`forecast_agent.py`)
**Purpose**: Predicts future fatigue trend  
**Inputs**: Current fatigue score  
**Outputs**: 5-step forecast array  
**Key Functions**:
- Maintains rolling window of last 10 scores
- Uses EMA-based forecasting
- Updates driver escalation state

### 4. Escalation Agent (`escalation_agent.py`)
**Purpose**: Determines escalation level (0-4)  
**Inputs**: Current score and forecast  
**Outputs**: Escalation level and old level  
**Key Functions**:
- Calls `decide_escalation()` logic
- Implements recovery logic (score < 45 → level 0)
- Tracks level transitions for SMS triggering

### 5. Intervention Agent (`intervention_agent.py`)
**Purpose**: Maps escalation to intervention action  
**Inputs**: Escalation level and sensor data  
**Outputs**: Intervention message, event type, and tags  
**Key Functions**:
- Maps level to action (0=monitor, 1=audio, 2=vibration, 3=pull over, 4=SMS)
- Derives event type (normal, fatigue_warning, critical_fatigue)
- Builds tags based on sensor readings

### 6. Safe-Stop Agent (`safe_stop_agent.py`)
**Purpose**: Sets safe-stop recommendation flag  
**Inputs**: Escalation level  
**Outputs**: safe_stop_needed boolean  
**Key Functions**:
- Sets flag for level ≥ 3
- Note: Actual location finding is in `/safe-stop` endpoint

### 7. Emergency Agent (`emergency_agent.py`)
**Purpose**: Triggers emergency SMS at level 4  
**Inputs**: Escalation level and transition info  
**Outputs**: SMS trigger status  
**Key Functions**:
- Detects level 4 transitions (old < 4 → new = 4)
- Calls `send_emergency_sms()` function
- Respects cooldown period

### 8. Timeline Logging Agent (`timeline_logging_agent.py`)
**Purpose**: Records event to all history stores  
**Inputs**: Complete state with all computed values  
**Outputs**: Final state (unchanged)  
**Key Functions**:
- Builds event record from state
- Appends to fatigue_history, driver_timeline, and alerts
- Final agent in pipeline

## State Flow

Each agent receives a `DriverState` dict and returns an updated version:

```python
DriverState = {
    # Input (from API)
    "user_id": str,
    "mode": str,
    "eye_ratio": float,
    "blink_count": int,
    "head_tilt": float,
    "yawn_ratio": Optional[float],
    
    # Generated (Input Agent)
    "event_id": str,
    "timestamp": str,
    
    # Computed (Fatigue Scoring Agent)
    "fatigue_score": int,
    "status": str,
    
    # Computed (Forecast Agent)
    "forecast": List[float],
    
    # Computed (Escalation Agent)
    "escalation_level": int,
    "old_escalation_level": int,
    
    # Computed (Intervention Agent)
    "intervention": str,
    "event_type": str,
    "tags": List[str],
    
    # Computed (Safe-Stop Agent)
    "safe_stop_needed": bool,
    
    # Computed (Emergency Agent)
    "sms_triggered": bool,
    "sms_info": Optional[str]
}
```

## Agent Initialization

Agents are connected to global state stores in `main.py`:

```python
# After function definitions
fatigue_scoring_agent.set_user_profiles(user_profiles)
forecast_agent.set_driver_escalation_state(driver_escalation_state)
escalation_agent.set_driver_escalation_state(driver_escalation_state)
emergency_agent.set_emergency_sms_function(send_emergency_sms)
timeline_logging_agent.set_global_stores(fatigue_history, driver_timeline, alerts)
```

## Testing

Run the workflow test:

```bash
python test_workflow.py
```

This will test:
- All agent imports
- Low fatigue scenario
- High fatigue scenario
- Timeline logging

## Adding New Agents

To add a new agent:

1. Create `agents/new_agent.py`
2. Define agent function: `def new_agent(state: DriverState) -> DriverState:`
3. Add node to workflow in `workflow.py`:
   ```python
   workflow.add_node("new_agent", new_agent)
   workflow.add_edge("previous_agent", "new_agent")
   workflow.add_edge("new_agent", "next_agent")
   ```
4. Update `DriverState` in `agent_state.py` if needed
5. Initialize agent in `main.py` if it needs global state access
