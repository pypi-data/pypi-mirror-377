#!/usr/bin/env python3
"""
Audio preprocessing example with noise suppression and VAD
"""
import numpy as np
import time
from speexaec import AudioPreprocessor


def main():
    """Demonstrate audio preprocessing features"""
    print("SpeexAEC Audio Preprocessing Example")
    print("=" * 45)
    
    # Configuration
    sample_rate = 16000      # 16 kHz sample rate  
    frame_duration_ms = 20   # 20ms frames
    
    # Calculate frame size
    frame_size = int(sample_rate * frame_duration_ms / 1000)
    
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Frame size: {frame_size} samples ({frame_duration_ms}ms)")
    print()
    
    # Initialize preprocessor
    try:
        preprocessor = AudioPreprocessor(frame_size, sample_rate)
        print("✓ Audio preprocessor initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize preprocessor: {e}")
        return
    
    # Configure preprocessing features
    print("\nConfiguring preprocessing features...")
    
    # Enable noise suppression
    preprocessor.set_denoise(True)
    preprocessor.set_noise_suppress(-15)  # Suppress noise by 15dB
    print("✓ Noise suppression enabled (-15dB)")
    
    # Enable automatic gain control
    preprocessor.set_agc(True)
    preprocessor.set_agc_level(8000)  # Target level
    print("✓ Automatic gain control enabled (level: 8000)")
    
    # Enable voice activity detection
    preprocessor.set_vad(True)
    print("✓ Voice activity detection enabled")
    
    # Enable dereverberation
    preprocessor.set_dereverb(True)
    print("✓ Dereverberation enabled")
    
    # Verify settings
    print(f"\nCurrent settings:")
    print(f"  Denoise: {preprocessor.get_denoise()}")
    print(f"  AGC: {preprocessor.get_agc()}")
    print(f"  VAD: {preprocessor.get_vad()}")
    print(f"  Dereverb: {preprocessor.get_dereverb()}")
    print(f"  Noise suppress level: {preprocessor.get_noise_suppress()}dB")
    print(f"  AGC level: {preprocessor.get_agc_level()}")
    
    # Simulate different types of audio
    test_scenarios = [
        ("Clean speech", generate_clean_speech),
        ("Noisy speech", generate_noisy_speech),
        ("Background noise only", generate_background_noise),
        ("Silence", generate_silence),
        ("Reverberant speech", generate_reverberant_speech),
    ]
    
    print(f"\nTesting preprocessing on different audio types...")
    print("-" * 60)
    
    for scenario_name, signal_generator in test_scenarios:
        print(f"\n{scenario_name}:")
        
        # Generate test frames
        frames = [signal_generator(frame_size) for _ in range(10)]
        
        # Process frames and analyze results
        voice_detections = []
        processing_times = []
        
        for i, frame in enumerate(frames):
            start_time = time.perf_counter()
            processed_frame, voice_detected = preprocessor.process(frame)
            end_time = time.perf_counter()
            
            processing_time = (end_time - start_time) * 1000  # ms
            processing_times.append(processing_time)
            voice_detections.append(voice_detected)
        
        # Analyze results
        voice_detection_rate = sum(voice_detections) / len(voice_detections) * 100
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        # Calculate signal statistics
        original_rms = np.sqrt(np.mean([np.mean(f**2) for f in frames]))
        processed_rms = np.sqrt(np.mean([np.mean(f**2) for f in [
            preprocessor.process(frame)[0] for frame in frames[:3]
        ]]))
        
        print(f"  Voice detection rate: {voice_detection_rate:.1f}%")
        print(f"  Avg processing time: {avg_processing_time:.3f}ms")
        print(f"  Signal level change: {original_rms:.0f} → {processed_rms:.0f} RMS")
    
    print(f"\n" + "=" * 60)
    print("Preprocessing demo completed successfully!")


def generate_clean_speech(length):
    """Generate clean speech-like signal"""
    t = np.arange(length)
    
    # Fundamental frequency around 150Hz
    fundamental = 150
    signal = np.sin(2 * np.pi * fundamental * t / 16000) * 1000
    
    # Add harmonics for realism
    signal += np.sin(2 * np.pi * fundamental * 2 * t / 16000) * 400
    signal += np.sin(2 * np.pi * fundamental * 3 * t / 16000) * 200
    signal += np.sin(2 * np.pi * fundamental * 4 * t / 16000) * 100
    
    # Apply speech envelope
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * t / length * 2)
    signal *= envelope
    
    return np.clip(signal, -32767, 32767).astype(np.int16)


def generate_noisy_speech(length):
    """Generate speech with background noise"""
    speech = generate_clean_speech(length)
    
    # Add white noise
    noise = np.random.normal(0, 300, length)
    
    # Add some colored noise (low frequency rumble)
    t = np.arange(length)
    colored_noise = np.sin(2 * np.pi * 50 * t / 16000) * 200
    colored_noise += np.sin(2 * np.pi * 120 * t / 16000) * 150
    
    total_noise = noise + colored_noise
    noisy_speech = speech + total_noise
    
    return np.clip(noisy_speech, -32767, 32767).astype(np.int16)


def generate_background_noise(length):
    """Generate background noise without speech"""
    # Simulate air conditioning, fan noise, etc.
    t = np.arange(length)
    
    # Low frequency hum
    noise = np.sin(2 * np.pi * 60 * t / 16000) * 200  # 60Hz hum
    noise += np.sin(2 * np.pi * 120 * t / 16000) * 100  # 120Hz harmonic
    
    # Add white noise
    noise += np.random.normal(0, 150, length)
    
    # Add some random low-frequency components
    for freq in [80, 100, 140, 180]:
        amplitude = np.random.uniform(50, 150)
        noise += np.sin(2 * np.pi * freq * t / 16000) * amplitude
    
    return np.clip(noise, -32767, 32767).astype(np.int16)


def generate_silence(length):
    """Generate near-silence with minimal noise"""
    # Very quiet background noise
    noise = np.random.normal(0, 20, length)
    return np.clip(noise, -32767, 32767).astype(np.int16)


def generate_reverberant_speech(length):
    """Generate speech with reverberation"""
    speech = generate_clean_speech(length)
    
    # Simple reverberation simulation
    reverb = speech.copy().astype(np.float32)
    
    # Add delayed and attenuated copies (early reflections)
    delays = [20, 35, 50, 80, 120]  # samples
    attenuations = [0.3, 0.25, 0.2, 0.15, 0.1]
    
    for delay, attenuation in zip(delays, attenuations):
        if delay < length:
            reverb[delay:] += speech[:-delay] * attenuation
    
    # Add late reverberation (exponentially decaying noise)
    t = np.arange(length)
    late_reverb = np.random.normal(0, 100, length) * np.exp(-t / (length * 0.5))
    reverb += late_reverb
    
    return np.clip(reverb, -32767, 32767).astype(np.int16)


if __name__ == "__main__":
    main()
