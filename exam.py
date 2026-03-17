# ============================================================
# FILE: exam.py (FIXED STABLE VERSION - CLEAN INDENTED)
# ============================================================

import streamlit as st
import random
import numpy as np
from PIL import Image
from streamlit_ace import st_ace
import streamlit.components.v1 as components

from database import get_all_questions, increase_attempt
from results import save_result, show_result
from code_runner.executor import run_python_code
from monitoring.proctoring import analyze_frame
from anti_cheat.ai_detector import cheating_risk

st.set_page_config(layout="wide")

# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}

.timer{
font-size:30px;
color:red;
font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

def init_state():

    defaults = {
        "step": "fullscreen",
        "index": 0,
        "score": 0,
        "questions": [],
        "answers": {},
        "tab_switches": 0,
        "skips": 0,
        "fast_answers": 0
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ============================================================
# SECURITY SCRIPT
# ============================================================

def security_script():

    components.html("""
<script>

if(!window.examSecurityLoaded){

    window.examSecurityLoaded = true;

    const parentDoc = window.parent.document;

    parentDoc.addEventListener("visibilitychange", function(){

        if(parentDoc.hidden){
            alert("Tab switching detected!");
        }

    });

}

</script>
""", height=0)


# ============================================================
# FULLSCREEN STEP
# ============================================================

def fullscreen_step():

    st.title("Enter Fullscreen Mode")

    components.html(
        """
        <div style="text-align:center;margin-top:100px;">

        <button onclick="openFullscreen()" 
        style="padding:20px;font-size:20px;background:green;color:white;border:none;border-radius:10px;">
        Enter Fullscreen
        </button>

        </div>

        <script>

        function openFullscreen(){

            const elem=parent.document.documentElement;

            if(elem.requestFullscreen){
                elem.requestFullscreen();
            }

        }

        </script>
        """,
        height=200
    )

    if st.button("Proceed to Camera"):
        st.session_state.step = "camera"
        st.rerun()


# ============================================================
# CAMERA STEP
# ============================================================

def camera_step():

    st.title("Camera Verification")

    cam = st.camera_input("Capture your face")

    if cam:

        img = Image.open(cam)
        img = np.array(img)

        result = analyze_frame(img)

        if result["warning"]:
            st.error(result["warning"])

        else:

            st.success("Face verified successfully")

            if st.button("Start Exam"):
                st.session_state.step = "exam"
                st.rerun()


# ============================================================
# LOAD QUESTIONS
# ============================================================

def prepare_questions(subject):

    qs = get_all_questions()

    mcq = [q for q in qs if q[0] == subject and q[3] == "mcq"]
    code = [q for q in qs if q[0] == subject and q[3] == "code"]

    random.shuffle(mcq)
    random.shuffle(code)

    return mcq[:10] + code[:5]


# ============================================================
# TIMER
# ============================================================

def js_timer(limit, qid):

    components.html(f"""
<div id="timer"
style="
font-size:40px;
color:red;
font-weight:bold;
position:fixed;
top:10px;
left:50%;
transform:translateX(-50%);
z-index:9999;">
</div>

<script>

if(window.currentQuestion !== "{qid}"){{

    window.currentQuestion = "{qid}";

    if(window.examTimer){{
        clearInterval(window.examTimer);
    }}

    let t = {limit};

    const timerBox = document.getElementById("timer");

    function updateTimer(){{

        timerBox.innerHTML = "Time Left: " + t + " sec";

        t--;

        if(t < 0){{

            clearInterval(window.examTimer);

            const buttons = window.parent.document.querySelectorAll("button");

            buttons.forEach(btn=>{{
                if(btn.innerText==="Skip"){{
                    btn.click();
                }}
            }});

        }}

    }}

    updateTimer();

    window.examTimer = setInterval(updateTimer,1000);

}}

</script>
""", height=80)


# ============================================================
# EXAM STEP
# ============================================================

def exam_step(student_id, subject):

    security_script()

    if not st.session_state.questions:

        st.session_state.questions = prepare_questions(subject)

        if not st.session_state.questions:
            st.error("No quiz available for this subject.")
            return

    qs = st.session_state.questions
    i = st.session_state.index

    if i >= len(qs):
        finalize_exam(student_id, subject)
        return

    q = qs[i]

    st.progress((i + 1) / len(qs))

    limit = 20 if q[3] == "mcq" else 180

    js_timer(limit, f"{i}-{q[4]}")

    st.markdown(f"### Question {i+1}")
    st.write(q[4])

    # ============================================================
    # MCQ
    # ============================================================

    if q[3] == "mcq":

        options = {
            "A": q[5],
            "B": q[6],
            "C": q[7],
            "D": q[8]
        }

        selected = st.radio(
            "Choose Answer",
            [f"{k}) {v}" for k, v in options.items()],
            key=f"mcq{i}"
        )

        col1, col2, col3 = st.columns(3)

        if col1.button("Previous"):

            if i > 0:
                st.session_state.index -= 1
                st.rerun()

        if col2.button("Skip"):

            st.session_state.skips += 1
            st.session_state.index += 1
            st.rerun()

        if col3.button("Submit"):

            ans = selected.split(")")[0]

            st.session_state.answers[i] = ans

            if ans == q[9]:
                st.session_state.score += 1

            st.session_state.index += 1
            st.rerun()

    # ============================================================
    # CODING
    # ============================================================

    elif q[3] == "code":

        st.write("Expected Output:")
        st.code(q[6])

        code = st_ace(language="python", height=300)

        if st.button("Run Code"):

            output = run_python_code(code)
            st.code(output)

        col1, col2, col3 = st.columns(3)

        if col1.button("Previous"):

            if i > 0:
                st.session_state.index -= 1
                st.rerun()

        if col2.button("Skip"):

            st.session_state.skips += 1
            st.session_state.index += 1
            st.rerun()

        if col3.button("Submit Code"):

            result = run_python_code(code)

            if result.strip() == q[6].strip():
                st.session_state.score += 1

            st.session_state.index += 1
            st.rerun()

    # ============================================================
    # RISK SCORE
    # ============================================================

    risk = cheating_risk(
        st.session_state.tab_switches,
        st.session_state.fast_answers,
        st.session_state.skips
    )

    st.sidebar.metric("Risk Score", risk["risk_score"])
    st.sidebar.write("Risk Level:", risk["risk_level"])


# ============================================================
# RESULT
# ============================================================

def finalize_exam(student_id, subject):

    score = st.session_state.score
    total = len(st.session_state.questions)

    percent = (score / total) * 100

    save_result(student_id, subject, score, total, percent, "Completed")
    increase_attempt(student_id, subject)

    st.success("Exam Completed")

    st.write("Score:", score, "/", total)
    st.write("Percentage:", percent)

    show_result(student_id)

    st.divider()

    if st.button("🏠 Go to Dashboard"):

        keys = [
            "step",
            "index",
            "score",
            "questions",
            "answers",
            "exam_active"
        ]

        for k in keys:
            if k in st.session_state:
                del st.session_state[k]

        st.rerun()


# ============================================================
# ENTRY
# ============================================================

def start_exam(student_id, subject):

    init_state()

    step = st.session_state.step

    if step == "fullscreen":
        fullscreen_step()

    elif step == "camera":
        camera_step()

    elif step == "exam":
        exam_step(student_id, subject)