"""Signal processing utilities."""

import numpy as np
from scipy.fftpack import fft, fftshift, fftfreq
from scipy import signal


def power_spectrum(t, data):
    """Compute the Fourier power spectrum of the data.

    :param np.ndarray t: Times in s
    :param np.ndarray data: Raw data
    :returns: frequencies, power_spectrum

    """
    fourier = fftshift(fft(data))
    freqs = fftshift(fftfreq(len(fourier), t[1] - t[0]))
    return freqs, np.abs(fourier)**2


def bandstop_filter(data, sample_rate, freq, width=2, order=4):
    """Apply a bandstop filter.

    :param array-like data: Data
    :param float sample_rate: Data sample rate [Hz]
    :param float freq: Center frequency to filter [Hz]
    :param float width: Width of filter [Hz] (default: 2)
    :param int order: Filter order (default: 4)

    """
    nyq = 0.5 * sample_rate
    low, high = (freq - width) / nyq, (freq + width) / nyq
    b, a = signal.butter(order, (low, high), btype="bandstop")
    return signal.lfilter(b, a, data)


def line_filter(data, sample_rate, order=4, line_freq=60.0, width=2.0):
    """Remove ac line noise from the data. This simply calls
    :func:`bandstop_filter` with the center frequency 60 Hz (default) and a
    width of 2 Hz.

    :param array-like data: Data
    :param float sample_rate: Data sample rate [Hz]
    :param int order: Filter order (default: 4)
    :param float line_freq: Line frequency [Hz] (default: 60 Hz)
    :param float width: Width to filter by [Hz] (default: 2 Hz)
    :returns: Filtered data

    """
    return bandstop_filter(data, sample_rate, line_freq, width, order)
