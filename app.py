from flask import Flask, render_template, Response, jsonify, request
import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import threading
import time
import base64
from PIL import ImageFont, ImageDraw, Image
import os
import json

app = Flask(__name__)

# Global variables
camera = None
is_running = False
detector = None
classifier = None
labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'o', 'a', 'i', 'u', 'e', 'oo', 'k', 'kh', 'g', 'gh', 'c', 'ch', 'j', 'jh', 't', 'th', 'd', 'dh', 'to', 'tho', 'do', 'dho', 'n', 'p', 'f', 'b', 'v', 'm', 'y', 'r', 's', 'h', 'rh', 'ng', 'bisrg']
bn_sign = {
  "0": "০",
  "1": "১",
  "2": "২",
  "3": "৩",
  "4": "৪",
  "5": "৫",
  "6": "৬",
  "7": "৭",
  "8": "৮",
  "9": "৯",
  "o": "অ",
  "a": "আ",
  "i": "ই",
  "e": "এ",
  "u": "উ",
  "oo": "ও",
  "b": "ব",
  "bisrg": "বিসর্গ",
  "c": "চ",
  "ch": "ছ",
  "d": "ড",
  "dh": "ঢ",
  "dho": "ধ",
  "do": "দ",
  "f": "ফ",
  "g": "গ",
  "gh": "ঘ",
  "h": "হ",
  "j": "জ",
  "jh": "ঝ",
  "k": "ক",
  "kh": "খ",
  "m": "ম",
  "n": "ন",
  "ng": "অনুস্বার",
  "p": "প",
  "r": "র",
  "rh": "ড়",
  "s": "স",
  "t": "ট",
  "th": "ঠ",
  "tho": "থ",
  "to": "ত",
  "v": "ভ",
  "y": "য়"
}
current_prediction = ""
current_english_label = ""
frame_buffer = None
lock = threading.Lock()

# Load sign images data
def load_sign_data():
    try:
        with open('static/data/sign_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create a default structure if file doesn't exist or is invalid
        sign_data = {}
        for label in labels:
            sign_data[label] = {
                "bangla": bn_sign.get(label, label),
                "image": f"../static/images/signs/Image_{label}.jpg",
                "description": f"Sign for {bn_sign.get(label, label)}"
            }
        
        # Create directory if it doesn't exist
        os.makedirs('static/data', exist_ok=True)
        
        # Save the default data
        with open('static/data/sign_data.json', 'w', encoding='utf-8') as f:
            json.dump(sign_data, f, ensure_ascii=False, indent=2)
        
        return sign_data

sign_data = load_sign_data()

def put_bangla_text(cv_img, text, position, font_path='fonts/SolaimanLipi_22-02-2012.ttf', font_size=32, color=(0, 255, 0)):
    # Convert OpenCV image (BGR) to PIL image (RGB)
    pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

    # Load Bangla font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        # Fallback to default font if Bangla font is not available
        cv2.putText(cv_img, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        return cv_img

    # Draw text on image
    draw = ImageDraw.Draw(pil_img)
    draw.text(position, text, font=font, fill=color)

    # Convert back to OpenCV image (RGB to BGR)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def initialize_camera():
    global camera, detector, classifier
    try:
        # Try to release any existing camera first
        if camera is not None:
            camera.release()
        
        # Initialize the camera with a specific backend
        camera = cv2.VideoCapture(0, cv2.CAP_ANY)
        
        # Set camera properties for better performance
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        # Check if camera opened successfully
        if not camera.isOpened():
            print("Error: Could not open camera.")
            return False
            
        detector = HandDetector(maxHands=2)
        classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")
        return True
    except Exception as e:
        print(f"Camera initialization error: {str(e)}")
        return False

def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None

def process_frames():
    global is_running, camera, detector, classifier, current_prediction, current_english_label, frame_buffer
    
    imgSize = 300
    
    while is_running:
        success, img = camera.read()
        if not success:
            time.sleep(0.1)
            continue

        # Flip image for mirror effect
        img = cv2.flip(img, 1)
        
        # Create a copy for processing
        img_display = img.copy()

        # Detect hands
        hands, img_display = detector.findHands(img_display)

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
        imgCrop = None

        if hands:
            if len(hands) == 1:
                hand = hands[0]
                x, y, w, h = hand['bbox']
                padding = 20
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(img.shape[1], x + w + padding)
                y2 = min(img.shape[0], y + h + padding)

                if x2 > x1 and y2 > y1:
                    imgCrop = img[y1:y2, x1:x2]

            elif len(hands) == 2:
                # Get bounding boxes for both hands
                hand1 = hands[0]
                hand2 = hands[1]
                x1_h1, y1_h1, w1_h1, h1_h1 = hand1['bbox']
                x1_h2, y1_h2, w1_h2, h1_h2 = hand2['bbox']

                # Calculate the combined bounding box with some extra padding
                padding = 20
                x_min = max(0, min(x1_h1, x1_h2) - padding)
                y_min = max(0, min(y1_h1, y1_h2) - padding)
                x_max = min(img.shape[1], max(x1_h1 + w1_h1, x1_h2 + w1_h2) + padding)
                y_max = min(img.shape[0], max(y1_h1 + h1_h1, y1_h2 + h1_h2) + padding)

                if x_max > x_min and y_max > y_min:
                    imgCrop = img[y_min:y_max, x_min:x_max]

            if imgCrop is not None:
                crop_h, crop_w = imgCrop.shape[:2]
                aspect_ratio = crop_h / crop_w

                if aspect_ratio > 1:
                    k = imgSize / crop_h
                    new_w = int(k * crop_w)
                    resized = cv2.resize(imgCrop, (new_w, imgSize))
                    w_gap = (imgSize - new_w) // 2
                    imgWhite[:, w_gap:w_gap + new_w] = resized
                else:
                    k = imgSize / crop_w
                    new_h = int(k * crop_h)
                    resized = cv2.resize(imgCrop, (imgSize, new_h))
                    h_gap = (imgSize - new_h) // 2
                    imgWhite[h_gap:h_gap + new_h, :] = resized

                prediction, index = classifier.getPrediction(imgWhite, draw=False)
                predicted_label = labels[index]
                bangla_label = bn_sign.get(predicted_label, predicted_label)
                current_prediction = bangla_label
                current_english_label = predicted_label

                # Modern overlay with predicted label
                if hands:
                    # Use the bounding box of the first detected hand for single hand,
                    # or the combined bounding box for two hands
                    if len(hands) == 1:
                        x_overlay, y_overlay, w_overlay, h_overlay = hands[0]['bbox']
                    else:
                        x_overlay, y_overlay = x_min, y_min
                        w_overlay, h_overlay = x_max - x_min, y_max - y_min

                    cv2.rectangle(img_display, (x_overlay - 20, y_overlay - 60), 
                                 (x_overlay + w_overlay + 20, y_overlay - 10), (0, 0, 0), cv2.FILLED)
                    try:
                        img_display = put_bangla_text(img_display, bangla_label, (x_overlay, y_overlay - 50))
                    except Exception as e:
                        # Fallback to English if Bangla rendering fails
                        cv2.putText(img_display, f'{predicted_label}', (x_overlay, y_overlay - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        # Draw main UI frame
        cv2.rectangle(img_display, (0, 0), (640, 40), (50, 50, 50), cv2.FILLED)
        cv2.putText(img_display, "   Bangla Sign Recognition", (10, 30),
                    cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)

        # Convert to JPEG
        ret, buffer = cv2.imencode('.jpg', img_display)
        if ret:
            with lock:
                frame_buffer = buffer.tobytes()
        
        time.sleep(0.03)  # ~30 FPS

def generate_frames():
    global frame_buffer, lock
    while True:
        with lock:
            if frame_buffer is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
            else:
                # Return a blank frame if no frame is available
                blank = np.ones((480, 640, 3), np.uint8) * 255
                cv2.putText(blank, "Camera not started", (150, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                _, buffer = cv2.imencode('.jpg', blank)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.03)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign')
def sign_page():
    return render_template('sign.html', signs=sign_data)

@app.route('/learn')
def learn_page():
    return render_template('learn.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start', methods=['POST'])
def start():
    global is_running
    if not is_running:
        if initialize_camera():
            is_running = True
            threading.Thread(target=process_frames, daemon=True).start()
            return jsonify({"status": "success", "message": "Camera started"})
        else:
            return jsonify({"status": "error", "message": "Failed to open camera"})
    return jsonify({"status": "success", "message": "Camera already running"})

@app.route('/stop', methods=['POST'])
def stop():
    global is_running
    is_running = False
    release_camera()
    return jsonify({"status": "success", "message": "Camera stopped"})

@app.route('/get_prediction')
def get_prediction():
    global current_prediction, current_english_label
    sign_image = ""
    if current_english_label in sign_data:
        sign_image = sign_data[current_english_label]["image"]
    return jsonify({
        "prediction": current_prediction,
        "english_label": current_english_label,
        "sign_image": sign_image
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/images/signs', exist_ok=True)
    os.makedirs('static/data', exist_ok=True)
    
    app.run(host='0.0.0.0', debug=True, threaded=True)
