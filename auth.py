import streamlit as st
from database import (
    get_user_by_roll,
    create_user,
    update_user,
    validate_user
)
from email_service import send_password_email, send_otp_email
import random, string, time


# ====================================
# PASSWORD GENERATOR
# ====================================

def generate_password():

    chars = string.ascii_letters + string.digits

    return "".join(random.choice(chars) for _ in range(8))


# ====================================
# LOGIN USER
# ====================================

def login_user():

    # Initialize session states safely
    defaults = {
        "flow": None,
        "otp": None,
        "otp_time": None,
        "otp_verified": False,
        "temp_roll": None,
        "login_attempts": 0
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


    st.subheader("🔐 Login")

    role = st.selectbox("Select Role", ["student", "admin"])

    roll = st.text_input("Roll Number / Admin ID")

    if roll == "":
        return


# =========================================================
# ADMIN LOGIN
# =========================================================

    if role == "admin":

        admin_pass = st.text_input("Admin Password", type="password")

        if st.button("Login as Admin"):

            user = get_user_by_roll(roll)

            if user and user["role"] == "admin" and validate_user(roll, admin_pass):

                st.success("Admin Login Successful!")

                st.session_state.logged_in = True
                st.session_state.userid = roll
                st.session_state.role = "admin"
                st.session_state.login_time = time.time()
                st.session_state.page = "Admin Panel"

                st.rerun()

            else:

                st.error("Incorrect Admin Credentials!")

        return


# =========================================================
# STUDENT LOGIN FLOW
# =========================================================

    user = get_user_by_roll(roll)

    st.session_state.temp_roll = roll


# ---------------------------------------------------------
# STUDENT NOT REGISTERED
# ---------------------------------------------------------

    if user is None:

        st.info("This Roll Number is not registered.")

        email = st.text_input("Enter Email to Create Account")

        if st.button("Submit Email"):

            if email == "":
                st.error("Email required")
                return

            with st.spinner("Creating account & sending password..."):

                # FIXED: Added required email and password placeholders
                create_user(roll, email="", password="", role="student")

                update_user(roll, email=email)

                new_pass = generate_password()

                update_user(roll, password=new_pass)

                send_password_email(email, new_pass)

            st.success("Account created! Password sent to your email.")

            st.session_state.flow = "ask_password"

            st.rerun()

        return


# ---------------------------------------------------------
# EMAIL NOT SET
# ---------------------------------------------------------

    if user["email"] == "":

        st.warning("Your email is not set. Enter email.")

        email = st.text_input("Enter Email")

        if st.button("Save Email"):

            with st.spinner("Sending password..."):

                update_user(roll, email=email)

                new_pass = generate_password()

                update_user(roll, password=new_pass)

                send_password_email(email, new_pass)

            st.success("Password sent! Login again.")

            st.session_state.flow = "ask_password"

            st.rerun()

        return


# ---------------------------------------------------------
# PASSWORD MISSING
# ---------------------------------------------------------

    if user["password"] == "":

        with st.spinner("Sending new password..."):

            new_pass = generate_password()

            update_user(roll, password=new_pass)

            send_password_email(user["email"], new_pass)

        st.success("New Password sent! Login again.")

        st.session_state.flow = "ask_password"

        st.rerun()

        return


# =========================================================
# OTP RESET FLOW
# =========================================================

    if st.session_state.flow == "otp_stage":

        st.subheader("🔑 OTP Verification")

        entered_otp = st.text_input("Enter OTP")

        if st.button("Verify OTP"):

            if time.time() - st.session_state.otp_time > 300:

                st.error("OTP expired. Request again.")

                st.session_state.flow = None

                return

            if entered_otp == st.session_state.otp:

                st.success("OTP verified! Set new password.")

                st.session_state.otp_verified = True

                st.rerun()

            else:

                st.error("Incorrect OTP!")


        if st.session_state.otp_verified:

            new_pass = st.text_input("New Password", type="password")

            confirm_pass = st.text_input("Confirm Password", type="password")

            if st.button("Update Password"):

                if len(new_pass) < 6:

                    st.error("Password must be at least 6 characters")

                    return

                if new_pass == confirm_pass:

                    update_user(roll, password=new_pass)

                    st.success("Password updated! Login again.")

                    st.session_state.flow = None
                    st.session_state.otp_verified = False
                    st.session_state.otp = None

                    st.rerun()

                else:

                    st.error("Passwords do not match!")

        return


# =========================================================
# NORMAL LOGIN
# =========================================================

    st.subheader("Enter Your Password")

    password = st.text_input("Password", type="password")


    if st.button("Forgot Password?"):

        otp = str(random.randint(100000, 999999))

        st.session_state.otp = otp
        st.session_state.otp_time = time.time()

        with st.spinner("Sending OTP..."):

            send_otp_email(user["email"], otp)

        st.success("OTP sent to your email!")

        st.session_state.flow = "otp_stage"

        st.rerun()


    if st.button("Login"):

        if st.session_state.login_attempts >= 5:

            st.error("Too many login attempts. Try later.")

            return

        if validate_user(roll, password):

            st.success("Login Successful!")

            st.session_state.logged_in = True
            st.session_state.userid = roll
            st.session_state.role = "student"
            st.session_state.login_time = time.time()
            st.session_state.page = "Student Panel"

            # reset states
            st.session_state.flow = None
            st.session_state.otp = None
            st.session_state.otp_verified = False
            st.session_state.login_attempts = 0

            st.rerun()

        else:

            st.session_state.login_attempts += 1

            st.error("Incorrect Password!")