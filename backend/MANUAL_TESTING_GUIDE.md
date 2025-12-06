# Manual Testing Guide - NeuroDrive Agentic Backend

This guide will walk you through manually testing the entire backend and verifying the agentic workflow.

## Prerequisites

Make sure you have all dependencies installed:

```bash
cd backend/app
pip install -r requirements.txt
```

---

## Method 1: Using the Automated Test Script (Recommended)

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd backend/app
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### Step 2: Run the Test Script

Open a **new terminal** (keep the server running) and run:

```bash
cd backend/app
python test_api.py
```

This will automatically test all 13 endpoints and show you:
- Health check
- User calibration
- Emergency contacts
- Predictions (low, medium, high fatigue)
- Personalized mode
- Escalation states
- Timeline logging
- Safe-stop recommendations
- Performance metrics

**Expected Output**: All tests should show ✅ Success

---

## Method 2: Using FastAPI Interactive Docs (Visual Testing)

### Step 1: Start the Server

```bash
cd backend/app
uvicorn main:app --reload
```

### Step 2: Open the Interactive API Docs

Open your browser and go to:
```
http://127.0.0.1:8000/docs
```

You'll see the **Swagger UI** with all endpoints listed.

### Step 3: Test Each Endpoint Manually

#### Test 1: Health Check

1. Click on `GET /` 
2. Click "Try it out"
3. Click "Execute"
4. **Expected Response**:
   ```json
   {
     "message": "NeuroDrive backend running"
   }
   ```

#### Test 2: Calibrate a User

1. Click on `POST /calibrate/{user_id}`
2. Click "Try it out"
3. Enter `test_user_1` as user_id
4. Use this request body:
   ```json
   {
     "open_ears": [0.30, 0.31, 0.29, 0.30, 0.32],
     "closed_ears": [0.18, 0.19, 0.17, 0.18, 0.20]
   }
   ```
5. Click "Execute"
6. **Expected Response**: Profile with open_ear, closed_ear, blink thresholds

#### Test 3: Set Emergency Contacts

1. Click on `POST /users/{user_id}/emergency-contacts`
2. Click "Try it out"
3. Enter `test_user_1` as user_id
4. Use this request body:
   ```json
   [
     {
       "phone_number": "+919876543210",
       "name": "Emergency Contact 1"
     }
   ]
   ```
5. Click "Execute"
6. **Expected Response**: Confirmation with contacts list

#### Test 4: Predict - Low Fatigue (Instant Mode)

1. Click on `POST /predict`
2. Click "Try it out"
3. Use this request body:
   ```json
   {
     "user_id": "test_user_instant",
     "mode": "instant",
     "eye_ratio": 0.30,
     "blink_count": 3,
     "head_tilt": 2.0,
     "yawn_ratio": 0.2
   }
   ```
4. Click "Execute"
5. **Expected Response**:
   ```json
   {
     "fatigue_score": 0,
     "status": "normal",
     "escalation_level": 0,
     "intervention": "✅ Normal monitoring",
     "safe_stop_needed": false,
     "event_id": "...",
     "event_type": "normal",
     "tags": [],
     "forecast": [0.0, 0.0, 0.0, 0.0, 0.0],
     "sms_triggered": false
   }
   ```

**🔍 Agent Flow Verification**: This request goes through all 8 agents:
- Input Agent validates data
- Fatigue Scoring Agent computes score = 0
- Forecast Agent predicts [0, 0, 0, 0, 0]
- Escalation Agent sets level = 0
- Intervention Agent maps to "Normal monitoring"
- Safe-Stop Agent sets flag = false
- Emergency Agent checks for SMS (none needed)
- Timeline Logging Agent records the event

#### Test 5: Predict - High Fatigue (Instant Mode)

1. Click on `POST /predict`
2. Click "Try it out"
3. Use this request body:
   ```json
   {
     "user_id": "test_user_instant",
     "mode": "instant",
     "eye_ratio": 0.18,
     "blink_count": 12,
     "head_tilt": 18.0,
     "yawn_ratio": 0.7
   }
   ```
4. Click "Execute"
5. **Expected Response**:
   ```json
   {
     "fatigue_score": 100,
     "status": "alert",
     "escalation_level": 4,
     "intervention": "📞 Notify emergency contact",
     "safe_stop_needed": true,
     "event_type": "critical_fatigue",
     "tags": ["critical_fatigue", "yawn", "high_blink_rate", "head_tilt"],
     "sms_triggered": false
   }
   ```

**🔍 Agent Flow Verification**: 
- Fatigue Scoring Agent computes score = 100
- Forecast Agent predicts high values
- Escalation Agent jumps to level = 4 (emergency)
- Intervention Agent maps to "Notify emergency contact"
- Safe-Stop Agent sets flag = true
- Emergency Agent would trigger SMS (if Twilio configured)

#### Test 6: Predict - Personalized Mode

1. Click on `POST /predict`
2. Click "Try it out"
3. Use this request body:
   ```json
   {
     "user_id": "test_user_1",
     "mode": "personalized",
     "eye_ratio": 0.25,
     "blink_count": 6,
     "head_tilt": 5.0,
     "yawn_ratio": 0.3
   }
   ```
4. Click "Execute"
5. **Expected Response**: Score based on calibrated profile

**🔍 Agent Flow Verification**:
- Fatigue Scoring Agent uses personalized profile
- Computes score relative to user's calibrated EAR values

#### Test 7: Get Timeline Events

1. Click on `GET /timeline/{user_id}`
2. Click "Try it out"
3. Enter `test_user_instant` as user_id
4. Click "Execute"
5. **Expected Response**: Array of events you just created

**🔍 Verify**: Timeline Logging Agent recorded all events

#### Test 8: Get Escalation State

1. Click on `GET /escalation/{user_id}`
2. Click "Try it out"
3. Enter `test_user_instant` as user_id
4. Click "Execute"
5. **Expected Response**:
   ```json
   {
     "level": 4,
     "last_change": 1234567890.123,
     "recent_scores": [0, 100]
   }
   ```

**🔍 Verify**: Escalation Agent maintained state correctly

#### Test 9: Safe-Stop Recommendations

1. Click on `POST /safe-stop`
2. Click "Try it out"
3. Use this request body:
   ```json
   {
     "user_id": "test_user_instant",
     "lat": 28.6139,
     "lng": 77.2090,
     "max_distance_m": 5000
   }
   ```
4. Click "Execute"
5. **Expected Response**: List of safe stops (demo data if no Google Maps API key)

#### Test 10: Dashboard Summary

1. Click on `GET /summary`
2. Click "Try it out"
3. Click "Execute"
4. **Expected Response**: Statistics from all predictions

---

## Method 3: Using cURL Commands (Command Line)

### Start the Server First

```bash
cd backend/app
uvicorn main:app --reload
```

### Test Commands

#### 1. Health Check
```bash
curl http://127.0.0.1:8000/
```

#### 2. Calibrate User
```bash
curl -X POST "http://127.0.0.1:8000/calibrate/test_user_1" \
  -H "Content-Type: application/json" \
  -d "{\"open_ears\": [0.30, 0.31, 0.29], \"closed_ears\": [0.18, 0.19, 0.17]}"
```

#### 3. Predict (Low Fatigue)
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"test_user\", \"mode\": \"instant\", \"eye_ratio\": 0.30, \"blink_count\": 3, \"head_tilt\": 2.0, \"yawn_ratio\": 0.2}"
```

#### 4. Predict (High Fatigue)
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"test_user\", \"mode\": \"instant\", \"eye_ratio\": 0.18, \"blink_count\": 12, \"head_tilt\": 18.0, \"yawn_ratio\": 0.7}"
```

#### 5. Get Timeline
```bash
curl http://127.0.0.1:8000/timeline/test_user
```

---

## Method 4: Using Postman (GUI Tool)

### Setup

1. Download Postman: https://www.postman.com/downloads/
2. Create a new collection called "NeuroDrive"
3. Set base URL: `http://127.0.0.1:8000`

### Create Requests

#### Request 1: Health Check
- Method: GET
- URL: `{{base_url}}/`

#### Request 2: Calibrate
- Method: POST
- URL: `{{base_url}}/calibrate/test_user_1`
- Body (JSON):
  ```json
  {
    "open_ears": [0.30, 0.31, 0.29, 0.30, 0.32],
    "closed_ears": [0.18, 0.19, 0.17, 0.18, 0.20]
  }
  ```

#### Request 3: Predict Low Fatigue
- Method: POST
- URL: `{{base_url}}/predict`
- Body (JSON):
  ```json
  {
    "user_id": "test_user_instant",
    "mode": "instant",
    "eye_ratio": 0.30,
    "blink_count": 3,
    "head_tilt": 2.0,
    "yawn_ratio": 0.2
  }
  ```

#### Request 4: Predict High Fatigue
- Method: POST
- URL: `{{base_url}}/predict`
- Body (JSON):
  ```json
  {
    "user_id": "test_user_instant",
    "mode": "instant",
    "eye_ratio": 0.18,
    "blink_count": 12,
    "head_tilt": 18.0,
    "yawn_ratio": 0.7
  }
  ```

---

## Method 5: Testing with Camera Module

### Step 1: Start Backend Server

```bash
cd backend/app
uvicorn main:app --reload
```

### Step 2: Run Camera Module

Open a **new terminal**:

```bash
cd backend
python camera_module.py
```

### What Happens

1. Camera calibration (eyes open for 5s, eyes closed for 5s)
2. Real-time detection starts
3. Every 3 seconds, camera sends data to `/predict` endpoint
4. **Agentic workflow processes the data**:
   - Input Agent validates
   - Fatigue Scoring Agent computes score
   - Forecast Agent predicts trend
   - Escalation Agent determines level
   - Intervention Agent maps action
   - Safe-Stop Agent sets flag
   - Emergency Agent checks for SMS
   - Timeline Logging Agent records event
5. Response displayed in terminal
6. Visual feedback on camera window

### Expected Console Output

```
🧠 Fatigue: {
  'fatigue_score': 25,
  'status': 'normal',
  'intervention': '✅ Normal monitoring',
  'escalation_level': 0,
  'safe_stop_needed': False,
  ...
}
```

---

## Verifying the Agentic Workflow

### How to Confirm All 8 Agents Are Working

#### 1. Check Server Logs

When you make a `/predict` request, the workflow executes silently. To see agent execution, you can add debug logging.

#### 2. Verify State Changes

Make multiple predictions and check:

```bash
# Get escalation state
curl http://127.0.0.1:8000/escalation/test_user_instant
```

You should see:
- `level` changing based on fatigue scores
- `recent_scores` array updating (max 10 scores)

#### 3. Verify Timeline Logging

```bash
# Get timeline
curl http://127.0.0.1:8000/timeline/test_user_instant
```

Each event should have:
- `event_id` (from Input Agent)
- `fatigue_score` (from Fatigue Scoring Agent)
- `escalation_level` (from Escalation Agent)
- `intervention` (from Intervention Agent)
- `tags` (from Intervention Agent)

#### 4. Test Escalation Progression

Send predictions with increasing fatigue:

1. **Low**: eye_ratio=0.30, blink=3 → Level 0
2. **Medium**: eye_ratio=0.23, blink=8 → Level 1-2
3. **High**: eye_ratio=0.18, blink=12 → Level 3-4

Watch the escalation level increase!

#### 5. Verify Forecast Agent

Make 3-4 predictions, then check the forecast in the response. It should predict future scores based on the trend.

---

## Expected Results Summary

| Test | Expected Outcome |
|------|-----------------|
| Health Check | "NeuroDrive backend running" |
| Calibration | Profile created with EAR thresholds |
| Low Fatigue | Score: 0-30, Level: 0, Status: normal |
| Medium Fatigue | Score: 40-60, Level: 1-2, Status: normal/alert |
| High Fatigue | Score: 80-100, Level: 3-4, Status: alert, Safe-stop: true |
| Personalized Mode | Score based on user's calibrated profile |
| Timeline | All events logged with complete metadata |
| Escalation State | Level and recent scores tracked |
| Safe-Stop | Locations returned (demo or real) |

---

## Troubleshooting

### Server Won't Start

**Error**: `Address already in use`

**Solution**:
```bash
# Windows
Get-Process python | Where-Object {$_.MainWindowTitle -like '*uvicorn*'} | Stop-Process -Force

# Then restart
uvicorn main:app --reload
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'langgraph'`

**Solution**:
```bash
cd backend/app
pip install -r requirements.txt
```

### User Not Calibrated Error

**Error**: `User not calibrated`

**Solution**: Call `/calibrate/{user_id}` endpoint first before using personalized mode.

---

## Quick Test Checklist

- [ ] Server starts without errors
- [ ] Health check returns 200 OK
- [ ] Calibration creates user profile
- [ ] Low fatigue prediction returns level 0
- [ ] High fatigue prediction returns level 4
- [ ] Personalized mode works with calibrated user
- [ ] Timeline shows all events
- [ ] Escalation state tracks correctly
- [ ] Safe-stop returns locations
- [ ] Camera module integrates successfully

---

## Next Steps

After manual testing:

1. ✅ Verify all endpoints work
2. ✅ Confirm agentic workflow executes
3. ✅ Test with camera module
4. Ready to integrate with frontend!

---

**Happy Testing! 🚀**

For automated testing, just run: `python test_api.py`
