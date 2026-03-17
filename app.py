# =========================================================
# FILE: app.py
# =========================================================

import streamlit as st
import time
from auth import login_user
from admin import admin_panel
from student import student_panel


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Online Examination System",
    page_icon="🧠",
    layout="wide"
)


# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

defaults = {
    "logged_in": False,
    "role": None,
    "userid": None,
    "page": "Login",
    "theme": "Light Mode",
    "last_activity": time.time()
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# AUTO LOGOUT (30 min inactivity)
# =========================================================

if st.session_state.logged_in:

    now = time.time()

    if now - st.session_state.last_activity > 1800:

        st.warning("Session expired. Please login again.")

        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.userid = None
        st.session_state.page = "Login"

        st.rerun()

    st.session_state.last_activity = now


# =========================================================
# THEME SWITCH
# =========================================================

theme_choice = st.sidebar.radio(
    "🎨 Theme",
    ["Light Mode", "Dark Mode"]
)

st.session_state.theme = theme_choice


# =========================================================
# LIGHT MODE CSS
# =========================================================

if st.session_state.theme == "Light Mode":

    st.markdown("""
    <style>

    .stApp{
        background:#f9f9f9;
        color:#222;
    }

    .big-title{
        text-align:center;
        font-size:46px;
        font-weight:800;
        color:#2E7D32;
        padding:10px;
    }

    .stButton>button{
        background:#e6e6e6;
        color:#222;
        border-radius:8px;
        padding:8px 20px;
    }

    .stButton>button:hover{
        background:#d4d4d4;
    }

    </style>
    """, unsafe_allow_html=True)


# =========================================================
# DARK MODE CSS
# =========================================================

else:

    st.markdown("""
    <style>

    .stApp{
        background:#0b0b0b;
        color:#e6e6e6;
    }

    .big-title{
        text-align:center;
        font-size:46px;
        font-weight:800;
        color:#5cd4ff;
        padding:10px;
    }

    .stButton>button{
        background:#272727;
        color:white;
        border-radius:8px;
        padding:8px 20px;
    }

    .stButton>button:hover{
        background:#3d3d3d;
    }

    </style>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN TITLE
# =========================================================

st.markdown(
    "<p class='big-title'>🧠 Online Examination System</p>",
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR USER INFO
# =========================================================

if st.session_state.logged_in:

    st.sidebar.success(
        f"Logged in as {st.session_state.role}\n\nID: {st.session_state.userid}"
    )

    if st.sidebar.button("Logout"):

        for k in list(st.session_state.keys()):
            del st.session_state[k]

        st.rerun()


# =========================================================
# NAVIGATION
# =========================================================


menu = ["Login", "Admin Panel", "Student Panel"]

if st.session_state.logged_in:

    if st.session_state.role == "admin":
        default_page = "Admin Panel"
    else:
        default_page = "Student Panel"

else:
    default_page = "Login"


choice = st.sidebar.radio(
    "Navigation",
    menu,
    index=menu.index(default_page)
)

st.session_state.page = choice


# =========================================================
# PAGE ROUTING
# =========================================================

if choice == "Login":

    login_user()


elif choice == "Admin Panel":

    if st.session_state.logged_in and st.session_state.role == "admin":

        admin_panel()

    else:

        st.warning("Please login as Admin!")


elif choice == "Student Panel":

    if st.session_state.logged_in and st.session_state.role == "student":

        student_panel()

    else:

        st.warning("Please login as Student!")


# =========================================================
# FOOTER
# =========================================================

st.markdown(
"""
<hr>
<center>

Online Examination System v1.0  
Developed with ❤️ using Streamlit

</center>
""",
unsafe_allow_html=True
)