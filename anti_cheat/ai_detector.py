# ===================================================
# FILE: anti_cheat/ai_detector.py
# ===================================================

def cheating_risk(
    tab_switches=0,
    fast_answers=0,
    skips=0,
    camera_warnings=0,
    suspicious_motion=0,
    exam_duration=None,
    expected_duration=None
):

    """
    Advanced cheating risk analysis.
    """

    # ================================
    # SAFETY NORMALIZATION
    # ================================

    tab_switches = int(tab_switches or 0)
    fast_answers = int(fast_answers or 0)
    skips = int(skips or 0)
    camera_warnings = int(camera_warnings or 0)
    suspicious_motion = int(suspicious_motion or 0)

    risk_score = 0


    # ================================
    # TAB SWITCHING
    # ================================

    if tab_switches > 0:
        risk_score += tab_switches * 12

    if tab_switches > 3:
        risk_score += 15


    # ================================
    # FAST ANSWERS
    # ================================

    if fast_answers > 2:
        risk_score += fast_answers * 6

    if fast_answers > 5:
        risk_score += 10


    # ================================
    # SKIP PATTERN
    # ================================

    if skips > 2:
        risk_score += skips * 4

    if skips > 5:
        risk_score += 10


    # ================================
    # CAMERA WARNINGS
    # ================================

    if camera_warnings > 0:
        risk_score += camera_warnings * 10


    # ================================
    # SUSPICIOUS MOTION
    # ================================

    if suspicious_motion > 0:
        risk_score += suspicious_motion * 8


    # ================================
    # EXAM TIME ANALYSIS
    # ================================

    if exam_duration and expected_duration:

        if exam_duration < expected_duration * 0.4:
            risk_score += 15


    # ================================
    # BEHAVIOUR COMBINATIONS
    # ================================

    if tab_switches > 2 and fast_answers > 3:
        risk_score += 15

    if tab_switches > 1 and skips > 3:
        risk_score += 10

    if fast_answers > 4 and skips > 4:
        risk_score += 8


    # ================================
    # SCORE LIMIT
    # ================================

    risk_score = min(risk_score, 100)


    # ================================
    # RISK LEVEL
    # ================================

    if risk_score >= 70:
        level = "HIGH"

    elif risk_score >= 40:
        level = "MEDIUM"

    else:
        level = "LOW"


    # ================================
    # RETURN RESULT
    # ================================

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "tab_switches": tab_switches,
        "fast_answers": fast_answers,
        "skips": skips,
        "camera_warnings": camera_warnings,
        "suspicious_motion": suspicious_motion
    }