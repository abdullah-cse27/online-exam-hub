# ===================================================
# FILE: anti_cheat/ai_detector.py (STABLE VERSION)
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
    Hybrid cheating risk analysis system.
    Combines:
    - Real-time AI proctoring (Vision)
    - Behavioral analytics (Interaction)
    - Temporal analytics (Time)
    """

    # ===================================================
    # 1. SAFE DATA EXTRACTION (PROCTORING DATA)
    # ===================================================
    if isinstance(data, dict):
        faces = data.get("faces", 1)
        looking = data.get("looking", True)
        motion = data.get("motion", False)
        objects = data.get("objects", [])
        low_light = data.get("low_light", False)
    else:
        # Defaults if proctoring data is missing
        faces = 1 
        looking = True
        motion = False
        objects = []
        low_light = False

    # ===================================================
    # 2. NORMALIZE INPUTS
    # ===================================================
    tab_switches = int(tab_switches or 0)
    fast_answers = int(fast_answers or 0)
    skips = int(skips or 0)
    camera_warnings = int(camera_warnings or 0)
    suspicious_motion = int(suspicious_motion or 0)

    risk_score = 0
    warning = ""

    # ===================================================
    # 3. VISION-BASED RISK (FACIAL ANALYSIS)
    # ===================================================
    if faces == 0:
        risk_score += 45
        warning = "⚠ Face not visible"
    elif faces > 1:
        risk_score += 75  # High penalty for multiple people
        warning = "⚠ Multiple faces detected"

    if not looking and faces > 0:
        risk_score += 20
        warning = "⚠ Please look at the screen"

    if low_light:
        risk_score += 5 
        warning = "⚠ Lighting is low"

    # ===================================================
    # 4. OBJECT DETECTION RISK (YOLO)
    # ===================================================
    if objects:
        if "cell phone" in objects:
            risk_score += 65  # Critical offense
            warning = "⚠ Mobile Phone detected"
        elif any(obj in ["book", "laptop", "tablet"] for obj in objects):
            risk_score += 50
            warning = f"⚠ Forbidden object: {objects[0]}"
        else:
            risk_score += 30
            warning = "⚠ Suspicious object detected"

    # ===================================================
    # 5. BEHAVIORAL RISK (INTERACTION)
    # ===================================================
    # Tab Switching: Each switch adds penalty
    if tab_switches > 0:
        risk_score += (tab_switches * 15)
        if tab_switches > 2:
            risk_score += 25  # Bulk penalty for repeated switching
            warning = "⚠ Frequent tab switching"

    # Fast Answers: Guessing or copy-paste behavior
    if fast_answers > 2:
        risk_score += (fast_answers * 5)

    # Suspicious Motion
    if suspicious_motion > 0:
        risk_score += 10

    # ===================================================
    # 6. TIME-BASED RISK (ANOMALY DETECTION)
    # ===================================================
    if exam_duration is not None and expected_duration is not None:
        # If student finishes in less than 25% of the time
        if exam_duration < (expected_duration * 0.25):
            risk_score += 30
            warning = "⚠ Exam completed unnaturally fast"

    # ===================================================
    # 7. FINAL RISK EVALUATION
    # ===================================================
    # Caps risk at 100%
    risk_score = min(risk_score, 100)

    if risk_score >= 80:
        level = "CRITICAL"
    elif risk_score >= 50:
        level = "HIGH"
    elif risk_score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "warning": warning or "Monitoring Active",
        "faces": faces,
        "status": "Cheating Detected" if risk_score > 70 else "Normal"
    }