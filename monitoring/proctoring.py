import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import streamlit as st

# ============================================================
# 🚀 1. HIGH-PERFORMANCE MODEL LOADING
# ============================================================

@st.cache_resource
def load_proctoring_models():
    # Haar Cascade backup ke liye rakha hai, but YOLO primary use karenge
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # YOLOv8 Nano - Faces aur Objects dono ke liye best hai
    yolo_model = YOLO("yolov8n.pt") 
    return face_cascade, yolo_model

face_cascade, yolo_model = load_proctoring_models()

# ============================================================
# 🛠️ 2. ADVANCED IMAGE PROCESSING
# ============================================================

def process_frame_optimized(image):
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    # Standardize to BGR for OpenCV
    if len(image.shape) == 3 and image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    elif len(image.shape) == 3 and image.shape[-1] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Performance ke liye resize (640x480 standard)
    return cv2.resize(image, (640, 480)).astype(np.uint8)

# ============================================================
# 🔍 3. ENHANCED DETECTION SUITE (YOLO POWERED)
# ============================================================

def detect_camera_tampering(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    # Logic: Too dark or too blurry
    is_blocked = avg_brightness < 12 or variance < 8
    return is_blocked, avg_brightness

def analyze_with_yolo(frame):
    """
    Ek hi baar YOLO chalao persons aur objects dono ke liye (Saves CPU)
    COCO Classes: 0 = person, 67 = cell phone, 73 = book, 63 = laptop
    """
    results = yolo_model.predict(frame, imgsz=320, conf=0.4, verbose=False, device='cpu')
    
    persons = 0
    forbidden_items = []
    boxes_to_draw = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = yolo_model.names[cls]
            coords = box.xyxy[0].tolist() # [x1, y1, x2, y2]

            if label == 'person':
                persons += 1
                boxes_to_draw.append({'coords': coords, 'label': 'STUDENT'})
            elif label in ['cell phone', 'book', 'laptop', 'remote']:
                forbidden_items.append(label)
                boxes_to_draw.append({'coords': coords, 'label': label.upper()})
    
    return persons, list(set(forbidden_items)), boxes_to_draw

# ============================================================
# 🧠 4. CORE ENGINE
# ============================================================

def analyze_frame(image):
    if not hasattr(analyze_frame, "frame_count"):
        analyze_frame.frame_count = 0
    if not hasattr(analyze_frame, "cached_data"):
        analyze_frame.cached_data = {"risk": 0, "faces": 1, "objects": [], "warning": ""}

    try:
        frame = process_frame_optimized(image)
        h, w, _ = frame.shape
        analyze_frame.frame_count += 1

        # Tampering check har frame par (Fast)
        is_blocked, _ = detect_camera_tampering(frame)
        
        # Heavy Detection har 5th frame par (Smoothness Fix)
        if analyze_frame.frame_count % 5 == 0:
            num_faces, objects, visual_boxes = analyze_with_yolo(frame)
            
            risk = 0
            warning = ""
            status_color = (0, 255, 0) # Green

            if is_blocked:
                risk, warning, status_color = 100, "🚨 CAMERA BLOCKED", (0, 0, 255)
            elif num_faces == 0:
                risk, warning, status_color = 85, "🚨 NO FACE DETECTED", (0, 165, 255)
            elif num_faces > 1:
                risk, warning, status_color = 95, "🚨 MULTIPLE PERSONS", (0, 0, 255)
            elif len(objects) > 0:
                risk, warning, status_color = 90, f"🚨 FORBIDDEN: {objects[0].upper()}", (0, 0, 255)
            else:
                warning = "✅ Monitoring Active"

            analyze_frame.cached_data = {
                "risk": risk,
                "warning": warning,
                "faces": num_faces,
                "objects": objects,
                "is_blocked": is_blocked,
                "visual_boxes": visual_boxes,
                "color": status_color
            }

        # Visuals Draw Karna (Har frame par display refresh ke liye)
        data = analyze_frame.cached_data
        for box in data.get("visual_boxes", []):
            x1, y1, x2, y2 = map(int, box['coords'])
            cv2.rectangle(frame, (x1, y1), (x2, y2), data['color'], 2)
            cv2.putText(frame, box['label'], (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, data['color'], 2)

        if data['risk'] > 50:
            cv2.rectangle(frame, (0,0), (w, 40), (0,0,0), -1)
            cv2.putText(frame, data['warning'], (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

        return frame, data

    except Exception as e:
        return image, {"risk": 0, "warning": f"Error: {str(e)}", "faces": 1}