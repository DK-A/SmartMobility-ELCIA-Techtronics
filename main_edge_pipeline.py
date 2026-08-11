import cv2
import json
import time
import os
from vision.detection.yolov8_detector import YOLOv8Detector
from radar_dsp.fft.velocity_extractor import VelocityExtractor
from fusion.sensor_fusion import FusionEngine
from incident_logic.wrong_way_detector import IncidentLogic
from lora.payload_manager import LoRaWANTransmitter

def main():
    video_path = "test_videos/wrong_way_drone1.mp4"
    if not os.path.exists(video_path):
        print(f"Error: {video_path} not found.")
        return

    # Initialize modules
    print("Initializing Edge Pipeline...")
    vision = YOLOv8Detector(model_path="yolov8n.pt") # Fast nano model
    radar = VelocityExtractor()
    fusion = FusionEngine()
    logic = IncidentLogic()
    lora = LoRaWANTransmitter()
    
    cap = cv2.VideoCapture(video_path)
    output_json_path = "outputs/live_events.json"
    
    os.makedirs("outputs", exist_ok=True)
    # Clear old events
    with open(output_json_path, 'w') as f:
        json.dump({}, f)

    print("Starting processing...")
    frame_count = 0
    active_incident = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Process every N frames to simulate real-time edge constraints
        if frame_count % 3 != 0:
            continue
            
        detections, annotated_frame = vision.detect_and_track(frame)
        
        for det in detections:
            # We filter for cars/trucks
            if det['class'] not in ['car', 'truck', 'bus']:
                continue
                
            # Simulate radar extraction for this target
            # For demonstration, we simulate negative velocity if y is decreasing, positive if increasing
            # This links the simulated radar to the visual movement
            # Let's say moving up the frame (decreasing y) is wrong way (-15 km/h)
            box = det['box']
            y_center = (box[1] + box[3]) / 2
            
            # Simple simulation: if y_center is in upper half and moving up, simulate negative velocity
            # We'll just hardcode a simulated velocity for the sake of the DSP pipeline execution
            true_vel = -18.0 if y_center < 360 else 30.0 
            
            raw_signal = radar.generate_simulated_if_signal(true_vel)
            extracted_vel = radar.extract_velocity(raw_signal)
            # Add sign back since our simple FFT extractor returned magnitude
            if true_vel < 0: extracted_vel = -extracted_vel
            
            # Fusion
            fused = fusion.fuse(det, extracted_vel)
            
            # Logic
            incident = logic.process(fused)
            
            if incident:
                active_incident = incident
                lora.transmit(incident)
                
                # Write to JSON for dashboard
                with open(output_json_path, 'w') as f:
                    json.dump(incident, f)
                    
        # Sleep to simulate real-time playback speed
        time.sleep(0.05)
        
    cap.release()
    print("Pipeline finished.")

if __name__ == "__main__":
    main()
