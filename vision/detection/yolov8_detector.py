from ultralytics import YOLO

class YOLOv8Detector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        print(f"Loaded YOLO model: {model_path}")

    def detect_and_track(self, frame):
        # Run tracking using ByteTrack
        results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)
        detections = []
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            classes = results[0].boxes.cls.int().cpu().tolist()
            confidences = results[0].boxes.conf.cpu().tolist()
            
            for box, track_id, cls, conf in zip(boxes, track_ids, classes, confidences):
                detections.append({
                    "track_id": track_id,
                    "box": box, # [x1, y1, x2, y2]
                    "class": self.model.names[cls],
                    "conf": conf
                })
        return detections, results[0].plot()
