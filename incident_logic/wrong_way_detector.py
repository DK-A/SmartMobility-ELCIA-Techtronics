import time

class IncidentLogic:
    def __init__(self):
        self.track_history = {} # id -> list of velocities and timestamps
        self.persistence_threshold = 2.0 # seconds
        self.velocity_threshold = -5.0 # km/h (negative is wrong way)
        self.stoppage_threshold = 2.0 # km/h (below this is stopped)
        self.stoppage_time_threshold = 5.0 # seconds

    def process(self, fused_target):
        tid = fused_target['target_id']
        vel = fused_target['velocity']
        current_time = time.time()
        
        if tid not in self.track_history:
            self.track_history[tid] = []
            
        self.track_history[tid].append({'time': current_time, 'vel': vel})
        
        # Keep only history within max lookback (e.g., 10 seconds)
        self.track_history[tid] = [h for h in self.track_history[tid] if current_time - h['time'] < 10.0]
        
        history = self.track_history[tid]
        duration = history[-1]['time'] - history[0]['time']
        avg_vel = sum(h['vel'] for h in history) / len(history)

        incident = None
        if avg_vel < self.velocity_threshold and duration >= self.persistence_threshold:
            incident = {
                "type": "WRONG-WAY MOVEMENT",
                "severity": "HIGH",
                "target": tid,
                "velocity": round(avg_vel, 1),
                "confidence": fused_target['confidence'],
                "evidence": [f"Camera trajectory ID: {tid}", "Radar velocity corroborated", f"{round(duration,1)}s persistence"],
                "action": "Alert operator and dispatch highway patrol.",
                "status": "OPEN",
                "box": fused_target['box']
            }
        elif abs(avg_vel) < self.stoppage_threshold and duration >= self.stoppage_time_threshold:
             incident = {
                "type": "STATIONARY BLOCKAGE",
                "severity": "MEDIUM",
                "target": tid,
                "velocity": round(avg_vel, 1),
                "confidence": fused_target['confidence'],
                "evidence": [f"Camera trajectory ID: {tid}", "Radar zero-doppler", f"{round(duration,1)}s persistence"],
                "action": "Inspect camera feed to determine blockage cause.",
                "status": "OPEN",
                "box": fused_target['box']
            }
        return incident
