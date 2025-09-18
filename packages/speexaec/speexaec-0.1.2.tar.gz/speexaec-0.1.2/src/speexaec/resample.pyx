# resample.pyx
"""
Python bindings for SpeexDSP Resampling
High-quality audio sample rate conversion
"""
import numpy as np
cimport numpy as cnp
from libc.stdlib cimport malloc, free

# Import C functions from speex_resampler.h
cdef extern from "speex/speex_resampler.h":
    ctypedef struct SpeexResamplerState
    
    SpeexResamplerState* speex_resampler_init(int nb_channels, 
                                             int in_rate, int out_rate,
                                             int quality, int *err)
    void speex_resampler_destroy(SpeexResamplerState *st)
    int speex_resampler_process_int(SpeexResamplerState *st,
                                   int channel_index,
                                   const short *in_, int *in_len,
                                   short *out, int *out_len)
    int speex_resampler_set_rate(SpeexResamplerState *st, int in_rate, int out_rate)
    void speex_resampler_get_rate(SpeexResamplerState *st, int *in_rate, int *out_rate)
    int speex_resampler_set_quality(SpeexResamplerState *st, int quality)
    int speex_resampler_get_quality(SpeexResamplerState *st, int *quality)
    int speex_resampler_skip_zeros(SpeexResamplerState *st)
    int speex_resampler_reset_mem(SpeexResamplerState *st)

# Error codes
cdef int RESAMPLER_ERR_SUCCESS = 0
cdef int RESAMPLER_ERR_ALLOC_FAILED = 1
cdef int RESAMPLER_ERR_BAD_STATE = 2
cdef int RESAMPLER_ERR_INVALID_ARG = 3
cdef int RESAMPLER_ERR_PTR_OVERLAP = 4


cdef class AudioResampler:
    """
    SpeexDSP Audio Resampler
    
    High-quality sample rate conversion for audio signals.
    Supports arbitrary input/output sample rates and multiple channels.
    """
    cdef SpeexResamplerState *st
    cdef int nb_channels
    cdef int in_rate
    cdef int out_rate
    cdef int quality

    def __init__(self, int nb_channels, int in_rate, int out_rate, int quality=4):
        """
        Initialize the audio resampler
        
        Parameters:
        -----------
        nb_channels : int
            Number of audio channels (1=mono, 2=stereo, etc.)
        in_rate : int
            Input sample rate in Hz
        out_rate : int
            Output sample rate in Hz
        quality : int, optional
            Resampling quality (0-10, default: 4)
            0 = lowest quality, fastest
            10 = highest quality, slowest
        """
        if nb_channels <= 0:
            raise ValueError("nb_channels must be positive")
        if in_rate <= 0:
            raise ValueError("in_rate must be positive")
        if out_rate <= 0:
            raise ValueError("out_rate must be positive")
        if quality < 0 or quality > 10:
            raise ValueError("quality must be between 0 and 10")
            
        self.nb_channels = nb_channels
        self.in_rate = in_rate
        self.out_rate = out_rate
        self.quality = quality
        
        # Initialize SpeexDSP resampler state
        cdef int err = 0
        self.st = speex_resampler_init(nb_channels, in_rate, out_rate, quality, &err)
        if self.st == NULL or err != RESAMPLER_ERR_SUCCESS:
            raise MemoryError(f"Failed to initialize Speex Resampler (error: {err})")

    def process(self, input_data, int channel=0):
        """
        Resample audio data for a specific channel
        
        Parameters:
        -----------
        input_data : array-like
            Input audio samples as int16
        channel : int, optional
            Channel index to process (default: 0)
            
        Returns:
        --------
        numpy.ndarray
            Resampled audio samples as int16
        """
        # Convert input to numpy array
        cdef cnp.ndarray[cnp.int16_t, ndim=1] in_arr = np.asarray(input_data, dtype=np.int16)
        
        # Validate channel index
        if channel < 0 or channel >= self.nb_channels:
            raise ValueError(f"channel {channel} out of range [0, {self.nb_channels-1}]")
        
        # Calculate output buffer size (with some extra space for safety)
        cdef int in_len = in_arr.shape[0]
        cdef int out_len = <int>((in_len * self.out_rate * 1.1) / self.in_rate) + 16
        
        # Prepare input/output buffers
        cdef cnp.ndarray[cnp.int16_t, ndim=1] out_arr = np.empty(out_len, dtype=np.int16)
        
        cdef int actual_in_len = in_len
        cdef int actual_out_len = out_len
        
        # Process resampling
        cdef int err = speex_resampler_process_int(
            self.st,
            channel,
            <const short*>in_arr.data, &actual_in_len,
            <short*>out_arr.data, &actual_out_len
        )
        
        if err != RESAMPLER_ERR_SUCCESS:
            raise RuntimeError(f"Resampling failed (error: {err})")
        
        # Return only the valid output data
        return out_arr[:actual_out_len]

    def process_interleaved(self, input_data):
        """
        Resample interleaved multi-channel audio data
        
        Parameters:
        -----------
        input_data : array-like
            Input audio samples as int16, interleaved by channel
            Shape should be (n_samples * n_channels,)
            
        Returns:
        --------
        numpy.ndarray
            Resampled interleaved audio samples as int16
        """
        # Convert input to numpy array
        cdef cnp.ndarray[cnp.int16_t, ndim=1] in_arr = np.asarray(input_data, dtype=np.int16)
        
        # Validate input length
        if in_arr.shape[0] % self.nb_channels != 0:
            raise ValueError(f"Input length ({in_arr.shape[0]}) not divisible by channels ({self.nb_channels})")
        
        cdef int samples_per_channel = in_arr.shape[0] // self.nb_channels
        
        # Calculate output buffer size
        cdef int out_samples_per_channel = <int>((samples_per_channel * self.out_rate * 1.1) / self.in_rate) + 16
        cdef int total_out_len = out_samples_per_channel * self.nb_channels
        
        # Prepare output buffer
        cdef cnp.ndarray[cnp.int16_t, ndim=1] out_arr = np.empty(total_out_len, dtype=np.int16)
        
        # Process each channel separately
        cdef int channel
        cdef int actual_in_len, actual_out_len
        cdef int max_out_samples = 0
        cdef cnp.ndarray[cnp.int16_t, ndim=1] channel_in
        cdef cnp.ndarray[cnp.int16_t, ndim=1] channel_out
        cdef int err
        
        for channel in range(self.nb_channels):
            # Extract channel data
            channel_in = in_arr[channel::self.nb_channels]
            channel_out = np.empty(out_samples_per_channel, dtype=np.int16)
            
            actual_in_len = samples_per_channel
            actual_out_len = out_samples_per_channel
            
            # Resample this channel
            err = speex_resampler_process_int(
                self.st,
                channel,
                <const short*>channel_in.data, &actual_in_len,
                <short*>channel_out.data, &actual_out_len
            )
            
            if err != RESAMPLER_ERR_SUCCESS:
                raise RuntimeError(f"Resampling failed for channel {channel} (error: {err})")
            
            # Interleave output
            out_arr[channel:actual_out_len*self.nb_channels:self.nb_channels] = channel_out[:actual_out_len]
            max_out_samples = max(max_out_samples, actual_out_len)
        
        # Return only the valid interleaved output data
        return out_arr[:max_out_samples * self.nb_channels]

    def set_rate(self, int in_rate, int out_rate):
        """Change the input/output sample rates"""
        if in_rate <= 0 or out_rate <= 0:
            raise ValueError("Sample rates must be positive")
        
        cdef int err = speex_resampler_set_rate(self.st, in_rate, out_rate)
        if err != RESAMPLER_ERR_SUCCESS:
            raise RuntimeError(f"Failed to set sample rates (error: {err})")
        
        self.in_rate = in_rate
        self.out_rate = out_rate

    def get_rate(self):
        """Get current input/output sample rates"""
        cdef int in_rate, out_rate
        speex_resampler_get_rate(self.st, &in_rate, &out_rate)
        return (in_rate, out_rate)

    def set_quality(self, int quality):
        """Set resampling quality (0-10)"""
        if quality < 0 or quality > 10:
            raise ValueError("Quality must be between 0 and 10")
        
        cdef int err = speex_resampler_set_quality(self.st, quality)
        if err != RESAMPLER_ERR_SUCCESS:
            raise RuntimeError(f"Failed to set quality (error: {err})")
        
        self.quality = quality

    def get_quality(self):
        """Get current resampling quality"""
        cdef int quality
        speex_resampler_get_quality(self.st, &quality)
        return quality

    def reset(self):
        """Reset the internal state of the resampler"""
        cdef int err = speex_resampler_reset_mem(self.st)
        if err != RESAMPLER_ERR_SUCCESS:
            raise RuntimeError(f"Failed to reset resampler (error: {err})")

    @property
    def channels(self):
        """Get number of channels"""
        return self.nb_channels
        
    @property
    def input_rate(self):
        """Get input sample rate"""
        return self.in_rate
        
    @property
    def output_rate(self):
        """Get output sample rate"""
        return self.out_rate

    def __dealloc__(self):
        """Cleanup when object is destroyed"""
        if self.st != NULL:
            speex_resampler_destroy(self.st)
            self.st = NULL
