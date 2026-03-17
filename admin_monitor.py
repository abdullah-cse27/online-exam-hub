# ===================================================
# FILE: admin_monitor.py
# ===================================================

import streamlit as st
import pandas as pd
from database import get_all_users, get_all_results


# ===================================================
# MAIN MONITOR
# ===================================================

def monitor_exam():

    st.title("📡 AI Live Exam Monitoring")

    users = get_all_users()
    results = get_all_results()

    students = [u for u in users if len(u) >= 4 and u[3] == "student"]


    # ===================================================
    # ACTIVE STUDENTS
    # ===================================================

    st.subheader("👨‍🎓 Active Students")

    data = []

    for s in students:

        roll = s[0]

        data.append({
            "Student": roll,
            "Status": "Online"
        })

    df = pd.DataFrame(data)

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No students registered yet.")

    st.divider()


    # ===================================================
    # SYSTEM SUMMARY
    # ===================================================

    st.subheader("📊 System Overview")

    total_students = len(students)
    total_exams = len(results)

    unique_subjects = set()

    for r in results:

        if len(r) > 1:
            unique_subjects.add(r[1])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Registered Students", total_students)

    with col2:
        st.metric("Exams Completed", total_exams)

    with col3:
        st.metric("Subjects", len(unique_subjects))

    st.divider()


    # ===================================================
    # SUBJECT ANALYTICS
    # ===================================================

    st.subheader("📚 Subject Analytics")

    subject_stats = {}

    for r in results:

        if len(r) < 6:
            continue

        subject = r[1]

        try:
            percent = float(r[4])
        except:
            continue

        if subject not in subject_stats:
            subject_stats[subject] = []

        subject_stats[subject].append(percent)

    chart_data = []

    for sub in subject_stats:

        avg = sum(subject_stats[sub]) / len(subject_stats[sub])

        chart_data.append({
            "Subject": sub,
            "Average Score": round(avg, 2)
        })

    if chart_data:

        chart_df = pd.DataFrame(chart_data)

        st.bar_chart(chart_df.set_index("Subject"))

    else:

        st.info("No subject data yet.")

    st.divider()


    # ===================================================
    # RECENT RESULTS
    # ===================================================

    st.subheader("📑 Recent Exam Results")

    if results:

        result_data = []

        for r in results:

            if len(r) < 6:
                continue

            result_data.append({
                "Student": r[0],
                "Subject": r[1],
                "Score": f"{r[2]}/{r[3]}",
                "Percentage": f"{r[4]}%",
                "Grade": r[5]
            })

        res_df = pd.DataFrame(result_data)

        st.dataframe(res_df, use_container_width=True)

    else:

        st.info("No exam results yet.")

    st.divider()


    # ===================================================
    # TOP PERFORMERS
    # ===================================================

    st.subheader("🏆 Top Performers")

    leaderboard = []

    for r in results:

        if len(r) < 6:
            continue

        try:
            leaderboard.append((r[0], float(r[4])))
        except:
            continue

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    if leaderboard:

        for i, entry in enumerate(leaderboard[:5], start=1):

            st.write(f"{i}. {entry[0]} — {entry[1]}%")

    else:

        st.info("Leaderboard not available yet.")