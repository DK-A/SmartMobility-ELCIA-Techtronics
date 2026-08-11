class FusionEngine:
    def __init__(self):
        pass

    def fuse(self, vision_track, radar_velocity):
        # In a real system, we'd associate radar targets with vision tracks using spatial calibration
        # Here we assume a 1:1 mapping for the primary target
        fused_velocity = radar_velocity
        confidence = vision_track['conf'] * 0.95 # Slight penalty for fusion uncertainty
        
        return {
            "target_id": f"Vehicle-{vision_track['track_id']}",
            "velocity": fused_velocity,
            "confidence": round(confidence * 100, 1),
            "box": vision_track['box'].tolist()
        }
