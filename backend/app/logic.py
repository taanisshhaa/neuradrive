
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
    """Very simple EMA-based forecast for the next few minutes.
    Returns a list of predicted fatigue scores for the next `steps` intervals.
    """
    if not recent_scores:
        return [0.0] * steps
    # Exponential moving average as state
    alpha = 0.4
    ema = float(recent_scores[0])
    for s in recent_scores[1:]:
        ema = alpha * s + (1 - alpha) * ema
    # Assume mean-reverting slight drift towards latest value
    predictions: list[float] = []
    current = ema
    for _ in range(steps):
        current = alpha * ema + (1 - alpha) * current
        predictions.append(round(max(0.0, min(100.0, current)), 2))
    return predictions
