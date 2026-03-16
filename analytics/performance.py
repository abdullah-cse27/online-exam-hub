# ===================================================
# FILE: analytics/performance.py
# ===================================================

# This file contains analytics logic for student results


# ===================================================
# STUDENT SUMMARY
# ===================================================

def get_student_summary(results, student_id):

    student_results = [r for r in results if r[0] == student_id]

    if not student_results:
        return None

    scores = []
    subjects = set()

    for r in student_results:

        score = int(r[2])
        total = int(r[3])

        percent = (score / total) * 100

        scores.append(percent)
        subjects.add(r[1])

    return {
        "total_exams": len(student_results),
        "average_score": round(sum(scores) / len(scores), 2),
        "best_score": round(max(scores), 2),
        "subjects": list(subjects)
    }


# ===================================================
# WEAK SUBJECT DETECTION
# ===================================================

def detect_weak_subjects(results, student_id):

    student_results = [r for r in results if r[0] == student_id]

    weak = []

    for r in student_results:

        subject = r[1]
        percent = float(r[4])

        if percent < 60:
            weak.append(subject)

    return list(set(weak))


# ===================================================
# RECOMMENDATIONS
# ===================================================

def generate_recommendations(results, student_id):

    weak = detect_weak_subjects(results, student_id)

    rec = []

    if not weak:

        rec.append("Great performance! Keep practicing regularly.")

    else:

        for w in weak:

            rec.append(f"Practice more questions in {w}")

    return rec