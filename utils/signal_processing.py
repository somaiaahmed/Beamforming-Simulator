import numpy as np
import scipy.signal as signal

def apply_window_function(signal_data, window_type='hann'):
    """
    Apply windowing function to signal
    
    Args:
        signal_data (np.array): Input signal
        window_type (str): Type of window function
    
    Returns:
        np.array: Windowed signal
    """
    window_functions = {
        'hann': np.hanning,
        'hamming': np.hamming,
        'blackman': np.blackman,
        'bartlett': np.bartlett
    }
    
    if window_type not in window_functions:
        raise ValueError(f"Unsupported window type: {window_type}")
    
    window = window_functions[window_type](len(signal_data))
    return signal_data * window

def apply_delay_and_sum(signals, delays):
    """
    Apply time delays and sum signals
    
    Args:
        signals (np.array): Input signals
        delays (np.array): Delay values for each signal
    
    Returns:
        np.array: Summed signal
    """
    # Interpolate signals based on delays
    delayed_signals = np.zeros_like(signals)
    for i, (sig, delay) in enumerate(zip(signals, delays)):
        # Linear interpolation for fractional delays
        delayed_signals[i] = np.interp(
            np.arange(len(sig)) - delay, 
            np.arange(len(sig)), 
            sig
        )
    
    return np.sum(delayed_signals, axis=0)

def compute_coherence(signal1, signal2):
    """
    Compute coherence between two signals
    
    Args:
        signal1 (np.array): First input signal
        signal2 (np.array): Second input signal
    
    Returns:
        float: Coherence value
    """
    f, Cxy = signal.coherence(signal1, signal2)
    return np.mean(Cxy)