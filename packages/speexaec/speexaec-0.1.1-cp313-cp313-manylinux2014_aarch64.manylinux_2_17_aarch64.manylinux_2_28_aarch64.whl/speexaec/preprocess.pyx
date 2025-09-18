# preprocess.pyx
"""
Python bindings for SpeexDSP Audio Preprocessing
Includes noise suppression, VAD, and automatic gain control
"""
import numpy as np
cimport numpy as cnp
from libc.stdlib cimport malloc, free

# Import C functions from speex_preprocess.h
cdef extern from "speex/speex_preprocess.h":
    ctypedef struct SpeexPreprocessState
    
    SpeexPreprocessState* speex_preprocess_state_init(int frame_size, int sampling_rate)
    void speex_preprocess_state_destroy(SpeexPreprocessState *st)
    int speex_preprocess_ctl(SpeexPreprocessState *st, int request, void *ptr)
    int speex_preprocess_run(SpeexPreprocessState *st, short *x)

# Control constants from speex_preprocess.h
cdef int SPEEX_PREPROCESS_SET_DENOISE = 0
cdef int SPEEX_PREPROCESS_GET_DENOISE = 1
cdef int SPEEX_PREPROCESS_SET_AGC = 2
cdef int SPEEX_PREPROCESS_GET_AGC = 3
cdef int SPEEX_PREPROCESS_SET_VAD = 4
cdef int SPEEX_PREPROCESS_GET_VAD = 5
cdef int SPEEX_PREPROCESS_SET_AGC_LEVEL = 6
cdef int SPEEX_PREPROCESS_GET_AGC_LEVEL = 7
cdef int SPEEX_PREPROCESS_SET_DEREVERB = 8
cdef int SPEEX_PREPROCESS_GET_DEREVERB = 9
cdef int SPEEX_PREPROCESS_SET_DEREVERB_LEVEL = 10
cdef int SPEEX_PREPROCESS_GET_DEREVERB_LEVEL = 11
cdef int SPEEX_PREPROCESS_SET_DEREVERB_DECAY = 12
cdef int SPEEX_PREPROCESS_GET_DEREVERB_DECAY = 13
cdef int SPEEX_PREPROCESS_SET_PROB_START = 14
cdef int SPEEX_PREPROCESS_GET_PROB_START = 15
cdef int SPEEX_PREPROCESS_SET_PROB_CONTINUE = 16
cdef int SPEEX_PREPROCESS_GET_PROB_CONTINUE = 17
cdef int SPEEX_PREPROCESS_SET_NOISE_SUPPRESS = 18
cdef int SPEEX_PREPROCESS_GET_NOISE_SUPPRESS = 19
cdef int SPEEX_PREPROCESS_SET_ECHO_SUPPRESS = 20
cdef int SPEEX_PREPROCESS_GET_ECHO_SUPPRESS = 21
cdef int SPEEX_PREPROCESS_SET_ECHO_SUPPRESS_ACTIVE = 22
cdef int SPEEX_PREPROCESS_GET_ECHO_SUPPRESS_ACTIVE = 23


cdef class AudioPreprocessor:
    """
    SpeexDSP Audio Preprocessor
    
    Provides noise suppression, automatic gain control (AGC), 
    voice activity detection (VAD), and dereverberation.
    """
    cdef SpeexPreprocessState *st
    cdef int frame_size
    cdef int sample_rate

    def __init__(self, int frame_size, int sample_rate=16000):
        """
        Initialize the audio preprocessor
        
        Parameters:
        -----------
        frame_size : int
            Number of samples per frame (typically 160 for 16kHz, 20ms frames)
        sample_rate : int, optional
            Sampling rate in Hz (default: 16000)
        """
        if frame_size <= 0:
            raise ValueError("frame_size must be positive")
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
            
        self.frame_size = frame_size
        self.sample_rate = sample_rate
        
        # Initialize SpeexDSP preprocessor state
        self.st = speex_preprocess_state_init(frame_size, sample_rate)
        if self.st == NULL:
            raise MemoryError("Failed to initialize Speex Preprocess State")

    def process(self, frame):
        """
        Process audio frame with preprocessing
        
        Parameters:
        -----------
        frame : array-like
            Input audio frame as int16 samples
            
        Returns:
        --------
        tuple
            (processed_frame, voice_activity)
            - processed_frame: numpy.ndarray of processed int16 samples
            - voice_activity: bool indicating if voice was detected
        """
        # Convert input to numpy array
        cdef cnp.ndarray[cnp.int16_t, ndim=1] frame_arr = np.asarray(frame, dtype=np.int16)
        
        # Validate frame size
        if frame_arr.shape[0] != self.frame_size:
            raise ValueError(f"frame size ({frame_arr.shape[0]}) != expected ({self.frame_size})")
        
        # Make a copy since speex_preprocess_run modifies in-place
        cdef cnp.ndarray[cnp.int16_t, ndim=1] out_arr = frame_arr.copy()
        
        # Process with preprocessing
        cdef int vad_result = speex_preprocess_run(self.st, <short*>out_arr.data)
        
        return out_arr, bool(vad_result)

    def set_denoise(self, bint enable):
        """Enable/disable noise suppression"""
        cdef int val = 1 if enable else 0
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_SET_DENOISE, <void*>&val)

    def get_denoise(self):
        """Get noise suppression status"""
        cdef int val
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_GET_DENOISE, <void*>&val)
        return bool(val)

    def set_agc(self, bint enable):
        """Enable/disable automatic gain control"""
        cdef int val = 1 if enable else 0
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_SET_AGC, <void*>&val)

    def get_agc(self):
        """Get AGC status"""
        cdef int val
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_GET_AGC, <void*>&val)
        return bool(val)

    def set_vad(self, bint enable):
        """Enable/disable voice activity detection"""
        cdef int val = 1 if enable else 0
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_SET_VAD, <void*>&val)

    def get_vad(self):
        """Get VAD status"""
        cdef int val
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_GET_VAD, <void*>&val)
        return bool(val)

    def set_agc_level(self, float level):
        """Set AGC level (typically 8000-32000)"""
        cdef float val = level
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_SET_AGC_LEVEL, <void*>&val)

    def get_agc_level(self):
        """Get AGC level"""
        cdef float val
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_GET_AGC_LEVEL, <void*>&val)
        return val

    def set_noise_suppress(self, int suppress_db):
        """Set noise suppression level in dB (negative values)"""
        cdef int val = suppress_db
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_SET_NOISE_SUPPRESS, <void*>&val)

    def get_noise_suppress(self):
        """Get noise suppression level"""
        cdef int val
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_GET_NOISE_SUPPRESS, <void*>&val)
        return val

    def set_dereverb(self, bint enable):
        """Enable/disable dereverberation"""
        cdef int val = 1 if enable else 0
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_SET_DEREVERB, <void*>&val)

    def get_dereverb(self):
        """Get dereverberation status"""
        cdef int val
        speex_preprocess_ctl(self.st, SPEEX_PREPROCESS_GET_DEREVERB, <void*>&val)
        return bool(val)

    @property
    def frame_size_property(self):
        """Get the frame size"""
        return self.frame_size
        
    @property
    def sample_rate_property(self):
        """Get the sample rate"""
        return self.sample_rate

    def __dealloc__(self):
        """Cleanup when object is destroyed"""
        if self.st != NULL:
            speex_preprocess_state_destroy(self.st)
            self.st = NULL
