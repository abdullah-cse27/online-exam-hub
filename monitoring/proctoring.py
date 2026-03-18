# ============================================================
# FILE: monitoring/proctoring.py (STABLE AI PROCTORING ENGINE)
# ============================================================

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

# ============================================================
# LOAD MODELS
# ============================================================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

yolo_model = YOLO("yolov8n.pt")

previous_frame = None
frame_counter = 0


# ============================================================
# NORMALIZE IMAGE
# ============================================================

def normalize_image(image):

    if isinstance(image, Image.Image):
        image = np.array(image)

    image = np.array(image)

    # ensure correct type
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    return image


# ============================================================
# FACE DETECTION (IMPROVED)
# ============================================================

def detect_faces(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.equalizeHist(gray)

    small = cv2.resize(gray, (0,0), fx=0.75, fy=0.75)

    faces = face_cascade.detectMultiScale(
        small,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40,40)
    )

    faces_rescaled = []
    for (x,y,w,h) in faces:
        faces_rescaled.append((
            int(x/0.75),
            int(y/0.75),
            int(w/0.75),
            int(h/0.75)
        ))

    return faces_rescaled


# ============================================================
# MOTION DETECTION
# ============================================================

def detect_motion(frame):

    global previous_frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21),0)

    if previous_frame is None:
        previous_frame = gray
        return False

    diff = cv2.absdiff(previous_frame, gray)

    thresh = cv2.threshold(diff,25,255,cv2.THRESH_BINARY)[1]

    motion_score = np.sum(thresh)/255

    previous_frame = gray

    return motion_score > 12000


# ============================================================
# LIGHT CHECK
# ============================================================

def detect_low_light(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    brightness = np.mean(gray)

    return brightness < 40


# ============================================================
# YOLO OBJECT DETECTION (THROTTLED)
# ============================================================

def detect_objects(frame):

    objects = []

    small = cv2.resize(frame,(640,480))
    results = yolo_model(small, verbose=False)

    for r in results:

        for box in r.boxes:

            cls = int(box.cls)
            label = yolo_model.names[cls]

            if label in ["cell phone","book","laptop"]:
                objects.append(label)

    return objects


# ============================================================
# LOOKING DETECTION
# ============================================================

def detect_looking(faces, frame_width):

    if len(faces) == 0:
        return True

    x,y,w,h = faces[0]

    center = x + w/2

    if center < frame_width*0.35 or center > frame_width*0.65:
        return False

    return True


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk(face_count,motion,low_light,objects,looking):

    score = 0

    if face_count == 0:
        score += 40

    elif face_count > 1:
        score += 60

    if not looking:
        score += 20

    if motion:
        score += 15

    if low_light:
        score += 10

    if len(objects) > 0:
        score += 40

    return min(score,100)


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_frame(image):

    global frame_counter

    try:

        frame = normalize_image(image)

        faces = detect_faces(frame)

        motion = detect_motion(frame)

        low_light = detect_low_light(frame)

        frame_counter += 1

        objects = []

        if frame_counter % 45 == 0:
            objects = detect_objects(frame)

        looking = detect_looking(faces, frame.shape[1])

        risk = calculate_risk(
            len(faces),
            motion,
            low_light,
            objects,
            looking
        )

        warning = ""

        if len(faces) == 0:
            warning = "⚠ Face not visible"

        elif len(faces) > 1:
            warning = "⚠ Multiple faces detected"

        elif not looking:
            warning = "⚠ Look at the screen"

        elif low_light:
            warning = "⚠ Lighting too low"

        elif motion:
            warning = "⚠ Suspicious movement detected"

        elif len(objects) > 0:
            warning = f"⚠ Object detected: {objects[0]}"


        # draw face boxes
        for (x,y,w,h) in faces:

            cv2.rectangle(
                frame,
                (x,y),
                (x+w,y+h),
                (0,255,0),
                2
            )

        data = {
            "faces": len(faces),
            "looking": looking,
            "motion": motion,
            "low_light": low_light,
            "objects": objects,
            "risk": risk,
            "warning": warning
        }

        return frame,data

    except Exception:

        return image,{
            "faces":0,
            "looking":True,
            "motion":False,
            "low_light":False,
            "objects":[],
            "risk":0,
            "warning":""
        }