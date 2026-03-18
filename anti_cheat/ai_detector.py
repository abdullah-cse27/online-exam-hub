# ===================================================
# FILE: anti_cheat/ai_detector.py (AI CHEATING ANALYZER)
# ===================================================

def cheating_risk(data=None,
                  tab_switches=0,
                  fast_answers=0,
                  skips=0,
                  camera_warnings=0,
                  suspicious_motion=0,
                  exam_duration=None,
                  expected_duration=None):

    """
    Hybrid cheating risk analysis
    Supports:
    - AI proctoring data
    - Exam behaviour analytics
    """

    # ===================================================
    # SAFE DATA EXTRACTION
    # ===================================================

    if isinstance(data, dict):

        faces = data.get("faces", 0)
        looking = data.get("looking", True)
        motion = data.get("motion", False)
        objects = data.get("objects", [])
        low_light = data.get("low_light", False)

    else:
        faces = 0
        looking = True
        motion = False
        objects = []
        low_light = False


    # ===================================================
    # NORMALIZE VALUES
    # ===================================================

    tab_switches = int(tab_switches or 0)
    fast_answers = int(fast_answers or 0)
    skips = int(skips or 0)
    camera_warnings = int(camera_warnings or 0)
    suspicious_motion = int(suspicious_motion or 0)

    risk_score = 0
    warning = ""


    # ===================================================
    # CAMERA ANALYSIS
    # ===================================================

    if faces == 0:
        risk_score += 40
        warning = "⚠ Face not visible"

    elif faces > 1:
        risk_score += 60
        warning = "⚠ Multiple faces detected"


    if not looking:
        risk_score += 20
        warning = "⚠ Look at the screen"


    if motion:
        risk_score += 15


    if low_light:
        risk_score += 10
        warning = "⚠ Low lighting"


    if len(objects) > 0:

        if "cell phone" in objects:
            risk_score += 50
            warning = "⚠ Phone detected"

        else:
            risk_score += 40
            warning = f"⚠ Suspicious object: {objects[0]}"


    # ===================================================
    # TAB SWITCHING
    # ===================================================

    if tab_switches > 0:
        risk_score += tab_switches * 12

    if tab_switches > 3:
        risk_score += 15


    # ===================================================
    # FAST ANSWERS
    # ===================================================

    if fast_answers > 2:
        risk_score += fast_answers * 6

    if fast_answers > 5:
        risk_score += 10


    # ===================================================
    # SKIP PATTERN
    # ===================================================

    if skips > 2:
        risk_score += skips * 4

    if skips > 5:
        risk_score += 10


    # ===================================================
    # CAMERA WARNINGS
    # ===================================================

    if camera_warnings > 0:
        risk_score += camera_warnings * 10


    # ===================================================
    # SUSPICIOUS MOTION
    # ===================================================

    if suspicious_motion > 0:
        risk_score += suspicious_motion * 8


    # ===================================================
    # EXAM TIME ANALYSIS
    # ===================================================

    if exam_duration and expected_duration:

        if exam_duration < expected_duration * 0.4:
            risk_score += 15


    # ===================================================
    # BEHAVIOUR COMBINATIONS
    # ===================================================

    if tab_switches > 2 and fast_answers > 3:
        risk_score += 15

    if tab_switches > 1 and skips > 3:
        risk_score += 10

    if fast_answers > 4 and skips > 4:
        risk_score += 8


    # ===================================================
    # LIMIT SCORE
    # ===================================================

    risk_score = min(risk_score, 100)


    # ===================================================
    # RISK LEVEL
    # ===================================================

    if risk_score >= 70:
        level = "HIGH"

    elif risk_score >= 40:
        level = "MEDIUM"

    else:
        level = "LOW"


    # ===================================================
    # RETURN RESULT
    # ===================================================

    result = {
        "risk_score": risk_score,
        "risk_level": level,
        "warning": warning,
        "faces": faces
    }

    return result