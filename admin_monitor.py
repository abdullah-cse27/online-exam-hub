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

    students = [u for u in users if u[3] == "student"]

    # -----------------------------------
    # STUDENT STATUS
    # -----------------------------------

    st.subheader("👨‍🎓 Active Students")

    data = []

    for s in students:

        roll = s[0]

        data.append({
            "Student": roll,
            "Status": "Online"
        })

    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)


    st.divider()


    # -----------------------------------
    # EXAM ANALYTICS
    # -----------------------------------

    st.subheader("📊 Exam Summary")

    total_students = len(students)
    total_exams = len(results)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Registered Students", total_students)

    with col2:
        st.metric("Exams Completed", total_exams)


    st.divider()


    # -----------------------------------
    # RESULT TABLE
    # -----------------------------------

    st.subheader("📑 Recent Exam Results")

    if results:

        result_data = []

        for r in results:

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