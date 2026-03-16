# ===================================================
# FILE: email_service.py (FIXED VERSION)
# ===================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import time


# ======================
# GMAIL SMTP CONFIG
# ======================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "shahabdulla09856@gmail.com"

# Gmail APP PASSWORD (not normal password)
APP_PASSWORD = "bjtmezddoyxwfuql"


# ======================
# OTP GENERATOR
# ======================

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


# ======================
# UNIVERSAL EMAIL SENDER
# ======================

def send_email(receiver_email, subject, body, html_body=None):

    msg = MIMEMultipart("alternative")

    msg["From"] = f"Online Examination System <{SENDER_EMAIL}>"
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if html_body:
        msg.attach(MIMEText(html_body, "html"))

    attempts = 3

    for attempt in range(attempts):

        try:

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)

            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(SENDER_EMAIL, APP_PASSWORD)

            server.sendmail(
                SENDER_EMAIL,
                receiver_email,
                msg.as_string()
            )

            server.quit()

            print("Email sent successfully →", receiver_email)

            return True

        except Exception as e:

            print("EMAIL ERROR:", e)

            time.sleep(2)

    return False


# ======================
# OTP EMAIL
# ======================

def send_otp_email(receiver_email, otp):

    subject = "Online Examination System - OTP Verification"

    body = f"""
Hello,

Your OTP for password reset is:

{otp}

This OTP is valid for 5 minutes.

Do NOT share this OTP with anyone.

Regards  
Online Examination System
"""

    html = f"""
<h3>Online Examination System</h3>
<p>Your OTP for password reset is:</p>
<h2>{otp}</h2>
<p>This OTP is valid for <b>5 minutes</b>.</p>
"""

    return send_email(receiver_email, subject, body, html)


# ======================
# PASSWORD EMAIL
# ======================

def send_password_email(receiver_email, password):

    subject = "Your Online Examination System Password"

    body = f"""
Hello Student,

Your login password is:

{password}

Use your Roll Number + this password to login.

Please change your password after login.

Regards  
Online Examination System
"""

    html = f"""
<h3>Online Examination System</h3>
<p>Your login password is:</p>
<h2>{password}</h2>
<p>Please change your password after login.</p>
"""

    return send_email(receiver_email, subject, body, html)


# ======================
# ACCOUNT CREATED EMAIL
# ======================

def send_account_created_email(receiver_email, roll):

    subject = "Account Created - Online Examination System"

    body = f"""
Hello,

Your student account has been created.

Roll Number: {roll}

You can now login to the examination system.

Regards  
Online Examination System
"""

    return send_email(receiver_email, subject, body)


# ======================
# EXAM NOTIFICATION EMAIL
# ======================

def send_exam_notification(receiver_email, subject):

    subject_line = "New Exam Available"

    body = f"""
Hello,

A new exam is available for subject:

{subject}

Login to the system and start your exam.

Good Luck!

Online Examination System
"""

    return send_email(receiver_email, subject_line, body)


# ======================
# TEST
# ======================

if __name__ == "__main__":

    test_email = "your_test_email@gmail.com"

    otp = generate_otp()

    if send_otp_email(test_email, otp):

        print("OTP email sent successfully")

    else:

        print("Failed to send OTP email")