import json

class LoRaWANTransmitter:
    def __init__(self, device_eui="A1B2C3D4"):
        self.eui = device_eui

    def transmit(self, event_data):
        # Compact the payload for LoRaWAN (minimize bytes)
        payload = {
            "t": event_data["type"][:2], # WW or ST
            "s": event_data["severity"][0], # H, M, L
            "v": event_data["velocity"],
            "id": event_data["target"]
        }
        json_payload = json.dumps(payload)
        print(f"[LoRa TX] Sending {len(json_payload)} bytes: {json_payload}")
        return True
