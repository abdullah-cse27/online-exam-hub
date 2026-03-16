# =====================================================
# FILE: results.py
# =====================================================

import streamlit as st
import os

from database import get_all_results
from analytics.performance import (
    get_student_summary,
    detect_weak_subjects,
    generate_recommendations
)

RESULT_FILE = "data/results.txt"


# =====================================================
# SAVE RESULT
# =====================================================

def save_result(student_id, subject, score, total, percentage, grade):

    os.makedirs("data", exist_ok=True)

    with open(RESULT_FILE, "a") as file:

        record = f"{student_id}|{subject}|{score}|{total}|{percentage}|{grade}\n"

        file.write(record)


# =====================================================
# SHOW RESULT
# =====================================================

def show_result(student_id):

    if not os.path.exists(RESULT_FILE):

        st.warning("No results available.")
        return

    results = []

    with open(RESULT_FILE, "r") as file:

        for line in file:

            data = line.strip().split("|")

            if data[0] == student_id:

                results.append(data)

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

    if not os.path.exists(RESULT_FILE):
        return

    data = []

    with open(RESULT_FILE, "r") as file:

        for line in file:

            parts = line.strip().split("|")

            student = parts[0]
            percentage = float(parts[4])

            data.append((student, percentage))

    data.sort(key=lambda x: x[1], reverse=True)

    st.subheader("🏆 Leaderboard")

    for i, entry in enumerate(data[:5], start=1):

        st.write(f"{i}. {entry[0]} — {entry[1]}%")