import librosa
from scipy import signal
import numpy as np

def normalize_amplitude(y: np.ndarray):
    """
    Normalize the signal amplitude to the range [-1, 1].
    
    Args:
        y (np.ndarray): input waveform
    
    Returns:
        np.ndarray: normalized waveform
    """
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak
    return y

def load_audio(filepath, sr=None):
    """
    Load and preprocess an audio file using librosa and SciPy.
    
    Steps:
    1. Load audio as mono waveform with librosa.
    2. Normalize amplitude to [-1, 1].
    3. Apply a 4th-order Butterworth band-pass filter (5–10 kHz) 
       using zero-phase filtering (`sosfiltfilt`).
    
    Args:
        filepath (str): path to the .wav file
        sr (int or None): target sampling rate. 
                          If None, the original sampling rate is preserved.
    
    Returns:
        y (np.ndarray): preprocessed waveform
        sr (int): sampling rate
    """
    # 1) Load audio file
    y, sr = librosa.load(filepath, sr=sr, mono=True)

    # 2) Normalize amplitude
    y = normalize_amplitude(y)

    # 3) Design a band-pass Butterworth filter (4th order, 5–10 kHz)
    sos = signal.butter(N=4, Wn=[5000.0, 10000.0], btype="bandpass", fs=32000, output="sos")

    # 4) Apply zero-phase filtering (filtfilt) along the time axis
    y = signal.sosfiltfilt(sos, y, axis=0)

    return y, sr
