import streamlit as st

from database import (
    get_all_questions, add_question, save_all_questions,
    get_user_by_roll, create_empty_user, update_user,
    get_all_results, get_all_users
)

# ======================================================
# ADMIN PANEL MAIN
# ======================================================

def admin_panel():

    st.header("🛠 Admin Control Panel")

    menu = [
        "📊 Dashboard",
        "➕ Add Question",
        "📄 View Questions",
        "✏ Edit Question",
        "❌ Delete Question",
        "➕ Add Student",
        "👥 View Students",
        "✏ Edit Student",
        "❌ Delete Student",
        "📊 Results Analytics",
        "🏆 Leaderboard",
        "📚 Subject Analytics",
        "=> Live Monitoring"
    ]

    choice = st.sidebar.selectbox("Select Action", menu)

    if choice == "📊 Dashboard":
        dashboard()

    elif choice == "➕ Add Question":
        add_question_ui()

    elif choice == "📄 View Questions":
        view_questions_ui()

    elif choice == "✏ Edit Question":
        edit_question_ui()

    elif choice == "❌ Delete Question":
        delete_question_ui()

    elif choice == "➕ Add Student":
        add_student_ui()

    elif choice == "👥 View Students":
        view_students_ui()

    elif choice == "✏ Edit Student":
        edit_student_ui()

    elif choice == "❌ Delete Student":
        delete_student_ui()

    elif choice == "📊 Results Analytics":
        view_results_ui()

    elif choice == "🏆 Leaderboard":
        leaderboard_ui()

    elif choice == "📚 Subject Analytics":
        subject_analytics()

    elif choice == "=> Live Monitoring":

        from admin_monitor import monitor_exam

        monitor_exam()


# ======================================================
# DASHBOARD
# ======================================================

def dashboard():

    st.subheader("📊 System Overview")

    users = get_all_users()
    questions = get_all_questions()
    results = get_all_results()

    students = [u for u in users if u[3] == "student"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Students", len(students))
    col2.metric("Questions", len(questions))
    col3.metric("Exams Taken", len(results))

    st.divider()

    diff = {"Easy":0,"Medium":0,"Hard":0}

    for q in questions:
        if len(q) > 2 and q[2] in diff:
            diff[q[2]] += 1

    st.subheader("📈 Question Difficulty Distribution")

    st.bar_chart(diff)


# ======================================================
# ADD QUESTION
# ======================================================

def add_question_ui():

    st.subheader("➕ Add New Question")

    subject = st.text_input("Subject")
    topic = st.text_input("Topic")

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    qtype = st.selectbox(
        "Question Type",
        ["MCQ", "Coding"]
    )

    question = st.text_area("Enter Question")

    if qtype == "MCQ":

        col1, col2 = st.columns(2)

        with col1:
            A = st.text_input("Option A")
            C = st.text_input("Option C")

        with col2:
            B = st.text_input("Option B")
            D = st.text_input("Option D")

        correct = st.selectbox("Correct Option", ["A", "B", "C", "D"])

        if st.button("Save Question"):

            if subject and topic and question and A and B and C and D:

                line = f"{subject}|{topic}|{difficulty}|mcq|{question}|{A}|{B}|{C}|{D}|{correct}"

                add_question(line)

                st.success("MCQ Question Added Successfully!")

            else:
                st.error("All fields required!")

    else:

        st.subheader("💻 Coding Question")

        sample_input = st.text_input("Sample Input (optional)")

        expected_output = st.text_input("Expected Output")

        if st.button("Save Coding Question"):

            if subject and topic and question and expected_output:

                line = f"{subject}|{topic}|{difficulty}|code|{question}|{sample_input}|{expected_output}"

                add_question(line)

                st.success("Coding Question Added Successfully!")

            else:
                st.error("All fields required!")


# ======================================================
# VIEW QUESTIONS
# ======================================================

def view_questions_ui():

    st.subheader("📄 Question Bank")

    qs = get_all_questions()

    if not qs:
        st.warning("No questions available.")
        return

    search = st.text_input("Search Question")

    subject_filter = st.text_input("Filter by Subject")

    for i, q in enumerate(qs):

        if len(q) < 5:
            continue

        if search and search.lower() not in q[4].lower():
            continue

        if subject_filter and subject_filter.lower() not in q[0].lower():
            continue

        if q[3] == "mcq" and len(q) >= 10:

            st.markdown(f"""
### {i+1}. {q[4]}

**Subject:** {q[0]}  
**Topic:** {q[1]}  
**Difficulty:** {q[2]}

A) {q[5]}  
B) {q[6]}  
C) {q[7]}  
D) {q[8]}

**Correct:** {q[9]}
---
""")

        elif q[3] == "code" and len(q) >= 7:

            st.markdown(f"""
### {i+1}. {q[4]}

**Subject:** {q[0]}  
**Topic:** {q[1]}  
**Difficulty:** {q[2]}

💻 **Coding Question**

**Expected Output:** {q[6]}

---
""")


# ======================================================
# EDIT QUESTION
# ======================================================

def edit_question_ui():

    st.subheader("✏ Edit Question")

    qs = get_all_questions()

    if not qs:
        st.warning("No questions found.")
        return

    index = st.selectbox("Select Question", list(range(len(qs))))

    q = qs[index]

    subject = st.text_input("Subject", q[0])
    topic = st.text_input("Topic", q[1])

    diff_list = ["Easy","Medium","Hard"]
    difficulty = st.selectbox(
        "Difficulty",
        diff_list,
        index=diff_list.index(q[2]) if q[2] in diff_list else 0
    )

    qtype = q[3]

    question = st.text_input("Question", q[4])

    if qtype == "mcq":

        A = st.text_input("Option A", q[5])
        B = st.text_input("Option B", q[6])
        C = st.text_input("Option C", q[7])
        D = st.text_input("Option D", q[8])

        correct_list = ["A","B","C","D"]

        correct = st.selectbox(
            "Correct",
            correct_list,
            index=correct_list.index(q[9]) if q[9] in correct_list else 0
        )

        if st.button("Save Changes"):

            qs[index] = [
                subject,topic,difficulty,"mcq",
                question,A,B,C,D,correct
            ]

            save_all_questions(qs)

            st.success("Question Updated!")

    else:

        sample_input = st.text_input("Sample Input", q[5])
        expected_output = st.text_input("Expected Output", q[6])

        if st.button("Save Changes"):

            qs[index] = [
                subject,topic,difficulty,"code",
                question,sample_input,expected_output
            ]

            save_all_questions(qs)

            st.success("Coding Question Updated!")


# ======================================================
# DELETE QUESTION
# ======================================================

def delete_question_ui():

    st.subheader("❌ Delete Question")

    qs = get_all_questions()

    index = st.selectbox("Select Question", list(range(len(qs))))

    if st.button("Delete"):

        qs.pop(index)

        save_all_questions(qs)

        st.error("Question Deleted")


# ======================================================
# ADD STUDENT
# ======================================================

def add_student_ui():

    st.subheader("➕ Add Student")

    roll = st.text_input("Student Roll Number")

    if st.button("Add Student"):

        if get_user_by_roll(roll):
            st.error("Student already exists")
            return

        create_empty_user(roll, role="student")

        st.success("Student added")


# ======================================================
# VIEW STUDENTS
# ======================================================

def view_students_ui():

    st.subheader("👥 Students")

    users = get_all_users()

    students = [u for u in users if u[3] == "student"]

    for roll,email,passwd,role in students:

        st.markdown(f"""
**Roll:** {roll}  
**Email:** {email if email else "(Not Set)"}  
---
""")


# ======================================================
# RESULTS ANALYTICS
# ======================================================

def view_results_ui():

    st.subheader("📊 Results Analytics")

    results = get_all_results()

    if not results:
        st.warning("No results available")
        return

    for r in results:

        st.write(
            f"{r[0]} | {r[1]} | {r[2]}/{r[3]} | {r[4]}% | {r[5]}"
        )


# ======================================================
# LEADERBOARD
# ======================================================

def leaderboard_ui():

    st.subheader("🏆 Top Students")

    results = get_all_results()

    scores = []

    for r in results:
        scores.append((r[0],float(r[4])))

    scores.sort(key=lambda x:x[1], reverse=True)

    for i,s in enumerate(scores[:10]):

        st.write(f"{i+1}. {s[0]} — {s[1]}%")


# ======================================================
# SUBJECT ANALYTICS
# ======================================================

def subject_analytics():

    st.subheader("📚 Subject Analytics")

    results = get_all_results()

    subjects = {}

    for r in results:

        subject = r[1]
        percent = float(r[4])

        if subject not in subjects:
            subjects[subject] = []

        subjects[subject].append(percent)

    for s in subjects:

        avg = sum(subjects[s]) / len(subjects[s])

        st.write(f"{s} → Average Score: {round(avg,2)}%")
# ======================================================
# EDIT STUDENT
# ======================================================

def edit_student_ui():

    st.subheader("✏ Edit Student")

    users = get_all_users()

    students = [u for u in users if u[3] == "student"]

    if not students:
        st.warning("No students found.")
        return

    rolls = [stu[0] for stu in students]

    selected = st.selectbox("Select Student", rolls)

    stu = next(s for s in students if s[0] == selected)

    new_email = st.text_input("Email", stu[1])

    if st.button("Update Student"):

        update_user(selected, email=new_email)

        st.success("Student Updated Successfully")


# ======================================================
# DELETE STUDENT
# ======================================================

def delete_student_ui():

    st.subheader("❌ Delete Student")

    users = get_all_users()

    students = [u for u in users if u[3] == "student"]

    if not students:
        st.warning("No students found.")
        return

    rolls = [stu[0] for stu in students]

    selected = st.selectbox("Select Student", rolls)

    if st.button("Delete Student"):

        remaining = [u for u in users if u[0] != selected]

        from database import write_file, USERS_FILE

        lines = ["|".join(u) for u in remaining]

        write_file(USERS_FILE, lines)

        st.success("Student Deleted Successfully")