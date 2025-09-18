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
from typing import TYPE_CHECKING, Iterable, Sequence, Tuple

__version__ = "0.1.2"
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


if TYPE_CHECKING:
    import numpy as np

    class EchoCanceller:
        frame_size_property: int
        filter_length_property: int
        sample_rate_property: int
        def __init__(self, frame_size: int, filter_length: int, sample_rate: int = 16000) -> None: ...
        def process(self, near_frame: Iterable[int], far_frame: Iterable[int]) -> np.ndarray: ...
        def process_bytes(self, near_frame: bytes, far_frame: bytes) -> bytes: ...

    class AudioPreprocessor:
        frame_size_property: int
        sample_rate_property: int
        def __init__(self, frame_size: int, sample_rate: int = 16000) -> None: ...
        def process(self, frame: Iterable[int]) -> tuple[Sequence[int], bool]: ...
        def set_denoise(self, enable: bool) -> None: ...
        def get_denoise(self) -> bool: ...
        def set_agc(self, enable: bool) -> None: ...
        def get_agc(self) -> bool: ...
        def set_vad(self, enable: bool) -> None: ...
        def get_vad(self) -> bool: ...
        def set_agc_level(self, level: float) -> None: ...
        def get_agc_level(self) -> float: ...
        def set_noise_suppress(self, suppress_db: int) -> None: ...
        def get_noise_suppress(self) -> int: ...
        def set_dereverb(self, enable: bool) -> None: ...
        def get_dereverb(self) -> bool: ...

    class AudioResampler:
        channels: int
        input_rate: int
        output_rate: int
        def __init__(self, nb_channels: int, in_rate: int, out_rate: int, quality: int = 4) -> None: ...
        def process(self, input_data: Iterable[int], channel: int = 0) -> np.ndarray: ...
        def process_interleaved(self, input_data: Iterable[int]) -> np.ndarray: ...
        def set_rate(self, in_rate: int, out_rate: int) -> None: ...
        def get_rate(self) -> Tuple[int, int]: ...
        def set_quality(self, quality: int) -> None: ...
        def get_quality(self) -> int: ...
        def reset(self) -> None: ...
