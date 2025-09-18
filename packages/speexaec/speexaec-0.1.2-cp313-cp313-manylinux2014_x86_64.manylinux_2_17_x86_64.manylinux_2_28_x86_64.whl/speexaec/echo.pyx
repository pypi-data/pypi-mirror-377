# echo.pyx
"""
Python bindings for SpeexDSP Echo Cancellation
"""
import numpy as np
cimport numpy as cnp
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy

# Import C functions from speex_echo.h
cdef extern from "speex/speex_echo.h":
    ctypedef struct SpeexEchoState
    
    SpeexEchoState* speex_echo_state_init(int frame_size, int filter_length)
    void speex_echo_state_destroy(SpeexEchoState *st)
    int speex_echo_ctl(SpeexEchoState *st, int request, void *ptr)
    void speex_echo_cancellation(SpeexEchoState *st,
                                 const short *rec, const short *play,
                                 short *out)

# Control constants from speex_echo.h
cdef int SPEEX_ECHO_SET_SAMPLING_RATE = 24
cdef int SPEEX_ECHO_GET_SAMPLING_RATE = 25


cdef class EchoCanceller:
    """
    SpeexDSP Echo Canceller
    
    High-performance acoustic echo cancellation using the Speex DSP library.
    Suitable for real-time audio processing applications.
    """
    cdef SpeexEchoState *st
    cdef int frame_size
    cdef int filter_length
    cdef int sample_rate

    def __init__(self, int frame_size, int filter_length, int sample_rate=16000):
        """
        Initialize the echo canceller
        
        Parameters:
        -----------
        frame_size : int
            Number of samples per frame (typically 160 for 16kHz, 20ms frames)
        filter_length : int
            Length of echo cancellation filter (typically 10-20 times frame_size)  
        sample_rate : int, optional
            Sampling rate in Hz (default: 16000)
        """
        if frame_size <= 0:
            raise ValueError("frame_size must be positive")
        if filter_length <= 0:
            raise ValueError("filter_length must be positive")
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
            
        self.frame_size = frame_size
        self.filter_length = filter_length
        self.sample_rate = sample_rate
        
        # Initialize SpeexDSP echo state
        self.st = speex_echo_state_init(frame_size, filter_length)
        if self.st == NULL:
            raise MemoryError("Failed to initialize Speex Echo State")
        
        # Set sampling rate
        cdef int rate = sample_rate
        if speex_echo_ctl(self.st, SPEEX_ECHO_SET_SAMPLING_RATE, <void*>&rate) != 0:
            speex_echo_state_destroy(self.st)
            raise RuntimeError("Failed to set sampling rate")

    def process(self, near_frame, far_frame):
        """
        Process audio frames for echo cancellation
        
        Parameters:
        -----------
        near_frame : array-like
            Input audio frame (microphone signal) as int16 samples
        far_frame : array-like  
            Reference frame (speaker signal) as int16 samples
            
        Returns:
        --------
        numpy.ndarray
            Echo-cancelled output frame as int16 samples
        """
        # Convert input to numpy arrays
        cdef cnp.ndarray[cnp.int16_t, ndim=1] near_arr = np.asarray(near_frame, dtype=np.int16)
        cdef cnp.ndarray[cnp.int16_t, ndim=1] far_arr = np.asarray(far_frame, dtype=np.int16)
        
        # Validate frame sizes
        if near_arr.shape[0] != self.frame_size:
            raise ValueError(f"near_frame size ({near_arr.shape[0]}) != frame_size ({self.frame_size})")
        if far_arr.shape[0] != self.frame_size:
            raise ValueError(f"far_frame size ({far_arr.shape[0]}) != frame_size ({self.frame_size})")
        
        # Prepare output buffer
        cdef cnp.ndarray[cnp.int16_t, ndim=1] out_arr = np.empty(self.frame_size, dtype=np.int16)
        
        # Process echo cancellation
        speex_echo_cancellation(
            self.st,
            <const short*>near_arr.data,
            <const short*>far_arr.data, 
            <short*>out_arr.data
        )
        
        return out_arr

    def process_bytes(self, bytes near_frame, bytes far_frame):
        """
        Process audio frames as raw bytes (for backward compatibility)
        
        Parameters:
        -----------
        near_frame : bytes
            Input audio frame as raw int16 bytes
        far_frame : bytes
            Reference frame as raw int16 bytes
            
        Returns:
        --------
        bytes
            Echo-cancelled output frame as raw int16 bytes
        """
        cdef int expected_bytes = self.frame_size * 2  # 2 bytes per int16 sample
        
        if len(near_frame) != expected_bytes:
            raise ValueError(f"near_frame size ({len(near_frame)}) != expected ({expected_bytes})")
        if len(far_frame) != expected_bytes:
            raise ValueError(f"far_frame size ({len(far_frame)}) != expected ({expected_bytes})")
        
        # Convert bytes to pointers
        cdef const short *near_buf = <const short*><char*>near_frame
        cdef const short *far_buf = <const short*><char*>far_frame
        
        # Allocate output buffer
        cdef short *out_buf = <short*>malloc(expected_bytes)
        if out_buf == NULL:
            raise MemoryError("Failed to allocate output buffer")
        
        try:
            # Process echo cancellation
            speex_echo_cancellation(self.st, near_buf, far_buf, out_buf)
            
            # Convert output to bytes
            return (<char*>out_buf)[:expected_bytes]
        finally:
            free(out_buf)

    @property
    def frame_size_property(self):
        """Get the frame size"""
        return self.frame_size
        
    @property  
    def filter_length_property(self):
        """Get the filter length"""
        return self.filter_length
        
    @property
    def sample_rate_property(self):
        """Get the sample rate"""
        return self.sample_rate

    def __dealloc__(self):
        """Cleanup when object is destroyed"""
        if self.st != NULL:
            speex_echo_state_destroy(self.st)
            self.st = NULL
