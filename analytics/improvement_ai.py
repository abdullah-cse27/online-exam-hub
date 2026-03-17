# ===================================================
# FILE: analytics/improvement_ai.py
# ===================================================

# AI based improvement suggestions for students


# ===================================================
# PERFORMANCE LEVEL
# ===================================================

def performance_level(percent):

    if percent >= 90:
        return "Excellent"

    elif percent >= 75:
        return "Good"

    elif percent >= 60:
        return "Average"

    else:
        return "Needs Improvement"


# ===================================================
# WEAK SUBJECTS
# ===================================================

def get_weak_subjects(results, student_id):

    weak_subjects = []

    for r in results:

        if r[0] != student_id:
            continue

        try:
            percent = float(r[4])
        except:
            continue

        if percent < 60:
            weak_subjects.append(r[1])

    return list(set(weak_subjects))


# ===================================================
# STRONG SUBJECTS
# ===================================================

def get_strong_subjects(results, student_id):

    strong = []

    for r in results:

        if r[0] != student_id:
            continue

        try:
            percent = float(r[4])
        except:
            continue

        if percent >= 80:
            strong.append(r[1])

    return list(set(strong))


# ===================================================
# STUDY PLAN GENERATOR
# ===================================================

def improvement_plan(results, student_id):

    weak_subjects = get_weak_subjects(results, student_id)

    strong_subjects = get_strong_subjects(results, student_id)

    suggestions = []

    if not weak_subjects:

        suggestions.append(
            "Great performance! Try advanced coding problems to improve further."
        )

    else:

        for sub in weak_subjects:

            suggestions.append(
                f"Practice more MCQ questions in {sub}"
            )

            suggestions.append(
                f"Solve coding challenges related to {sub}"
            )

            suggestions.append(
                f"Review important concepts of {sub} in Learning Mode"
            )

    if strong_subjects:

        suggestions.append(
            f"Your strong subjects: {', '.join(strong_subjects)}"
        )

        suggestions.append(
            "Try harder quizzes to maintain your performance."
        )

    return suggestions


# ===================================================
# TOPIC RECOMMENDATION (FOR LEARNING MODE)
# ===================================================

def recommend_topics(subject):

    topics = {

        "Python": [
            "Loops",
            "Functions",
            "Lists",
            "Dictionaries",
            "Recursion"
        ],

        "C": [
            "Pointers",
            "Arrays",
            "Structures",
            "Functions",
            "Memory Management"
        ],

        "DSA": [
            "Stacks",
            "Queues",
            "Linked Lists",
            "Trees",
            "Sorting Algorithms"
        ]
    }

    return topics.get(subject, [])