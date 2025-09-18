"""
SpeexAEC - Python bindings for SpeexDSP audio processing library

This package provides high-performance Python bindings for the SpeexDSP library,
enabling real-time audio processing including:

- Echo cancellation
- Noise suppression 
- Voice activity detection (VAD)
- Automatic gain control (AGC)
- Audio resampling
- Dereverberation

Designed for use in real-time applications including VoIP, video conferencing,
and embedded audio processing on platforms like BeagleBone AI.

Compatible with aiortc and other real-time communication frameworks.
"""

__version__ = "0.1.1"
__author__ = "Miguel Ángel Manzano"
__email__ = "mamanzano@leitat.org"

# Import main classes from the unified extension module
try:
    from ._speexaec import EchoCanceller, AudioPreprocessor, AudioResampler
    
    __all__ = [
        'EchoCanceller',
        'AudioPreprocessor', 
        'AudioResampler',
    ]
    
except ImportError as e:
    # Handle case where extensions aren't built yet
    import warnings
    warnings.warn(f"Could not import compiled extensions: {e}. "
                 "Make sure the package is properly installed with: pip install -e .")
    __all__ = []

# Utility functions
def get_version():
    """Get the package version"""
    return __version__

def get_frame_size(sample_rate=16000, frame_duration_ms=20):
    """
    Calculate frame size for given sample rate and duration
    
    Parameters:
    -----------
    sample_rate : int
        Sample rate in Hz (default: 16000)
    frame_duration_ms : int
        Frame duration in milliseconds (default: 20)
        
    Returns:
    --------
    int
        Frame size in samples
    """
    return int(sample_rate * frame_duration_ms / 1000)


def get_filter_length(sample_rate=16000, echo_tail_ms=200):
    """
    Calculate echo cancellation filter length
    
    Parameters:
    -----------
    sample_rate : int
        Sample rate in Hz (default: 16000)
    echo_tail_ms : int
        Echo tail length in milliseconds (default: 200)
        
    Returns:
    --------
    int
        Filter length in samples
    """
    return int(sample_rate * echo_tail_ms / 1000)