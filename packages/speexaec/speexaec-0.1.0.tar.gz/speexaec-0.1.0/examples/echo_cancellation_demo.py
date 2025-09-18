#!/usr/bin/env python3
"""
Simple echo cancellation example
"""
import numpy as np
import time
from speexaec import EchoCanceller


def main():
    """Demonstrate basic echo cancellation"""
    print("SpeexAEC Echo Cancellation Example")
    print("=" * 40)
    
    # Configuration
    sample_rate = 16000      # 16 kHz sample rate
    frame_duration_ms = 20   # 20ms frames
    echo_tail_ms = 200       # 200ms echo tail
    
    # Calculate frame parameters
    frame_size = int(sample_rate * frame_duration_ms / 1000)
    filter_length = int(sample_rate * echo_tail_ms / 1000)
    
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Frame size: {frame_size} samples ({frame_duration_ms}ms)")
    print(f"Filter length: {filter_length} samples ({echo_tail_ms}ms)")
    print()
    
    # Initialize echo canceller
    try:
        ec = EchoCanceller(frame_size, filter_length, sample_rate)
        print("✓ Echo canceller initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize echo canceller: {e}")
        return
    
    # Simulate real-time processing
    print("\nSimulating real-time echo cancellation...")
    print("Processing 100 frames...")
    
    total_time = 0
    num_frames = 100
    
    for i in range(num_frames):
        # Generate simulated audio frames
        # In real application, these would come from microphone and speaker
        near_frame = generate_speech_like_signal(frame_size)
        far_frame = generate_speech_like_signal(frame_size)
        
        # Add simulated echo (delayed and attenuated far signal)
        echo_delay = 50  # samples
        echo_attenuation = 0.3
        if i >= echo_delay:
            # Add echo to near signal
            echo_component = far_frame * echo_attenuation
            near_frame = near_frame + echo_component.astype(np.int16)
        
        # Measure processing time
        start_time = time.perf_counter()
        
        # Process echo cancellation
        output_frame = ec.process(near_frame, far_frame)
        
        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000  # ms
        total_time += processing_time
        
        # Print progress occasionally
        if (i + 1) % 20 == 0:
            print(f"  Processed {i+1}/{num_frames} frames "
                  f"(avg: {processing_time:.2f}ms per frame)")
    
    # Performance summary
    avg_time = total_time / num_frames
    frame_time = frame_duration_ms
    cpu_usage = (avg_time / frame_time) * 100
    
    print(f"\nPerformance Summary:")
    print(f"  Average processing time: {avg_time:.3f}ms per frame")
    print(f"  Frame duration: {frame_time}ms")
    print(f"  CPU usage: {cpu_usage:.1f}%")
    
    if cpu_usage < 50:
        print("  ✓ Excellent performance for real-time processing")
    elif cpu_usage < 80:
        print("  ⚠ Good performance, should work for real-time")
    else:
        print("  ⚠ High CPU usage, may struggle in real-time")


def generate_speech_like_signal(length):
    """Generate a speech-like test signal"""
    # Create a signal with speech-like characteristics
    # Mix of low-frequency content and some high-frequency components
    t = np.arange(length)
    
    # Base frequency around 200Hz (typical voice fundamental)
    fundamental = 200
    signal = np.sin(2 * np.pi * fundamental * t / 16000) * 500
    
    # Add harmonics
    signal += np.sin(2 * np.pi * fundamental * 2 * t / 16000) * 200
    signal += np.sin(2 * np.pi * fundamental * 3 * t / 16000) * 100
    
    # Add some noise for realism
    noise = np.random.normal(0, 50, length)
    signal += noise
    
    # Apply envelope to make it more speech-like
    envelope = np.exp(-t / (length * 0.3))  # Decay envelope
    signal *= envelope
    
    # Ensure it fits in int16 range
    signal = np.clip(signal, -32767, 32767)
    return signal.astype(np.int16)


if __name__ == "__main__":
    main()
