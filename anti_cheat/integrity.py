# ============================================================
# FILE: anti_cheat/integrity.py
# ============================================================

def calculate_integrity(
    tab_switches,
    exam_time,
    total_questions,
    attempts,
    fast_answers=0,
    skips=0
):

    score = 100

    # -----------------------------
    # Tab Switching Penalty
    # -----------------------------

    score -= tab_switches * 8


    # -----------------------------
    # Suspicious Fast Answers
    # -----------------------------

    if fast_answers > 2:
        score -= fast_answers * 4


    # -----------------------------
    # Skipped Questions
    # -----------------------------

    if skips > 3:
        score -= skips * 3


    # -----------------------------
    # Attempt History
    # -----------------------------

    if attempts > 1:
        score -= (attempts - 1) * 5


    # -----------------------------
    # Average Time Analysis
    # -----------------------------

    avg_time = exam_time / total_questions

    if avg_time < 5:
        score -= 10


    # -----------------------------
    # Clamp Score
    # -----------------------------

    if score < 0:
        score = 0

    if score > 100:
        score = 100


    return score


# ============================================================
# Integrity Status
# ============================================================

def integrity_status(score):

    if score >= 85:
        return "SAFE"

    elif score >= 65:
        return "SUSPICIOUS"

    else:
        return "HIGH RISK"