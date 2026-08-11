import os
import json
import cv2
import time
from flask import Flask, render_template, send_from_directory, Response
from ultralytics import YOLO

app = Flask(__name__)

# Load basic YOLOv8 model for the demo
model = YOLO('yolov8n.pt')

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

# Video streaming generator function
def generate_frames(video_name):
    video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_videos', video_name)
    if not os.path.exists(video_path):
        video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_videos', 'wrong_way_drone1.mp4')
        
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
            
        # Run YOLO detection/tracking
        results = model.track(frame, persist=True, verbose=False)
        annotated_frame = results[0].plot()
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        
        # Yield in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
        # Simulate real-time delay
        time.sleep(0.03)

from flask import request

@app.route('/video_feed')
def video_feed():
    video_name = request.args.get('video', 'wrong_way_drone1.mp4')
    # Basic security check
    video_name = os.path.basename(video_name) 
    return Response(generate_frames(video_name), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/events')
def get_events():
    events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'outputs', 'live_events.json')
    try:
        if os.path.exists(events_path):
            with open(events_path, 'r') as f:
                data = json.load(f)
                return data
        return {}
    except Exception as e:
        return {}

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, port=5000)
