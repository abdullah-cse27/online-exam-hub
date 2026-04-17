import streamlit as st
import random
import numpy as np
import av
from PIL import Image
from streamlit_ace import st_ace
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# --- INTERNAL IMPORTS ---
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
        self.risk = 0
        self.faces = 1
        self.warning = ""

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.frame_count += 1
        
        try:
            if self.frame_count % 5 == 0:
                processed_frame, data = analyze_frame(img)
                self.faces = data.get("faces", 0)
                self.warning = data.get("warning", "")
                
                risk_data = cheating_risk(
                    data=data,
                    tab_switches=0, 
                    fast_answers=0,
                    skips=0,
                    camera_warnings=1 if self.faces == 0 or self.faces > 1 or self.warning else 0,
                    suspicious_motion=data.get("motion", 0)
                )
                self.risk = risk_data.get("risk_score", 0)
        except:
            pass
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ============================================================
# 🚀 SMOOTH MONITORING FRAGMENT
# ============================================================

@st.fragment(run_every=1.0)
def smooth_metrics_display(ctx):
    # Agar exam finish ho gaya hai toh metrics dikhana band kar do
    if st.session_state.get("exam_finished", False):
        return

    if ctx and ctx.video_processor:
        risk = ctx.video_processor.risk
        faces = ctx.video_processor.faces
        warning = ctx.video_processor.warning
        
        col1, col2 = st.columns(2)
        col1.metric("Risk Score", f"{round(risk, 1)}%")
        col2.metric("Persons Detected", faces)
        
        if faces > 1: st.error(f"🚨 ALERT: {faces} People Detected!")
        if warning: st.warning(warning)
        elif risk < 25: st.success("✅ Environment Secure")
    else:
        st.info("Initializing Camera...")

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
        "camera_started": False,
        "exam_finished": False  # New Flag
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ============================================================
# LIVE CAMERA MONITORING (FIXED: Auto-Stop)
# ============================================================

def live_monitor():
    # Agar exam finish ho gaya hai toh camera component render hi nahi hoga
    if st.session_state.get("exam_finished", False):
        return None

    ctx = webrtc_streamer(
        key="exam-monitor",
        video_processor_factory=ProctorProcessor,
        desired_playing_state=True,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
        rtc_configuration={"iceServers":[{"urls":["stun:stun.l.google.com:19302"]}]}
    )
    return ctx

# ============================================================
# SECURITY SCRIPT (FIXED: Auto-Deactivate)
# ============================================================

def security_script():
    # Passing the finished status to JS
    is_finished = "true" if st.session_state.get("exam_finished", False) else "false"
    
    components.html(f"""
<script>
// Global status to stop checks
window.parent.examFinished = {is_finished};

if(!window.examSecurityLoaded){{
    window.examSecurityLoaded = true;
    const parentDoc = window.parent.document;

    function triggerSecurity(){{
        // Don't trigger if exam is over
        if(window.parent.examFinished === true) return;
        
        if(parentDoc.getElementById("examOverlay")) return;

        const overlay = parentDoc.createElement("div");
        overlay.id = "examOverlay";
        overlay.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);color:white;z-index:999999;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:28px;font-family:sans-serif;";
        overlay.innerHTML = `
            <h1 style="color:red;">⚠ Tab Switching Detected</h1>
            <p id="count">Please return to exam</p>
            <button id="continueExam" style="margin-top:20px;padding:12px 24px;font-size:18px;background:green;color:white;border:none;border-radius:6px;cursor:pointer;">
                Continue Exam
            </button>
        `;
        parentDoc.body.appendChild(overlay);
        parentDoc.getElementById("continueExam").onclick = () => overlay.remove();
    }}

    parentDoc.addEventListener("visibilitychange", () => {{
        if(parentDoc.hidden) triggerSecurity();
    }});
    window.addEventListener("blur", () => triggerSecurity());
}}
</script>
""", height=0)

# ============================================================
# STEPS
# ============================================================

def fullscreen_step():
    st.title("Enter Fullscreen Mode")
    st.info("Assessment must be taken in fullscreen to ensure proctoring accuracy.")
    components.html("""
        <div style="text-align:center;margin-top:50px;">
            <button onclick="openFullscreen()" style="padding:15px 30px;font-size:20px;background:#2E7D32;color:white;border:none;border-radius:10px;cursor:pointer;">
            Launch Fullscreen
            </button>
        </div>
        <script>
        function openFullscreen(){
            const elem = parent.document.documentElement;
            if(elem.requestFullscreen){ elem.requestFullscreen(); }
        }
        </script>""", height=150)
    if st.button("Proceed to Rules"):
        st.session_state.step="rules"
        st.rerun()

def rules_step():
    st.title("📜 Exam Rules")
    st.markdown("1. No Tab Switching\n2. AI Proctoring Active\n3. Don't leave the camera frame.")
    if st.button("Proceed to Camera Setup"):
        st.session_state.step="camera"
        st.rerun()

def camera_step():
    st.title("Camera Setup")
    webrtc_streamer(key="camera-preview", media_stream_constraints={"video": True, "audio": False})
    if st.button("Start Exam"):
        st.session_state.camera_started = True
        st.session_state.step = "exam"
        st.rerun()

# ============================================================
# EXAM ENGINE
# ============================================================

def prepare_questions(subject):
    qs = get_all_questions()
    mcq = [q for q in qs if q[0] == subject and q[3] == "mcq"]
    code = [q for q in qs if q[0] == subject and q[3] == "code"]
    random.shuffle(mcq); random.shuffle(code)
    return mcq[:10] + code[:5]

def js_timer(limit, qid):
    components.html(f"""
<div id="timer" style="font-size:28px;font-family:monospace;color:#D32F2F;font-weight:bold;position:fixed;top:15px;left:50%;transform:translateX(-50%);z-index:9999;background:white;padding:5px 15px;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.2);"></div>
<script>
if(!window.currentQuestion || window.currentQuestion !== "{qid}"){{
    window.currentQuestion = "{qid}";
    if(window.examTimer){{ clearInterval(window.examTimer); }}
    let t = {limit};
    const timerBox = document.getElementById("timer");
    window.examTimer = setInterval(()=>{{
        timerBox.innerHTML = "⏱ " + t + "s";
        t--;
        if(t < 0){{
            clearInterval(window.examTimer);
            window.parent.document.querySelectorAll("button").forEach(btn=>{{
                if(btn.innerText.includes("Skip")) btn.click();
            }});
        }}
    }},1000);
}}
</script>""", height=70)

def exam_step(student_id, subject):
    st.markdown("<style>[data-testid='stSidebar'] {display:none;} .block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)
    security_script()

    left, right = st.columns([4, 1.2])

    with right:
        st.markdown("### Monitoring")
        if st.session_state.camera_started and not st.session_state.exam_finished:
            ctx = live_monitor()
            smooth_metrics_display(ctx)

    with left:
        if not st.session_state.questions:
            st.session_state.questions = prepare_questions(subject)
        
        qs = st.session_state.questions
        i = st.session_state.index

        if i >= len(qs):
            finalize_exam(student_id, subject)
            return

        q = qs[i]
        st.progress((i + 1) / len(qs))
        limit = 30 if q[3] == "mcq" else 300
        js_timer(limit, f"q-{i}")

        st.markdown(f"### Question {i+1} of {len(qs)}")
        st.info(q[4])

        if q[3] == "mcq":
            options = [f"A) {q[5]}", f"B) {q[6]}", f"C) {q[7]}", f"D) {q[8]}"]
            selected = st.radio("Select answer:", options, key=f"mcq{i}")
            col1, col2, col3 = st.columns([1,1,1])
            if col1.button("⬅ Previous") and i > 0:
                st.session_state.index -= 1; st.rerun()
            if col2.button("Skip Question"):
                st.session_state.skips += 1; st.session_state.index += 1; st.rerun()
            if col3.button("Submit & Next", type="primary"):
                if selected[0] == q[9]: st.session_state.score += 1
                st.session_state.index += 1; st.rerun()

        elif q[3] == "code":
            st.code(f"Expected Output: {q[6]}")
            code = st_ace(language="python", height=300, key=f"ace{i}", theme="monokai")
            col1, col2 = st.columns([1,1])
            if col1.button("Run Code"): st.code(run_code(q[0], code))
            if col2.button("Final Submit", type="primary"):
                if run_code(q[0], code).strip() == q[6].strip(): st.session_state.score += 1
                st.session_state.index += 1; st.rerun()

# ============================================================
# FINALIZE (FIXED: Full Cleanup)
# ============================================================

def finalize_exam(student_id, subject):
    # Step 1: Set flags to stop all monitoring
    st.session_state.exam_finished = True
    st.session_state.camera_started = False
    
    score, total = st.session_state.score, len(st.session_state.questions)
    percent = (score / total) * 100
    save_result(student_id, subject, score, total, percent, "Completed")
    increase_attempt(student_id, subject)
    
    st.balloons()
    st.success(f"Exam Completed! Score: {score}/{total}")
    show_result(student_id)
    
    if st.button("Exit Exam"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

def start_exam(student_id, subject):
    init_state()
    step = st.session_state.step
    if step == "fullscreen": fullscreen_step()
    elif step == "rules": rules_step()
    elif step == "camera": camera_step()
    elif step == "exam": exam_step(student_id, subject)