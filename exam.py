# ============================================================
# FILE: exam.py (UPDATED FINAL VERSION)
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
        "step":"fullscreen",
        "index":0,
        "score":0,
        "questions":[],
        "answers":{}
    }

    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v


# ============================================================
# SECURITY SCRIPT
# ============================================================
def security_script():

    components.html("""
    <script>

    if(!window.examSecurityLoaded){

        window.examSecurityLoaded = true;

        const parentWindow = window.parent;
        const parentDoc = parentWindow.document;

        let overlay = null;
        let countdownTimer = null;

        function showWarning(){

            if(overlay) return;

            let t = 15;

            overlay = parentDoc.createElement("div");

            overlay.style.position="fixed";
            overlay.style.top="0";
            overlay.style.left="0";
            overlay.style.width="100%";
            overlay.style.height="100%";
            overlay.style.background="rgba(0,0,0,0.9)";
            overlay.style.display="flex";
            overlay.style.flexDirection="column";
            overlay.style.alignItems="center";
            overlay.style.justifyContent="center";
            overlay.style.color="white";
            overlay.style.fontSize="50px";
            overlay.style.zIndex="999999";

            const text = parentDoc.createElement("div");

            const btn = parentDoc.createElement("button");
            btn.innerText="Cancel";
            btn.style.marginTop="20px";
            btn.style.padding="15px";
            btn.style.fontSize="20px";

            btn.onclick=function(){
                clearInterval(countdownTimer);
                overlay.remove();
                overlay=null;
            };

            overlay.appendChild(text);
            overlay.appendChild(btn);

            parentDoc.body.appendChild(overlay);

            countdownTimer = setInterval(function(){

                text.innerHTML="Tab switch detected! Return in "+t+" sec";

                t--;

                if(t<0){

                    clearInterval(countdownTimer);

                    alert("Exam terminated due to tab switching");

                    parentWindow.location.reload();
                }

            },1000);
        }

        // REAL TAB SWITCH DETECTION
        parentDoc.addEventListener("visibilitychange", function(){

            if(parentDoc.hidden){
                showWarning();
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
        st.session_state.step="camera"
        st.rerun()


# ============================================================
# CAMERA STEP
# ============================================================

def camera_step():

    st.title("Camera Verification")

    cam=st.camera_input("Capture your face")

    if cam:

        img=Image.open(cam)
        img=np.array(img)

        result=analyze_frame(img)

        if result["warning"]:
            st.error(result["warning"])

        else:

            st.success("Face verified successfully")

            if st.button("Proceed to Exam"):
                st.session_state.step="exam"
                st.rerun()


# ============================================================
# LOAD QUESTIONS
# ============================================================

def prepare_questions(subject):

    qs=get_all_questions()

    mcq=[q for q in qs if q[0]==subject and q[3]=="mcq"]
    code=[q for q in qs if q[0]==subject and q[3]=="code"]

    random.shuffle(mcq)
    random.shuffle(code)

    return mcq[:10]+code[:5]


# ============================================================
# TIMER
# ============================================================
def js_timer(limit,qid):

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

    // Reset timer for new question
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

                const popup = document.createElement("div");

                popup.style.position="fixed";
                popup.style.bottom="20px";
                popup.style.right="20px";
                popup.style.background="orange";
                popup.style.padding="15px";
                popup.style.fontSize="18px";
                popup.style.borderRadius="10px";
                popup.style.zIndex="999999";

                popup.innerHTML="Time up for this question";

                document.body.appendChild(popup);

                setTimeout(()=>{{

                    popup.remove();

                    const buttons = window.parent.document.querySelectorAll("button");

                    buttons.forEach(btn=>{{
                        if(btn.innerText==="Skip"){{
                            btn.click();
                        }}
                    }});

                }},1500);

            }}
        }}

        updateTimer();

        window.examTimer = setInterval(updateTimer,1000);

    }}

    </script>
    """, height=90)

# ============================================================
# EXAM STEP
# ============================================================

def exam_step(student_id,subject):

    security_script()

    if not st.session_state.questions:
        st.session_state.questions=prepare_questions(subject)

    qs=st.session_state.questions
    i=st.session_state.index

    if i>=len(qs):
        finalize_exam(student_id,subject)
        return

    q=qs[i]

    st.progress((i+1)/len(qs))

    limit=20 if q[3]=="mcq" else 180
    js_timer(limit,i)

    st.markdown(f"### Question {i+1}")
    st.write(q[4])

# ============================================================
# MCQ
# ============================================================

    if q[3]=="mcq":

        options={
            "A":q[5],
            "B":q[6],
            "C":q[7],
            "D":q[8]
        }

        selected=st.radio(
            "Choose Answer",
            [f"{k}) {v}" for k,v in options.items()],
            key=f"mcq{i}"
        )

        col1,col2,col3=st.columns(3)

        if col1.button("Previous"):

            if i>0:
                st.session_state.index-=1
                st.rerun()

        if col2.button("Skip"):

            st.session_state.index+=1
            st.rerun()

        if col3.button("Submit"):

            st.session_state.answers[i]=selected.split(")")[0]

            if selected.split(")")[0]==q[9]:
                st.session_state.score+=1

            st.session_state.index+=1
            st.rerun()


# ============================================================
# CODING
# ============================================================

    elif q[3]=="code":

        st.code(q[6])

        code=st_ace(language="python",height=300)

        if st.button("Run Code"):

            output=run_python_code(code)
            st.code(output)

        col1,col2,col3=st.columns(3)

        if col1.button("Previous"):

            if i>0:
                st.session_state.index-=1
                st.rerun()

        if col2.button("Skip"):

            st.session_state.index+=1
            st.rerun()

        if col3.button("Submit Code"):

            result=run_python_code(code)

            if result.strip()==q[6].strip():
                st.session_state.score+=1

            st.session_state.index+=1
            st.rerun()


# ============================================================
# RESULT
# ============================================================

def finalize_exam(student_id,subject):

    score=st.session_state.score
    total=len(st.session_state.questions)

    percent=(score/total)*100

    save_result(student_id,subject,score,total,percent,"Completed")
    increase_attempt(student_id,subject)

    st.success("Exam Completed")

    st.write("Score:",score,"/",total)
    st.write("Percentage:",percent)

    show_result(student_id)


# ============================================================
# ENTRY
# ============================================================

def start_exam(student_id,subject):

    init_state()

    step=st.session_state.step

    if step=="fullscreen":
        fullscreen_step()

    elif step=="camera":
        camera_step()

    elif step=="exam":
        exam_step(student_id,subject)