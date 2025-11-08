# def compute_fatigue_score(eye_ratio: float, blink_count: int, head_tilt: float):
#     """
#     Compute a simple fatigue score (0–100) based on facial parameters.
#     """
#     score = 0

#     # Eye aspect ratio (EAR): smaller = eyes closing
#     if eye_ratio < 0.22:
#         score += 50
#     elif eye_ratio < 0.25:
#         score += 30

#     # Blink frequency: high blink rate may indicate fatigue
#     if blink_count > 20:
#         score += 20

#     # Head tilt (degrees): driver looking down or away
#     if abs(head_tilt) > 15:
#         score += 30

#     # Cap the score at 100
#     return min(score, 100)
# app/logic.py
import time

# keep short-term memory of how long eyes stay closed
_last_closed_time = 0.0
_closed_duration = 0.0
_prev_open = True

def compute_fatigue_score(eye_ratio: float, blink_count: int, head_tilt: float, yawn_ratio: float | None = None):
    """
    Compute a 0–100 fatigue score that adapts to the user’s typical EAR range.
    """

    global _last_closed_time, _closed_duration, _prev_open

    # --- 1. learn simple moving baseline ---
    # these numbers are meant to roughly match what you saw on screen
    OPEN_EAR = 0.30     # average EAR when eyes open for you
    CLOSED_EAR = 0.24   # average EAR when eyes closed for you
    range_span = OPEN_EAR - CLOSED_EAR
    eye_ratio = max(min(eye_ratio, OPEN_EAR), CLOSED_EAR)  # clamp

    # map EAR to [0, 1] where 1 = fully closed
    eye_closure = (OPEN_EAR - eye_ratio) / range_span

    # --- 2. track sustained closure duration ---
    now = time.time()
    if eye_ratio < CLOSED_EAR + 0.02:          # eyes are essentially closed
        if _prev_open:
            _last_closed_time = now
        _closed_duration = now - _last_closed_time
        _prev_open = False
    else:
        _closed_duration = 0.0
        _prev_open = True

    # --- 3. scoring ---
    score = 0

    # eye closure contribution
    score += int(eye_closure * 70)             # 0-70 points based on closure

    # sustained closure (micro-sleep)
    if _closed_duration > 1.5:                 # closed for >1.5 s
        score += 30

    # blinking frequency
    if blink_count > 5:
        score += 10 + 2 * (blink_count - 5)

    # head tilt
    if abs(head_tilt) > 10:
        score += 10 + int(abs(head_tilt) / 2)

    # yawn contribution
    if yawn_ratio is not None and yawn_ratio > 0.6:
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
