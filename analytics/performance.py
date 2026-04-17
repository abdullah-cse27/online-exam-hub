# ===================================================
# FILE: analytics/performance.py (INTEGRITY INCLUDED)
# ===================================================

# ===================================================
# STUDENT SUMMARY
# ===================================================

def get_student_summary(results, student_id):
    student_results = [r for r in results if str(r[0]) == str(student_id)]

    if not student_results:
        return None

    scores = []
    risks = [] # Tracking Integrity
    subjects = set()

    for r in student_results:
        try:
            # Index 2: Score, Index 3: Total
            score = int(r[2])
            total = int(r[3])
            percent = (score / total) * 100
            scores.append(percent)
            
            subjects.add(r[1])
            
            # Risk detection (Index 7 is cheat_risk in our new format)
            if len(r) >= 8:
                risks.append(float(r[7]))
        except:
            continue

    if not scores:
        return None

    return {
        "total_exams": len(scores),
        "average_score": round(sum(scores) / len(scores), 2),
        "best_score": round(max(scores), 2),
        "worst_score": round(min(scores), 2),
        "average_risk": round(sum(risks) / len(risks), 2) if risks else 0,
        "subjects": list(subjects)
    }


# ===================================================
# SUBJECT PERFORMANCE
# ===================================================

def subject_performance(results, student_id):
    student_results = [r for r in results if str(r[0]) == str(student_id)]
    subject_scores = {}

    for r in student_results:
        subject = r[1]
        try:
            # Index 4 is percentage
            percent = float(r[4])
        except:
            continue

        if subject not in subject_scores:
            subject_scores[subject] = []
        subject_scores[subject].append(percent)

    summary = {}
    for s in subject_scores:
        avg = sum(subject_scores[s]) / len(subject_scores[s])
        summary[s] = round(avg, 2)

    return summary


# ===================================================
# WEAK SUBJECT DETECTION
# ===================================================

def detect_weak_subjects(results, student_id):
    perf = subject_performance(results, student_id)
    weak = []
    for subject, score in perf.items():
        if score < 60:
            weak.append(subject)
    return weak


# ===================================================
# IMPROVEMENT TREND
# ===================================================

def detect_improvement(results, student_id):
    student_results = [r for r in results if str(r[0]) == str(student_id)]
    
    if len(student_results) < 2:
        return "New Student"

    scores = []
    for r in student_results:
        try:
            scores.append(float(r[4]))
        except:
            continue

    if len(scores) < 2:
        return "Initial Stage"

    if scores[-1] > scores[-2]:
        return "Improving 📈"
    elif scores[-1] < scores[-2]:
        return "Performance dropped ⚠"
    else:
        return "Stable"


# ===================================================
# RECOMMENDATIONS
# ===================================================

def generate_recommendations(results, student_id):
    summary = get_student_summary(results, student_id)
    weak = detect_weak_subjects(results, student_id)
    rec = []

    if not weak:
        rec.append("🌟 Excellent Academic Standing! Keep it up.")
    else:
        for w in weak:
            rec.append(f"Focus on {w}: Review basic concepts and retake mock tests.")

    # Risk-based recommendation
    if summary and summary["average_risk"] > 50:
        rec.append("❗ Warning: Maintain better integrity during exams to avoid disqualification.")
    
    trend = detect_improvement(results, student_id)
    rec.append(f"Trend Analysis: {trend}")
    
    return rec


# ===================================================
# TOP STUDENTS
# ===================================================

def get_top_students(results, limit=10):
    scores = {}
    for r in results:
        student = str(r[0])
        try:
            percent = float(r[4])
        except:
            continue

        if student not in scores:
            scores[student] = []
        scores[student].append(percent)

    avg_scores = []
    for student in scores:
        avg = sum(scores[student]) / len(scores[student])
        avg_scores.append((student, round(avg, 2)))

    avg_scores.sort(key=lambda x: x[1], reverse=True)
    return avg_scores[:limit]