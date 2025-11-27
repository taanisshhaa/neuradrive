
import time

# keep short-term memory of how long eyes stay closed
_last_closed_time = 0.0
_closed_duration = 0.0
_prev_open = True
def compute_fatigue_instant(
    eye_ratio: float,
    blink_count: int,
    head_tilt: float,
    yawn_ratio: float | None
):
    score = 0

    # Generic EAR thresholds (no calibration)
    if eye_ratio < 0.22:
        score += 40
    elif eye_ratio < 0.25:
        score += 25

    if blink_count > 6:
        score += 15 + 2 * (blink_count - 6)

    if abs(head_tilt) > 12:
        score += 15 + int(abs(head_tilt) / 2)

    if yawn_ratio and yawn_ratio > 0.6:
        score += 15

    return min(score, 100)

def compute_fatigue_personalized(
    user_profile: dict,
    eye_ratio: float,
    blink_count: int,
    head_tilt: float,
    yawn_ratio: float | None
):
    OPEN_EAR = user_profile["ema_open"]
    CLOSED_EAR = user_profile["ema_closed"]

    span = OPEN_EAR - CLOSED_EAR
    eye_ratio = max(min(eye_ratio, OPEN_EAR), CLOSED_EAR)

    # EWMA online adaptation
    alpha = 0.02
    user_profile["ema_open"] = (1 - alpha) * OPEN_EAR + alpha * eye_ratio
    user_profile["ema_closed"] = (1 - alpha) * CLOSED_EAR + alpha * eye_ratio

    eye_closure = (OPEN_EAR - eye_ratio) / span

    score = int(eye_closure * 70)

    if blink_count > 5:
        score += 10 + 2 * (blink_count - 5)

    if abs(head_tilt) > 10:
        score += 10 + int(abs(head_tilt) / 2)

    if yawn_ratio and yawn_ratio > 0.6:
        score += 15

    return min(score, 100)



def forecast_next_scores(recent_scores: list[int], steps: int = 5) -> list[float]:
    """
    EMA forecast biased toward current value to capture sudden fatigue spikes.
    """
    if not recent_scores:
        return [0.0] * steps

    alpha = 0.5
    current = float(recent_scores[-1])  # MOST RECENT SCORE
    ema = current

    # Backward smoothing
    for s in reversed(recent_scores[:-1]):
        ema = alpha * s + (1 - alpha) * ema

    predictions = []
    for _ in range(steps):
        ema = 0.7 * current + 0.3 * ema   # Bias toward current spike
        predictions.append(round(max(0.0, min(100.0, ema)), 2))

    return predictions

def decide_escalation(level: int, score: int, forecast: list[float]):
    """
    Correct priority-based adaptive escalation:
    - Highest risk is checked first
    - Allows instant jump to critical levels
    """
    predicted_risk = max(forecast) if forecast else score

    # 🔴 EMERGENCY — immediate jump
    if score >= 90 or predicted_risk >= 90:
        return 4

    # 🟠 CRITICAL — pull over immediately
    if score >= 80 or predicted_risk >= 80:
        return 3

    # 🟡 HIGH — vibration
    if score >= 65 or predicted_risk >= 70:
        return 2

    # 🔵 MODERATE — gentle alert
    if score >= 50 or predicted_risk >= 60:
        return 1

    # 🟢 SAFE — reset
    return 0



def escalation_action(level: int):
    """
    Maps escalation level to physical/logical action.
    """
    if level == 0:
        return "✅ Normal monitoring"
    elif level == 1:
        return "🔊 Gentle audio alert"
    elif level == 2:
        return "📳 Trigger vibration"
    elif level == 3:
        return "🚨 Strong alert + instruct to pull over"
    elif level == 4:
        return "📞 Notify emergency contact"
