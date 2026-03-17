# ============================================================
# FILE: monitoring/proctoring.py (AI PROCTORING ENGINE)
# ============================================================

import cv2
import numpy as np
from PIL import Image

# ============================================================
# LOAD FACE DETECTOR
# ============================================================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

previous_frame = None


# ============================================================
# NORMALIZE IMAGE
# ============================================================

def normalize_image(image):

    if isinstance(image, Image.Image):
        image = np.array(image)

    image = np.array(image)

    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image


# ============================================================
# FACE DETECTION
# ============================================================

def detect_faces(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )

    return faces


# ============================================================
# MOTION DETECTION
# ============================================================

def detect_motion(frame):

    global previous_frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if previous_frame is None:
        previous_frame = gray
        return False

    diff = cv2.absdiff(previous_frame, gray)

    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]

    motion_score = np.sum(thresh) / 255

    previous_frame = gray

    if motion_score > 40000:
        return True

    return False


# ============================================================
# LIGHT CHECK
# ============================================================

def detect_low_light(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    brightness = np.mean(gray)

    if brightness < 40:
        return True

    return False


# ============================================================
# OBJECT DETECTION (placeholder)
# ============================================================

def detect_objects(frame):

    """
    Future Expansion:
    - phone detection
    - book detection
    - second person detection
    """

    return []


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk(face_count, motion, low_light, objects):

    score = 0

    if face_count == 0:
        score += 40

    elif face_count > 1:
        score += 60

    if motion:
        score += 20

    if low_light:
        score += 15

    if len(objects) > 0:
        score += 40

    if score > 100:
        score = 100

    return score


# ============================================================
# RISK LEVEL
# ============================================================

def risk_level(score):

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    else:
        return "LOW"


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_frame(image):

    frame = normalize_image(image)

    faces = detect_faces(frame)

    motion = detect_motion(frame)

    low_light = detect_low_light(frame)

    objects = detect_objects(frame)

    risk = calculate_risk(len(faces), motion, low_light, objects)

    level = risk_level(risk)

    result = {

        "face_count": len(faces),
        "motion_detected": motion,
        "low_light": low_light,
        "objects": objects,

        "risk_score": risk,
        "risk_level": level,

        "warning": None
    }

    # ====================================
    # WARNINGS
    # ====================================

    if len(faces) == 0:
        result["warning"] = "⚠ No face detected"

    elif len(faces) > 1:
        result["warning"] = "⚠ Multiple faces detected"

    elif low_light:
        result["warning"] = "⚠ Lighting too low"

    elif motion:
        result["warning"] = "⚠ Suspicious movement detected"

    elif len(objects) > 0:
        result["warning"] = "⚠ Suspicious object detected"

    return result