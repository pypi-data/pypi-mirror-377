import numpy as np
from scipy.signal import correlate, find_peaks, convolve

def matched_filter(signal, pulse_width, fs):
    pulse_samples = int(pulse_width * fs)
    template = np.ones(pulse_samples)
    return np.convolve(signal, template[::-1], mode='same')

def autocorrelation(signal):
    auto = correlate(signal, signal, mode='full')
    lags = np.arange(-len(signal)+1, len(signal)) / 1.0  # will scale outside
    return auto, lags

def estimate_PRI_from_autocorr(auto, lags, threshold_factor=0.1):
    # Only positive lags
    pos_mask = lags > 0
    auto_pos = auto[pos_mask]
    lags_pos = lags[pos_mask]

    peaks, _ = find_peaks(auto_pos, height=threshold_factor*np.max(auto_pos))
    peak_lags = lags_pos[peaks]

    estimated_PRIs = np.diff(peak_lags)
    PRI_estimate = np.median(estimated_PRIs)
    return PRI_estimate, peak_lags, auto_pos, lags_pos

def estimate_pulse_width_from_autocorr(auto, lags, zoom_range=20e-6, fs=1e6):
    center_idx = len(auto)//2
    zoom_mask = (np.arange(len(auto)) >= center_idx - int(zoom_range*fs)) & \
                (np.arange(len(auto)) <= center_idx + int(zoom_range*fs))
    zoom_lags = lags[zoom_mask]
    zoom_auto = auto[zoom_mask]

    center_value = zoom_auto[np.argmax(zoom_auto)]
    threshold = 0.01 * center_value

    # Left side
    left_idx_candidates = np.where(zoom_auto[:len(zoom_auto)//2] <= threshold)[0]
    left_idx = left_idx_candidates[-1] if len(left_idx_candidates) > 0 else 0

    # Right side
    right_idx_candidates = np.where(zoom_auto[len(zoom_auto)//2:] <= threshold)[0]
    right_idx = right_idx_candidates[0] + len(zoom_auto)//2 if len(right_idx_candidates) > 0 else len(zoom_auto)-1

    pulse_width_estimate = zoom_lags[right_idx] - zoom_lags[left_idx]
    return pulse_width_estimate, zoom_lags, zoom_auto, left_idx, right_idx

def estimate_PRI_from_mf(mf_output, t, threshold_ratio=0.5):
    peaks, _ = find_peaks(mf_output, height=threshold_ratio*np.max(mf_output))
    peak_times = t[peaks]
    estimated_PRIs = np.diff(peak_times)
    mean_PRI = np.mean(estimated_PRIs)
    std_PRI = np.std(estimated_PRIs)
    return mean_PRI, std_PRI, peak_times, estimated_PRIs

def detect_fundamental_PRIs(auto_pos, lags_pos, N_emitters=2, min_PRI=None, tol=0.03, smooth_signal=None):
    """
    Detect fundamental PRIs from autocorrelation peaks with harmonic rejection.
    """
    signal_to_use = smooth_signal if smooth_signal is not None else auto_pos
    prominence = 0.12 * np.max(signal_to_use)
    min_distance = int(0.3 * min_PRI * 1e6) if min_PRI is not None else 1
    peaks, _ = find_peaks(signal_to_use, prominence=prominence, distance=min_distance)
    peak_lags_us = lags_pos[peaks] * 1e6

    fundamentals = []
    for lag_us in np.sort(peak_lags_us):
        if min_PRI and lag_us < 0.5 * min_PRI*1e6:
            continue
        is_harmonic = any(abs(lag_us/f - round(lag_us/f)) < tol for f in fundamentals)
        if not is_harmonic:
            fundamentals.append(lag_us)
    return np.array(fundamentals[:N_emitters]), peak_lags_us, peaks

def add_awgn(signal, SNR_dB, seed=None, rng=None):
    """
    Additive White Gaussian Noise to achieve target SNR.
    
    Parameters
    ----------
    signal : np.ndarray
        Input clean signal.
    SNR_dB : float
        Desired SNR in dB (relative to signal power).
    rng : np.random.Generator, optional
        Random generator (default None, uses np.random).

    Returns
    -------
    noisy_signal : np.ndarray
    """
    if rng is None:
        rng = np.random.default_rng()

    signal_power = np.mean(signal**2)
    SNR_linear = 10**(SNR_dB / 10)
    noise_power = signal_power / SNR_linear
    noise = rng.normal(0, np.sqrt(noise_power), size=signal.shape)
    return signal + noise

def matched_filter_detect(rx_noisy, pulse_width, fs, base_PRI, jitter_std):
    """Apply matched filtering and detect peaks."""
    pulse_samples = int(pulse_width * fs)
    template = np.ones(pulse_samples)

    mf_output = convolve(rx_noisy, template[::-1], mode='valid')
    t_valid = np.arange(len(mf_output)) / fs

    threshold = 0.3 * np.max(mf_output)
    min_PRI_samples = int((base_PRI - 3*jitter_std) * fs)
    min_distance_samples = max(min_PRI_samples, pulse_samples)

    peaks, properties = find_peaks(
        mf_output, 
        height=threshold, 
        distance=min_distance_samples
    )

    template_delay = (pulse_samples - 1) / (2*fs)
    pulse_times_detected = t_valid[peaks] + template_delay

    return mf_output, t_valid, peaks, pulse_times_detected, threshold

def estimate_PRI_statistics(pulse_times_detected):
    """Estimate PRI statistics with outlier removal."""
    if len(pulse_times_detected) <= 1:
        return None, None, None

    estimated_PRIs = np.diff(pulse_times_detected)
    mean_PRI = np.mean(estimated_PRIs)
    std_PRI = np.std(estimated_PRIs)

    valid_mask = np.abs(estimated_PRIs - mean_PRI) <= 3 * std_PRI
    estimated_PRIs_clean = estimated_PRIs[valid_mask]

    if len(estimated_PRIs_clean) > 1:
        mean_PRI_clean = np.mean(estimated_PRIs_clean)
        std_PRI_clean = np.std(estimated_PRIs_clean)
    else:
        mean_PRI_clean = mean_PRI
        std_PRI_clean = std_PRI
        estimated_PRIs_clean = estimated_PRIs

    return estimated_PRIs_clean, mean_PRI_clean, std_PRI_clean

def matched_filter_chirp(rx_signal, pulse_width, fs, fc, bandwidth):
    """Apply matched filter using a single chirp template."""
    pulse_samples = int(pulse_width * fs)
    tau_template = np.arange(pulse_samples) / fs
    k = bandwidth / pulse_width
    template = np.cos(2*np.pi*fc*tau_template + np.pi*k*tau_template**2)
    
    mf_output = convolve(rx_signal, template[::-1], mode='same')
    return mf_output

def detect_peaks(mf_output, t, threshold_factor=0.5):
    """Detect peaks in matched filter output and estimate PRIs."""
    peak_indices, _ = find_peaks(mf_output, height=threshold_factor*np.max(mf_output))
    peak_times = t[peak_indices]
    estimated_PRIs = np.diff(peak_times)
    PRI_estimate = np.median(estimated_PRIs) if len(estimated_PRIs) > 0 else None
    return peak_indices, peak_times, estimated_PRIs, PRI_estimate

def estimate_pulse_widths(mf_output, t, peak_indices, window=20):
    """Estimate pulse width from matched filter peak widths at half maximum."""
    widths = []
    for idx in peak_indices:
        start = max(idx - window, 0)
        end = min(idx + window, len(mf_output))
        segment = mf_output[start:end]
        segment_times = t[start:end]

        half_max = mf_output[idx] / 2
        # left
        left_candidates = np.where(segment[:window] <= half_max)[0]
        left_idx = left_candidates[-1] if len(left_candidates) > 0 else 0
        # right
        right_candidates = np.where(segment[window:] <= half_max)[0]
        right_idx = right_candidates[0] + window if len(right_candidates) > 0 else len(segment) - 1

        widths.append(segment_times[right_idx] - segment_times[left_idx])
    return np.median(widths) if widths else None

def estimate_delay(rx1, rx2, fs):
    """
    Estimate time delay between rx1 and rx2 using cross-correlation.
    
    Returns:
        estimated_delay: in seconds
        lags: lag vector for plotting
        cross_corr: cross-correlation vector
    """
    cross_corr = correlate(rx2, rx1, mode='full')
    lags = np.arange(-len(rx1)+1, len(rx1)) / fs
    peak_idx = np.argmax(cross_corr)
    estimated_delay = lags[peak_idx]
    return estimated_delay, lags, cross_corr

def autocorr_two_pulses(rx, fs):
    auto = correlate(rx, rx, mode='full')
    lags = np.arange(-len(rx)+1, len(rx)) / fs
    positive_lags = lags[len(lags)//2:]
    auto_positive = auto[len(auto)//2:]
    return positive_lags, auto_positive

def estimate_fundamentals(positive_lags, auto_positive, min_lag_us=20, threshold_ratio=0.3, tolerance=0.05):
    peaks, _ = find_peaks(auto_positive, height=threshold_ratio*np.max(auto_positive))
    peak_lags = positive_lags[peaks]  # in seconds
    peak_lags_us = peak_lags * 1e6

    fundamentals = []
    for lag in sorted(peak_lags_us):
        if lag < min_lag_us:
            continue
        # reject harmonics
        is_harmonic = any(abs(lag/f - round(lag/f)) < tolerance for f in fundamentals)
        if not is_harmonic:
            fundamentals.append(lag)

    return np.array(fundamentals)