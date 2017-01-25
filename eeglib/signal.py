"""Signal processing utilities."""

import numpy as np
from scipy.fftpack import fft, fftshift, fftfreq


def power_spectrum(t, data):
    """Compute the Fourier power spectrum of the data.

    :param np.ndarray t: Times in s
    :param np.ndarray data: Raw data
    :returns: frequencies, power_spectrum

    """
    fourier = fftshift(fft(data))
    freqs = fftshift(fftfreq(len(fourier), t[1] - t[0]))
    return freqs, np.abs(fourier)**2
