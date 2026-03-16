# ===================================================
# FILE: analytics/improvement_ai.py
# ===================================================

def improvement_plan(results, student_id):

    weak_subjects = []

    for r in results:

        if r[0] == student_id:

            percent = float(r[4])

            if percent < 60:

                weak_subjects.append(r[1])


    suggestions = []

    if not weak_subjects:

        suggestions.append("Maintain your performance by solving advanced questions.")

    else:

        for sub in set(weak_subjects):

            suggestions.append(
                f"Practice more questions in {sub}"
            )

    return suggestions