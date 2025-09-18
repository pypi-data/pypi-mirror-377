"""
Unified Cython extension for SpeexAEC
This module includes echo cancellation, preprocessing, and resampling classes.
"""

# Include existing feature modules into a single extension module
include "echo.pyx"
include "preprocess.pyx"
include "resample.pyx"
