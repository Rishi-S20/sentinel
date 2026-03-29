"""Anomaly detector — compares belief states and fires alerts on significant changes."""

from app.models.belief import BeliefState


# How much conviction must shift to trigger an alert
CONVICTION_DELTA_THRESHOLD = 0.2


def detect_anomaly(previous: BeliefState | None, new_belief: dict) -> dict | None:
    """
    Compare previous belief to the new one.
    Returns an alert dict if a significant change is detected, else None.
    """
    if previous is None:
        # First run — no prior belief to compare against
        return None

    delta = new_belief["conviction"] - previous.conviction

    if abs(delta) < CONVICTION_DELTA_THRESHOLD:
        return None

    direction = "bullish" if delta > 0 else "bearish"
    severity = "high" if abs(delta) >= 0.4 else "medium"

    return {
        "alert_type": "conviction_shift",
        "severity": severity,
        "message": (
            f"Conviction shifted {direction} by {abs(delta):.2f} "
            f"({previous.conviction:.2f} → {new_belief['conviction']:.2f}). "
            f"New thesis: {new_belief['thesis']}"
        ),
        "delta": delta,
    }
