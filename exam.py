# ============================================================
# FILE: exam.py (FINAL STABLE VERSION WITH LIVE PROCTORING + TEST CASES)
# ============================================================

import streamlit as st
import random
import numpy as np
import av
from PIL import Image
from streamlit_ace import st_ace
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

st.set_page_config(layout="wide")

from database import get_all_questions, increase_attempt
from results import save_result, show_result
from code_runner.executor import run_code
from monitoring.proctoring import analyze_frame
from anti_cheat.ai_detector import cheating_risk

# ============================================================
# AI PROCTORING PROCESSOR
# ============================================================

class ProctorProcessor(VideoProcessorBase):

    def __init__(self):
        self.frame_count = 0

    def recv(self, frame):

        img = frame.to_ndarray(format="bgr24")

        self.frame_count += 1

        # Run AI every 5 frames only
        if self.frame_count % 5 == 0:

            processed_frame, data = analyze_frame(img)

            risk = cheating_risk(data)

            st.session_state.cheat_risk = risk

            if "faces" in data:
                st.session_state.faces_detected = data["faces"]

        else:
            processed_frame = img

        return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")


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
        "fast_answers": 0,
        "editor_reset": 0,
        "camera_started": False,
        "cheat_risk": 0,
        "faces_detected": 0
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ============================================================
# LIVE CAMERA MONITORING
# ============================================================

def live_monitor():

    st.markdown("""
    <style>
    .hidden-cam{
        position:fixed;
        left:-9999px;
        top:-9999px;
        width:1px;
        height:1px;
        opacity:0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hidden-cam">', unsafe_allow_html=True)

    webrtc_streamer(
        key="exam-monitor",
        video_processor_factory=ProctorProcessor,
        desired_playing_state=True,
        media_stream_constraints={"video": True, "audio": False}
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SECURITY SCRIPT
# ============================================================

def security_script():

    components.html("""
<script>

if(!window.examSecurityLoaded){

window.examSecurityLoaded=true;

const parentDoc = window.parent.document;

parentDoc.addEventListener("visibilitychange",function(){

if(parentDoc.hidden){

const overlay = parentDoc.createElement("div");

overlay.style.position="fixed";
overlay.style.top="0";
overlay.style.left="0";
overlay.style.width="100%";
overlay.style.height="100%";
overlay.style.background="rgba(0,0,0,0.85)";
overlay.style.color="white";
overlay.style.zIndex="999999";
overlay.style.display="flex";
overlay.style.flexDirection="column";
overlay.style.alignItems="center";
overlay.style.justifyContent="center";
overlay.style.fontSize="28px";

let time = 20;

overlay.innerHTML = `
<h1>⚠ Tab Switching Detected</h1>
<p id="count">Exam will terminate in 20 sec</p>
<button id="cancelBtn"
style="padding:12px 30px;font-size:20px;margin-top:20px;border:none;background:green;color:white;border-radius:8px;">
Cancel
</button>
`;

parentDoc.body.appendChild(overlay);

const timer = setInterval(()=>{

time--;

parentDoc.getElementById("count").innerText =
"Exam will terminate in "+time+" sec";

if(time<=0){

clearInterval(timer);

location.reload();

}

},1000);

parentDoc.getElementById("cancelBtn").onclick = function(){

clearInterval(timer);
overlay.remove();

}

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

    if st.button("Proceed to Rules"):
        st.session_state.step="rules"
        st.rerun()


# ============================================================
# RULES
# ============================================================

def rules_step():

    st.title("📜 Exam Rules")

    st.markdown("""
    - Do not switch tabs
    - Do not use phone
    - Camera must remain ON
    - Copy paste disabled
    - Each MCQ timed
    """)

    if st.button("Proceed to Camera"):
        st.session_state.step="camera"
        st.rerun()


# ============================================================
# CAMERA VERIFICATION
# ============================================================

def camera_step():

    st.title("Camera Setup")

    st.write("Ensure your face is visible")

    webrtc_streamer(
        key="camera-preview",
        media_stream_constraints={
            "video": True,
            "audio": False
        }
    )

    if st.button("Start Exam"):
        st.session_state.camera_started = True
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
font-size:32px;
font-family:monospace;
color:red;
font-weight:bold;
position:fixed;
top:10px;
left:50%;
transform:translateX(-50%);
z-index:9999;">
</div>

<script>

if(!window.currentQuestion || window.currentQuestion !== "{qid}"){{

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
if(btn.innerText.includes("Skip")){{
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
# TEST CASE RUNNER
# ============================================================

def run_test_cases(language, code, test_cases, expected_output):

    passed = 0
    total = len(test_cases)

    results = []

    for case in test_cases:

        try:

            input_data = " ".join(map(str, case))

            output = run_code(language, code, input_data)

            if output.strip() == expected_output.strip():

                passed += 1
                results.append("✅ Passed")

            else:

                results.append("❌ Failed")

        except:

            results.append("⚠ Error")

    return passed, total, results


# ============================================================
# EXAM STEP
# ============================================================

def exam_step(student_id, subject):
    st.markdown("""
    <style>

    /* Hide sidebar */
    [data-testid="stSidebar"] {display:none;}

    /* Center main block */
    .block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    max-width:1200px;
    }

    /* Hide webcam video */
    video{
    display:none !important;
    }

    /* Reduce space */
    div[data-testid="stVerticalBlock"] > div:empty{
    display:none;
    }

    /* Question card */
    .question-card{
    padding:12px;
    border-radius:10px;
    background:white;
    border:1px solid #e0e0e0;
    font-size:18px;
    box-shadow:0 2px 5px rgba(0,0,0,0.08);
    }

    /* Radio spacing */
    div[role="radiogroup"]{
    margin-top:-10px;
    }

    </style>
    """, unsafe_allow_html=True)

    security_script()

    left, right = st.columns([5,1])

    with right:

        if st.session_state.camera_started:
            live_monitor()

            st.metric("⚠ Cheating Risk", round(st.session_state.cheat_risk,2))
            st.metric("👤 Faces", st.session_state.faces_detected)


    # QUESTION PANEL
    with left:

        if not st.session_state.questions:

            st.session_state.questions = prepare_questions(subject)

            if not st.session_state.questions:
                st.error("No quiz available")
                return

        qs = st.session_state.questions
        i = st.session_state.index

        if i >= len(qs):
            finalize_exam(student_id, subject)
            return

        q = qs[i]

        st.progress((i + 1) / len(qs))

        limit = 30 if q[3] == "mcq" else 180

        js_timer(limit, f"{i}-{q[4]}")

        with st.container():

            st.markdown(f"### 📝 Question {i+1}")

            st.markdown(f"""
            <div class="question-card">
            {q[4]}
            </div>
            """, unsafe_allow_html=True)


    # =========================
    # MCQ
    # =========================

    if q[3] == "mcq":

        options = {
            "A": q[5],
            "B": q[6],
            "C": q[7],
            "D": q[8]
        }

        option_list = [f"{k}) {v}" for k, v in options.items()]

        previous = st.session_state.answers.get(i)

        index_value = None
        if previous:
            index_value = ["A","B","C","D"].index(previous)
        st.markdown("""
        <style>
        div[role="radiogroup"]{
        margin-top:-10px;
        }
        </style>
        """, unsafe_allow_html=True)
        selected = st.radio(
            "Choose Answer",
            option_list,
            index=index_value,
            key=f"mcq{i}"
        )
        col1, col2, col3 = st.columns([1,1,1])
        if col1.button("⬅ Previous", use_container_width=True):

            if i > 0:
                st.session_state.index -= 1
                st.rerun()

        if col2.button("Skip", use_container_width=True):

            st.session_state.skips += 1
            st.session_state.index += 1
            st.rerun()

        if col3.button("Submit", use_container_width=True):

            ans = selected.split(")")[0]

            prev = st.session_state.answers.get(i)

            st.session_state.answers[i] = ans

            if prev is None and ans == q[9]:
                st.session_state.score += 1

            st.session_state.index += 1
            st.rerun()

# ============================================================
# CODING
# ============================================================

    elif q[3] == "code":

        st.markdown("### Expected Output")
        st.code(q[6])

        test_cases = []

        if len(q) > 10:
            test_cases = q[10]

        ace_language = {
            "Python": "python",
            "C": "c_cpp",
            "C++": "c_cpp"
        }.get(q[0], "python")

        editor_key = f"editor_{i}_{st.session_state.editor_reset}"

        code = st_ace(
            language=ace_language,
            height=220,
            key=editor_key,
            wrap=True,
            theme="monokai",
            font_size=16,
            value="# Write your code here\n"
        )

        # ---------------------------
        # RUN CODE
        # ---------------------------

        if st.button("Run Code"):

            output = run_code(q[0], code)
            st.code(output)

        # ---------------------------
        # RUN TEST CASES
        # ---------------------------

        if test_cases:

            if st.button("Run Test Cases"):

                passed, total, results = run_test_cases(q[0], code, test_cases, q[6])

                st.markdown("### Test Case Results")

                for idx, res in enumerate(results):

                    st.write(f"Test Case {idx+1}: {res}")

                st.success(f"{passed}/{total} Passed")

        # ---------------------------
        # NAVIGATION BUTTONS
        # ---------------------------

        col1, col2, col3 = st.columns([1,1,1])

        if col1.button("⬅ Previous", use_container_width=True):

            if i > 0:
                st.session_state.index -= 1
                st.rerun()

        if col2.button("Skip", use_container_width=True):

            st.session_state.index += 1
            st.session_state.editor_reset += 1
            st.rerun()

        if col3.button("Submit", use_container_width=True):

            result = run_code(q[0], code)

            if result.strip() == q[6].strip():
                st.session_state.score += 1

            st.session_state.index += 1
            st.session_state.editor_reset += 1
            st.rerun()

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

    if st.button("Go Dashboard"):

        for k in list(st.session_state.keys()):
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

    elif step == "rules":
        rules_step()

    elif step == "camera":
        camera_step()

    elif step == "exam":
        exam_step(student_id, subject)