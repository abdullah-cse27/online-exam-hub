# ===================================================
# FILE: ai_features/cheating_detector.py
# ===================================================

import cv2
import mediapipe as mp

# Initialize mediapipe
mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

# ===================================================
# FACE DETECTION
# ===================================================

def detect_faces(frame):

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_detector.process(rgb)

    faces = []

    if results.detections:

        for det in results.detections:

            bbox = det.location_data.relative_bounding_box

            faces.append(bbox)

    return faces


# ===================================================
# CHEATING ANALYSIS
# ===================================================

def analyze_frame(frame):

    faces = detect_faces(frame)

    warning = None

    if len(faces) == 0:

        warning = "No face detected"

    elif len(faces) > 1:

        warning = "Multiple faces detected"

    return {
        "faces": len(faces),
        "warning": warning
    }


# ===================================================
# OBJECT PLACEHOLDER
# ===================================================

def detect_objects(frame):

    """
    Placeholder for object detection.
    Future:
    detect phone / book / person.
    """

    return []


# ===================================================
# HEAD MOVEMENT CHECK
# ===================================================

def detect_suspicious_movement(previous_frame, current_frame):

    if previous_frame is None:
        return False

    diff = cv2.absdiff(previous_frame, current_frame)

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    movement = gray.mean()

    if movement > 25:

        return True

    return False


# ===================================================
# CHEATING SCORE
# ===================================================

def calculate_cheating_score(events):

    score = 0

    for e in events:

        if e == "no_face":
            score += 2

        elif e == "multiple_faces":
            score += 5

        elif e == "movement":
            score += 1

    return score