# ============================================================
# FILE: anti_cheat/integrity.py
# ============================================================

def calculate_integrity(
    tab_switches,
    exam_time,
    total_questions,
    attempts,
    fast_answers=0,
    skips=0,
    camera_warnings=0,
    suspicious_motion=0
):

    """
    Calculate integrity score for an exam attempt.
    Higher score = more trustworthy behaviour.
    """

    # =============================================
    # SAFETY CONVERSION
    # =============================================

    tab_switches = int(tab_switches or 0)
    exam_time = float(exam_time or 0)
    total_questions = int(total_questions or 1)
    attempts = int(attempts or 1)
    fast_answers = int(fast_answers or 0)
    skips = int(skips or 0)
    camera_warnings = int(camera_warnings or 0)
    suspicious_motion = int(suspicious_motion or 0)

    score = 100


    # =============================================
    # TAB SWITCH PENALTY
    # =============================================

    if tab_switches > 0:
        score -= tab_switches * 8

    if tab_switches > 3:
        score -= 10


    # =============================================
    # FAST ANSWERS
    # =============================================

    if fast_answers > 2:
        score -= fast_answers * 4

    if fast_answers > 5:
        score -= 10


    # =============================================
    # SKIPPED QUESTIONS
    # =============================================

    if skips > 3:
        score -= skips * 3

    if skips > 6:
        score -= 8


    # =============================================
    # CAMERA WARNINGS
    # =============================================

    if camera_warnings > 0:
        score -= camera_warnings * 6


    # =============================================
    # SUSPICIOUS MOTION
    # =============================================

    if suspicious_motion > 0:
        score -= suspicious_motion * 5


    # =============================================
    # ATTEMPT HISTORY
    # =============================================

    if attempts > 1:
        score -= (attempts - 1) * 5

    if attempts > 3:
        score -= 10


    # =============================================
    # AVERAGE TIME ANALYSIS
    # =============================================

    if total_questions > 0:

        avg_time = exam_time / total_questions

        if avg_time < 5:
            score -= 10

        elif avg_time < 10:
            score -= 5


    # =============================================
    # EXTREMELY SHORT EXAM
    # =============================================

    if exam_time < (total_questions * 5):
        score -= 10


    # =============================================
    # CLAMP SCORE
    # =============================================

    score = max(0, min(score, 100))


    return score


# ============================================================
# INTEGRITY STATUS
# ============================================================

def integrity_status(score):

    """
    Convert integrity score into readable risk level.
    """

    if score >= 85:
        return "SAFE"

    elif score >= 65:
        return "SUSPICIOUS"

    else:
        return "HIGH RISK"