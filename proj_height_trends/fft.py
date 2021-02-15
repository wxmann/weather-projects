from scipy import fftpack
import numpy as np


def power_spectrum(ds, sample_spacing):
    sig_fft = fftpack.fft(ds)
    power = np.abs(sig_fft) ** 2
    sample_freq = fftpack.fftfreq(ds.size, sample_spacing)
    positive_freq = sample_freq > 0
    return sample_freq[positive_freq], power[positive_freq]


def freq_filter(ds, freq_exclude, sample_spacing):
    sig_fft = fftpack.fft(ds)
    sample_freq = fftpack.fftfreq(ds.size, sample_spacing)
    filter = freq_exclude(sample_freq)
    sig_fft[filter] = 0
    ds_pass = np.real(fftpack.ifft(sig_fft))
    return ds_pass