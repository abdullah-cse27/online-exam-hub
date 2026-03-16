# ===================================================
# FILE: student.py
# ===================================================

import streamlit as st

from exam import start_exam

from database import (
    get_result,
    get_user_by_roll,
    update_user,
    get_all_subjects,
    get_attempts,
    get_all_results
)

from email_service import generate_otp, send_otp_email

from analytics.performance import (
    get_student_summary,
    detect_weak_subjects,
    generate_recommendations
)


# ===================================================
# STUDENT PANEL
# ===================================================

def student_panel():

    st.header("🎓 Student Panel")

    student_id = st.session_state.userid

    # Load all results once
    all_results = get_all_results()


    # ===================================================
    # PERFORMANCE DASHBOARD
    # ===================================================

    summary = get_student_summary(all_results, student_id)

    if summary:

        st.subheader("📊 Performance Dashboard")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Exams", summary.get("total_exams", 0))
        col2.metric("Average Score", f"{summary.get('average_score',0)}%")
        col3.metric("Subjects Covered", len(summary.get("subjects", [])))

        st.divider()


    # ===================================================
    # PREVENT EXIT DURING EXAM
    # ===================================================

    if st.session_state.get("exam_active", False):

        st.warning("⚠ Exam in progress. Navigation disabled.")

        start_exam(
            st.session_state.userid,
            st.session_state.exam_subject
        )

        return


    # ===================================================
    # MENU
    # ===================================================

    menu = [
        "Start Exam",
        "View Result",
        "Exam History",
        "Performance Analytics",
        "Change Password"
    ]

    choice = st.selectbox("Select Option", menu)


    # ===================================================
    # START EXAM
    # ===================================================

    if choice == "Start Exam":

        subjects = get_all_subjects()

        if not subjects:
            st.warning("No subjects found!")
            return

        subject = st.selectbox("Select Subject", subjects)

        attempts = get_attempts(student_id, subject)

        st.info(f"Attempts used: {attempts} / 3")

        if attempts >= 3:
            st.error("❌ Maximum attempts reached.")
            return

        if st.button("Continue ➜", use_container_width=True):

            st.session_state.exam_subject = subject
            st.session_state.show_rules = True

            st.rerun()

        if st.session_state.get("show_rules", False):

            show_exam_rules(student_id, subject)
            return


    # ===================================================
    # VIEW RESULT
    # ===================================================

    elif choice == "View Result":

        result = get_result(student_id)

        if result:

            roll, subject, score, total, percent, grade = result

            st.subheader("📊 Latest Result")

            st.write(f"Subject: **{subject}**")
            st.write(f"Score: **{score}/{total}**")
            st.write(f"Percentage: **{percent}%**")
            st.write(f"Grade: **{grade}**")

        else:
            st.warning("No result found.")


    # ===================================================
    # EXAM HISTORY
    # ===================================================

    elif choice == "Exam History":

        history = [r for r in all_results if r[0] == student_id]

        if not history:
            st.warning("No exam history found.")
            return

        st.subheader("📜 Exam History")

        for r in history:

            st.write(
                f"{r[1]} — Score {r[2]}/{r[3]} | {r[4]}% | Grade {r[5]}"
            )


    # ===================================================
    # PERFORMANCE ANALYTICS
    # ===================================================

    elif choice == "Performance Analytics":

        summary = get_student_summary(all_results, student_id)

        if not summary:
            st.warning("No analytics available yet.")
            return

        st.subheader("📈 Detailed Analytics")

        st.write("Average Score:", summary.get("average_score",0), "%")

        weak = detect_weak_subjects(all_results, student_id)

        if weak:

            st.subheader("⚠ Weak Subjects")

            for w in weak:
                st.warning(w)

        st.subheader("💡 Recommendations")

        rec = generate_recommendations(all_results, student_id)

        for r in rec:
            st.info(r)


    # ===================================================
    # CHANGE PASSWORD
    # ===================================================

    elif choice == "Change Password":

        change_password_flow(student_id)



# ===================================================
# SHOW RULES
# ===================================================

def show_exam_rules(student_id, subject):

    st.subheader("📘 Exam Rules")

    st.markdown("""
### ⚠ Important Instructions

✔ Each question has **20 second timer**  
✔ Questions appear in **random order**  
✔ **Tab switching detected**  
✔ **No going back**  
✔ **Max 3 attempts per subject**

Passing Criteria

A = 90%+  
B = 75%+  
C = 60%+  
FAIL otherwise
""")

    if st.button("I Agree & Start Exam 🚀"):

        st.session_state.show_rules = False
        st.session_state.exam_active = True
        st.session_state.exam_subject = subject

        st.rerun()



# ===================================================
# CHANGE PASSWORD FLOW
# ===================================================

def change_password_flow(student_id):

    st.subheader("🔒 Change Password")

    user = get_user_by_roll(student_id)

    if not user:
        st.error("User not found!")
        return

    email = user["email"]

    if not email:
        st.error("Email not registered!")
        return

    st.write(f"Email: **{email}**")

    if st.button("Send OTP"):

        otp = generate_otp()

        st.session_state.otp = otp

        if send_otp_email(email, otp):
            st.success("OTP sent to email")

    if "otp" in st.session_state:

        entered = st.text_input("Enter OTP")

        if st.button("Verify OTP"):

            if entered == st.session_state.otp:

                st.session_state.otp_verified = True
                st.success("OTP Verified")

            else:
                st.error("Wrong OTP")

    if st.session_state.get("otp_verified"):

        newp = st.text_input("New Password", type="password")
        conf = st.text_input("Confirm Password", type="password")

        if st.button("Update Password"):

            if newp == conf and len(newp) >= 6:

                update_user(student_id, password=newp)

                st.success("Password Updated")

                st.session_state.otp_verified = False
                st.session_state.otp = None

            else:
                st.error("Passwords must match and be at least 6 characters")