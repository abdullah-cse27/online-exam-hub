# =====================================================
# FILE: results.py (UPDATED WITH PROCTORING ANALYTICS)
# =====================================================

import streamlit as st
import os
import time

from database import get_all_results, get_leaderboard
from analytics.performance import (
    get_student_summary,
    detect_weak_subjects,
    generate_recommendations
)

RESULT_FILE = "Data/results.txt"


# =====================================================
# SAVE RESULT (UPDATED TO INCLUDE CHEAT RISK)
# =====================================================

def save_result(student_id, subject, score, total, percentage, grade, cheat_risk=0):
    os.makedirs("Data", exist_ok=True)
    
    timestamp = str(int(time.time()))
    # Adding timestamp and cheat_risk to the record
    record = f"{student_id}|{subject}|{score}|{total}|{percentage}|{grade}|{timestamp}|{cheat_risk}\n"

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
            # Checking for updated 8-part format or old 6-part format
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
    
    # Extract cheat risk if available (8th index), otherwise default to 0
    cheat_risk = float(latest[7]) if len(latest) >= 8 else 0


    # ==============================
    # RESULT HEADER
    # ==============================
    st.title("📊 Exam Result")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Subject", subject)
        st.metric("Score", f"{score}/{total}")

    with col2:
        st.metric("Percentage", f"{percentage}%")
        st.metric("Grade", grade)
        
    with col3:
        # Highlighting Cheating Risk for proctors
        st.metric("AI Risk Score", f"{cheat_risk}%", delta=f"{cheat_risk}%", delta_color="inverse")


    # ==============================
    # PROCTORING FEEDBACK
    # ==============================
    if cheat_risk > 70:
        st.error(f"🚨 **High Integrity Risk:** AI detected multiple anomalies ({cheat_risk}% risk).")
    elif cheat_risk > 40:
        st.warning(f"⚠ **Proctoring Note:** Some suspicious behavior was flagged.")
    else:
        st.success("✅ **Integrity Verified:** Exam completed with high trust score.")


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
    # ANALYTICS & HISTORY (Logic remains same)
    # ==============================
    all_results = get_all_results()
    summary = get_student_summary(all_results, student_id)

    if summary:
        st.subheader("📈 Performance Analytics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Exams", summary["total_exams"])
        c2.metric("Average Score", f"{summary['average_score']}%")
        c3.metric("Subjects Covered", len(summary["subjects"]))

    weak = detect_weak_subjects(all_results, student_id)
    if weak:
        st.subheader("⚠ Weak Subjects")
        for w in weak:
            st.warning(w)

    st.subheader("💡 Recommendations")
    rec = generate_recommendations(all_results, student_id)
    for r in rec:
        st.info(r)

    st.subheader("📜 Exam History")
    for r in results:
        risk_val = r[7] if len(r) >= 8 else "N/A"
        st.write(f"📅 {r[1]} — {r[2]}/{r[3]} ({r[4]}%) | Grade: {r[5]} | Risk: {risk_val}%")

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
        st.write(f"{i}. Student Roll: {student} — {percent}%")