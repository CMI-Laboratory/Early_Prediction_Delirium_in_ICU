import numpy as np
from scipy.signal import butter, filtfilt, medfilt
import json
import sys

'''
***Raw signal must be a one-dimensional ndarray like below.***

raw_data = array([1.2., 2.7., 1.3., ...,  1.7.,  1.5.,  1.2.])

'''

# Filter definitions
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def adaptive_filter(data, kernel_size=151):
    if kernel_size % 2 == 0:
        kernel_size += 1
    artifact_estimate = medfilt(data, kernel_size=71)
    data_clean = data - artifact_estimate
    return data_clean

def z_score_normalization(data):
    return (data - np.mean(data)) / np.std(data)

def process_signal(raw_data, sig_type='ecg',fs=250.0):
    # --- ECG Processing ---
    if sig_type == 'ecg':
        # 1. HPF 0.5 Hz
        hpf_ecg = butter_highpass_filter(raw_data, 0.5, fs, order=2)
        # 2. Adaptive Filtering
        adaptive_ecg = adaptive_filter(hpf_ecg)
        # 3. BPF 0.5-40 Hz
        bpf_ecg = butter_bandpass_filter(adaptive_ecg, 0.5, 40.0, fs, order=2)
        # 4. Normalization
        norm_ecg = z_score_normalization(bpf_ecg)
        
        processed_sig = norm_ecg
    
    elif sig_type = 'ppg':
        # --- PPG Processing ---
        # PPG Bandpass: 0.5 - 8 Hz (Removes DC wander and high freq noise)
        bpf_ppg = butter_bandpass_filter(raw_data, 0.5, 8.0, fs, order=2)
        norm_ppg = z_score_normalization(bpf_ppg)
        processed_sig = norm_ppg


    else:
        # --- Respiratory Processing ---
        # Resp Bandpass: 0.1 - 0.5 Hz (Focus on breathing rate ~6-30 bpm)
        bpf_resp = butter_bandpass_filter(raw_data, 0.1, 0.5, fs, order=2)
        norm_resp = z_score_normalization(bpf_resp)
        processed_sig = norm_resp
    
    return processed_sig

