# ===================================================
# FILE: student.py (STABLE FIXED VERSION)
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
# LOAD STUDY MATERIAL
# ===================================================

def load_study_material():

    material = {}

    try:
        with open("Data/study_material.txt", "r", encoding="utf-8") as f:

            for line in f:

                parts = line.strip().split("|")

                if len(parts) < 5:
                    continue

                subject, topic, explanation, question, answer = parts

                subject = subject.lower()

                if subject not in material:
                    material[subject] = {}

                material[subject][topic] = {
                    "explanation": explanation,
                    "question": question,
                    "answer": answer
                }

    except:
        pass

    return material


# ===================================================
# STUDENT PANEL
# ===================================================

def student_panel():

    st.header("🎓 Student Panel")

    # ---------------------------
    # SESSION SAFETY
    # ---------------------------

    if "userid" not in st.session_state:
        st.error("User not logged in")
        return

    if "exam_active" not in st.session_state:
        st.session_state.exam_active = False

    student_id = st.session_state.userid

    all_results = get_all_results()
    summary = get_student_summary(all_results, student_id)

    # ===================================================
    # EXAM ACTIVE
    # ===================================================

    if st.session_state.exam_active:

        start_exam(
            st.session_state.userid,
            st.session_state.exam_subject
        )

        return

    # ===================================================
    # MENU
    # ===================================================

    menu = [
        "Dashboard",
        "Reading Mode",
        "Latest Quiz",
        "All Quizzes",
        "Start Exam",
        "Leaderboard",
        "View Result",
        "Performance Analytics",
        "Change Password"
    ]

    choice = st.sidebar.selectbox("Menu", menu)

    # ===================================================
    # DASHBOARD
    # ===================================================

    if choice == "Dashboard":

        st.subheader("📊 Student Dashboard")

        if summary:

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Exams", summary.get("total_exams", 0))
            col2.metric("Average Score", f"{summary.get('average_score',0)}%")
            col3.metric("Subjects Covered", len(summary.get("subjects", [])))

        st.divider()

        st.info("Use sidebar to explore learning modules and quizzes.")

    # ===================================================
    # READING MODE
    # ===================================================

    elif choice == "Reading Mode":

        st.subheader("📚 Study Mode")

        material = load_study_material()

        if not material:
            st.warning("No study material available.")
            return

        subjects = list(material.keys())

        subject = st.selectbox("Choose Subject", subjects)

        topics = list(material[subject].keys())

        topic = st.selectbox("Choose Topic", topics)

        st.markdown("### 📖 Explanation")
        st.write(material[subject][topic]["explanation"])

        st.divider()

        st.markdown("### 🧠 Practice Question")
        st.write(material[subject][topic]["question"])

        user_answer = st.text_input("Your Answer")

        if st.button("Check Answer"):

            correct = material[subject][topic]["answer"]

            if user_answer.strip().lower() == correct.lower():
                st.success("Correct Answer ✅")
            else:
                st.error(f"Correct Answer: {correct}")

        st.divider()

        if st.button("Start Topic Quiz"):

            st.session_state.exam_subject = subject
            st.session_state.exam_active = True
            st.rerun()

    # ===================================================
    # LATEST QUIZ
    # ===================================================

    elif choice == "Latest Quiz":

        st.subheader("🆕 Latest Quiz")

        subjects = get_all_subjects()

        if not subjects:
            st.warning("No quizzes available")
            return

        latest = subjects[-1]

        st.success(f"Latest Quiz Available: **{latest}**")

        if st.button("Start Latest Quiz"):

            st.session_state.exam_subject = latest
            st.session_state.exam_active = True
            st.rerun()

    # ===================================================
    # ALL QUIZZES
    # ===================================================

    elif choice == "All Quizzes":

        st.subheader("📚 Available Quizzes")

        subjects = get_all_subjects()

        if not subjects:
            st.warning("No quizzes available")
            return

        for sub in subjects:

            col1, col2 = st.columns([3, 1])

            col1.write(sub)

            if col2.button("Start", key=sub):

                st.session_state.exam_subject = sub
                st.session_state.exam_active = True
                st.rerun()

    # ===================================================
    # START EXAM (FIXED BUG)
    # ===================================================

    elif choice == "Start Exam":

        st.subheader("📝 Start Exam")

        subjects = get_all_subjects()

        if not subjects:
            st.warning("No exams available")
            return

        subject = st.selectbox("Select Subject", subjects)

        if st.button("Start Exam"):

            st.session_state.exam_subject = subject
            st.session_state.exam_active = True
            st.rerun()

    # ===================================================
    # LEADERBOARD
    # ===================================================

    elif choice == "Leaderboard":

        st.subheader("🏆 Leaderboard")

        if not all_results:
            st.warning("No results available yet.")
            return

        scores = {}

        for r in all_results:

            roll = str(r[0])
            percent = float(r[4])

            if roll not in scores:
                scores[roll] = percent
            else:
                scores[roll] = max(scores[roll], percent)

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for i, (roll, percent) in enumerate(sorted_scores[:10]):
            st.write(f"{i+1}. {roll} — {percent}%")
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
            st.info("No results available yet.")

    # ===================================================
    # PERFORMANCE ANALYTICS
    # ===================================================

    elif choice == "Performance Analytics":

        st.subheader("📈 Performance Analytics")

        summary = get_student_summary(all_results, student_id)

        if summary:

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Exams", summary["total_exams"])
            col2.metric("Average Score", f"{summary['average_score']}%")
            col3.metric("Subjects Covered", len(summary["subjects"]))

        weak = detect_weak_subjects(all_results, student_id)

        if weak:

            st.subheader("⚠ Weak Subjects")

            for w in weak:
                st.warning(w)

        rec = generate_recommendations(all_results, student_id)

        st.subheader("💡 Recommendations")

        for r in rec:
            st.info(r)

    # ===================================================
    # CHANGE PASSWORD
    # ===================================================

    elif choice == "Change Password":

        change_password_flow(student_id)


# ===================================================
# PASSWORD CHANGE
# ===================================================

def change_password_flow(student_id):

    st.subheader("🔒 Change Password")

    user = get_user_by_roll(student_id)

    if not user:
        st.error("User not found")
        return

    email = user["email"]

    st.write(f"Email: **{email}**")

    if st.button("Send OTP"):

        otp = generate_otp()

        st.session_state.otp = otp

        if send_otp_email(email, otp):
            st.success("OTP sent")

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

            if newp != conf:
                st.error("Passwords do not match")
                return

            update_user(student_id, password=newp)

            st.success("Password Updated")