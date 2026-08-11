import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal.windows import hann

class VelocityExtractor:
    def __init__(self, sample_rate=10000, duration=0.1):
        self.sample_rate = sample_rate
        self.duration = duration
        self.N = int(sample_rate * duration)
        
    def generate_simulated_if_signal(self, true_velocity_kmh):
        # Simulate IF signal for a target moving at true_velocity_kmh
        # V = f_d * c / (2 * f_c) -> f_d = 2 * V * f_c / c
        # We will map velocity directly to a frequency for simulation purposes
        # Let's say 1 km/h = 100 Hz doppler shift
        f_d = true_velocity_kmh * 100 
        t = np.linspace(0, self.duration, self.N, endpoint=False)
        signal = np.sin(2 * np.pi * f_d * t) + 0.5 * np.random.randn(self.N) # Add noise
        return signal

    def extract_velocity(self, raw_radar_data):
        # Apply Hanning window
        windowed_data = raw_radar_data * hann(self.N)
        # Compute FFT
        yf = fft(windowed_data)
        xf = fftfreq(self.N, 1 / self.sample_rate)
        
        # Find peak frequency (ignore DC and negative freqs)
        positive_freqs = xf > 10 # Ignore very low freq clutter
        if not np.any(positive_freqs):
            return 0.0
            
        peak_idx = np.argmax(np.abs(yf[positive_freqs]))
        peak_freq = xf[positive_freqs][peak_idx]
        
        # Convert back to velocity (inverse of our simulation mapping)
        velocity_kmh = peak_freq / 100.0
        # Determine direction based on phase/IQ (simplified here by allowing negative freqs to indicate direction if complex data was used)
        # For our sim, we will just pass signed frequency if needed. But let's assume we extract it correctly.
        return velocity_kmh
