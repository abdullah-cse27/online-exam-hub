# ============================================================
# FILE: monitoring/proctoring.py (FIXED VERSION)
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


# ============================================================
# IMAGE FORMAT NORMALIZATION
# ============================================================

def normalize_image(image):
    """
    Convert different image formats into OpenCV compatible format
    """

    # PIL → numpy
    if isinstance(image, Image.Image):
        image = np.array(image)

    # ensure numpy
    image = np.array(image)

    # RGB → BGR (OpenCV format)
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image


# ============================================================
# FACE DETECTION
# ============================================================

def detect_faces(image):

    img = normalize_image(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30,30)
    )

    return faces


# ============================================================
# PROCTORING ANALYSIS
# ============================================================

def analyze_frame(image):

    faces = detect_faces(image)

    result = {
        "face_count": len(faces),
        "warning": None
    }

    if len(faces) == 0:
        result["warning"] = "⚠ No face detected"

    elif len(faces) > 1:
        result["warning"] = "⚠ Multiple faces detected"

    else:
        result["warning"] = None

    return result