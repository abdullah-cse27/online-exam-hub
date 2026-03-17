# =====================================================
# FILE: results.py
# =====================================================

import streamlit as st
import os

from database import get_all_results, get_leaderboard
from analytics.performance import (
    get_student_summary,
    detect_weak_subjects,
    generate_recommendations
)

RESULT_FILE = "Data/results.txt"


# =====================================================
# SAVE RESULT
# =====================================================

def save_result(student_id, subject, score, total, percentage, grade):

    os.makedirs("Data", exist_ok=True)

    record = f"{student_id}|{subject}|{score}|{total}|{percentage}|{grade}\n"

    with open(RESULT_FILE, "a", encoding="utf-8") as file:
        file.write(record)


# =====================================================
# LOAD STUDENT RESULTS
# =====================================================

def load_student_results(student_id):

    results = []

    if not os.path.exists(RESULT_FILE):
        return results

    with open(RESULT_FILE, "r", encoding="utf-8") as file:

        for line in file:

            parts = line.strip().split("|")

            if len(parts) < 6:
                continue

            if parts[0] == str(student_id):
                results.append(parts)

    return results


# =====================================================
# SHOW RESULT
# =====================================================

def show_result(student_id):

    results = load_student_results(student_id)

    if not results:
        st.warning("No result found.")
        return


    latest = results[-1]

    subject = latest[1]
    score = int(latest[2])
    total = int(latest[3])
    percentage = float(latest[4])
    grade = latest[5]


    # ==============================
    # RESULT HEADER
    # ==============================

    st.title("📊 Exam Result")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Subject", subject)
        st.metric("Score", f"{score}/{total}")

    with col2:
        st.metric("Percentage", f"{percentage}%")
        st.metric("Grade", grade)


    # ==============================
    # PERFORMANCE MESSAGE
    # ==============================

    if percentage >= 90:
        st.success("🔥 Excellent Performance!")

    elif percentage >= 75:
        st.success("👍 Very Good Performance!")

    elif percentage >= 60:
        st.warning("🙂 Good but can improve")

    else:
        st.error("⚠ Needs Improvement")


    # ==============================
    # LOAD ALL RESULTS
    # ==============================

    all_results = get_all_results()


    # ==============================
    # PERFORMANCE ANALYTICS
    # ==============================

    summary = get_student_summary(all_results, student_id)

    if summary:

        st.subheader("📈 Performance Analytics")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Exams", summary["total_exams"])
        col2.metric("Average Score", f"{summary['average_score']}%")
        col3.metric("Subjects Covered", len(summary["subjects"]))


    # ==============================
    # WEAK SUBJECTS
    # ==============================

    weak = detect_weak_subjects(all_results, student_id)

    if weak:

        st.subheader("⚠ Weak Subjects")

        for w in weak:
            st.warning(w)


    # ==============================
    # RECOMMENDATIONS
    # ==============================

    st.subheader("💡 Recommendations")

    rec = generate_recommendations(all_results, student_id)

    for r in rec:
        st.info(r)


    # ==============================
    # HISTORY
    # ==============================

    st.subheader("📜 Exam History")

    for r in results:
        st.write(f"{r[1]} — {r[2]}/{r[3]} ({r[4]}%) Grade {r[5]}")


    # ==============================
    # LEADERBOARD
    # ==============================

    show_leaderboard()


# =====================================================
# LEADERBOARD
# =====================================================

def show_leaderboard():

    leaderboard = get_leaderboard()

    if not leaderboard:
        st.info("Leaderboard not available yet.")
        return

    st.subheader("🏆 Leaderboard")

    for i, entry in enumerate(leaderboard[:5], start=1):

        student, percent = entry

        st.write(f"{i}. {student} — {percent}%")