# ===================================================
# FILE: anti_cheat/ai_detector.py
# ===================================================

def cheating_risk(tab_switches, fast_answers, skips):

    risk_score = 0

    # ------------------------------
    # Tab Switching Behaviour
    # ------------------------------

    if tab_switches > 0:
        risk_score += tab_switches * 15


    # ------------------------------
    # Extremely Fast Answers
    # ------------------------------

    if fast_answers > 2:
        risk_score += fast_answers * 6


    # ------------------------------
    # Question Skipping Pattern
    # ------------------------------

    if skips > 2:
        risk_score += skips * 4


    # ------------------------------
    # Behaviour Combination
    # ------------------------------

    if tab_switches > 2 and fast_answers > 3:
        risk_score += 15


    if skips > 4:
        risk_score += 10


    # ------------------------------
    # Clamp Score
    # ------------------------------

    if risk_score > 100:
        risk_score = 100


    # ------------------------------
    # Risk Levels
    # ------------------------------

    if risk_score >= 70:
        level = "HIGH"

    elif risk_score >= 40:
        level = "MEDIUM"

    else:
        level = "LOW"


    return {
        "risk_score": risk_score,
        "risk_level": level
    }