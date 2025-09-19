#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from multiprocessing import Process, Queue
import queue
import tempfile
import time

import numpy
import scipy.fft
from scipy.optimize import minimize
import scipy.signal
from sklearn.decomposition import FastICA

from brainflow.board_shim import BoardShim, BoardIds
from brainflow.data_filter import DataFilter

# Check if we can load the sped-up statically-typed functions.
try:
    from .data_helper_functions import hampel as hampel_cython
    from .data_helper_functions import movement_filter as movement_filter_cython
    _cython_function_available = True
    print("Successfully loaded Cythonised functions!")
except:
    _cython_function_available = False
    print("WARNING: Could not load Cythonised functions!")


def _run_single_channel(cython_function, channel_data, i, data_queue, *args):
    args = [channel_data] + list(*args)
    signal = cython_function(*args)
    data_queue.put([i,signal])
    return 0


def _parallelise_cython(data, cython_function, *args):
    n_jobs = data.shape[0]
    data_queue = Queue()
    processes = []
    for i in range(n_jobs):
        p = Process(target=_run_single_channel, \
            args=(cython_function, data[i,:], i, data_queue, *args))
        p.name = "cython_func_channel_{}".format(i)
        p.start()
        processes.append(p)

    n_jobs_finished = 0
    signal = numpy.zeros(data.shape, dtype=data.dtype)
    while n_jobs_finished < n_jobs:
        if not data_queue.empty():
            try:
                i, s = data_queue.get()
                signal[i,:] = s
                n_jobs_finished += 1
            except queue.Empty:
                pass
        time.sleep(0.1)

    for p in processes:
        p.join(1.0)
        if p.is_alive():
            p.kill()

    return signal


def read_file(fpath, reuse=False):

    """Loads data from a text file using the BrainFlow API. In order to do so,
    the file is first copied into a temporary file which does not include the
    header. (This is a bit of a hack, as the header is very useful for human
    readability and understanding what is in the file, but the BrainFlow
    routines choke on it.)
    
    Arguments
    fpath:
        type: str
        desc: Path to the data file from which data needs loading.
    
    Keyword Arguments
    reuse:
        type: bool
        desc: If a temporary copy of the current file already exists, reuse it
            instead of creating a new temp file. If you're loading different
            files with the same base name (i.e. in different folders), you
            should set this to False. (Default = True)
    
    Returns
    data:
        type: numpy.ndarray
        desc: NumPy array with shape (M,N), where M is the number of recorded
            channels, and N the number of samples.
    """
    
    with open(fpath, "r") as f:
        lines = f.readlines()
        lines.pop(0)
    name, ext = os.path.splitext(os.path.basename(fpath))
    tmp = os.path.join(tempfile.gettempdir(), "{}{}".format(name, ext))
    if (not os.path.isfile(tmp)) or (not reuse):
        if not reuse:
            i = 0
            while os.path.isfile(tmp):
                i += 1
                tmp = os.path.join(tempfile.gettempdir(), \
                    "{}-{}{}".format(name, i, ext))
        with open(tmp, "w") as f:
            f.writelines(lines)
    data = DataFilter.read_file(tmp)

    return data


def get_physiology(raw, board):
    
    """Separates the physiological data from a full BrainFlow data array. It
    returns the electrophysiology channels, time channel, and also the
    sampling rate (this is from the board description; you might want to check
    it against the actual timestamps from the time channel).
    
    Arguments
    raw:
        type: numpy.ndarray
        desc: NumPy array with shape (M,N), where M is the number of recorded
            channels, and N the number of samples. (Usually loaded directly
            through this module's read_file function.)

    board:
        type: str
        desc: Name of the OpenBCI board. Choose from "ganglion", "cyton",
            "cyton-daisy", "ganglion_wifi", "cyton_wifi", or 
            "cyton-daisy_wifi".
    
    Retuns
    data:
        type: numpy.ndarray
        desc: NumPy array with shape (M,N), where M is the number of physiology
            channels, and N the number of samples.
    
    time:
        type: numpy.ndarray
        desc: NumPy array with shape (1,N), where N is the number of samples.
    
    markers:
        type: numpy.ndarray
        desc: NumPy array with shape (1,N), where N is the number of samples.
    
    sampling_rate:
        type: int
        desc: Sampling frequency for the board. (From the board description;
            check timestamps in time to compute empirical sampling rate.)
    """
    
    if board == "ganglion":
        board_id = BoardIds.GANGLION_BOARD
    elif board == "cyton":
        board_id = BoardIds.CYTON_BOARD
    elif board == "cyton-daisy":
        board_id = BoardIds.CYTON_DAISY_BOARD
    elif board == "ganglion_wifi":
        board_id = BoardIds.GANGLION_WIFI_BOARD
    elif board == "cyton_wifi":
        board_id = BoardIds.CYTON_WIFI_BOARD
    elif board == "cyton-daisy_wifi":
        board_id = BoardIds.CYTON_DAISY_WIFI_BOARD

    # Get the board description for sample rate and channel indices.
    descr = BoardShim.get_board_descr(board_id)
    sampling_rate = descr["sampling_rate"]

    # Get the timestamps.
    ti = descr["timestamp_channel"]
    t = numpy.copy(raw[ti,:])
    
    # Get the markers.
    mi = descr["marker_channel"]
    m = numpy.copy(raw[mi,:])
    
    # Get the data from the physiological channels.
    pi = descr["eeg_channels"]
    data = numpy.copy(raw[pi,:])

    return data, t, m, sampling_rate


def _butter_bandpass(high_pass, low_pass, sampling_rate, order=5, sos=True):
    nyq = 0.5 * sampling_rate
    low = high_pass / nyq
    high = low_pass / nyq
    if sos:
        output = "sos"
    else:
        output = "ba"
    filt = scipy.signal.butter(order, [low, high], analog=False, \
        btype='band', output=output)
    return filt

def butter_bandpass_filter(data, high_pass, low_pass, sampling_rate, order=5, \
    bidirectional=True):
    
    """Performs a Butterworth filter using cascaded second-order sections 
    (sos), which is a digital IIR (infinite impulse response) filter. The 
    filter can be applied unidirectionally (only forwards) or bidirectionally 
    (forwards and again backwards). The bidirectional option is for zero-lag 
    (zero-phase) filtering, which should be used if you care about the timing 
    of signals across different frequency bands (e.g. if you're comparing an 
    ECG signal with an EEG signal).
    
    Arguments
    
    data:
        type: numpy.ndarray
        desc: a NumPy array with shape (M,N), where M is the number of 
            channels and N the number of samples.

    high_pass:
        type: float
        desc: The frequency (in Hz) above which data will be let through. This 
            is the lower cutoff of the band through which signal is allowed.

    low_pass:
        type: float
        desc: The frequency (in Hz) below which data will be let through. This 
            is the higher cutoff of the band through which signal is allowed.

    sampling_rate:
        type: float
        desc: The sampling rate (in Hz) that the passed data was acquired with.

    Keyword Arguments

    order:
        type: int
        desc: The order of the filter. See scipy.signal.iirfilter for details 
            on the implementation. (Default = 5)

    bidirectional:
        type: bool
        desc: When set to True, the data will be run through the filter twice: 
            one forwards and once in reverse. This ensures zero-lag, which is 
            crucial for comparisons between signals that are filtered through 
            different bands. (Default = True)
    """
    
    sos = _butter_bandpass(high_pass, low_pass, sampling_rate, order=order, \
        sos=True)
    if bidirectional:
        signal = scipy.signal.sosfiltfilt(sos, data)
    else:
        signal = scipy.signal.sosfilt(sos, data)
    return signal


def hampel(*args, **kwargs):
    """For documentation, see hampel_filter. This function exists for
    backwards compatability, as `hampel_filter` used to be `hampel`.
    """
    return hampel_filter(*args, **kwargs)

def hampel_filter(data, k=3, n_sigma=3.0, force_python=False):

    """Performs a Hampel filtering, a median based outlier rejection in which
    outliers are detected based on a local median, and are replaced by that
    median (local median is determined in a moving window).
    
    Arguments
    
    data:
        type: numpy.ndarray
        desc: a NumPy array with shape (M,N), where M is the number of 
            channels and N the number of samples.

    Keyword Arguments

    k:
        type: int
        desc: Number of neighbours on either side of a sample with which a 
            local median is computed. The window length for computing a median 
            is thus 2k+1. (Default = 3)
    
    n_sigma:
        type: float
        desc: Number of standard deviations a sample can be away from a local
            median before it is replaced by that local median. (Default = 3)
    
    force_python:
        type: bool
        desc: This function has a Cython and a Python implementation. Setting 
            force_python to True ensures that the Python implementation is 
            used. This is likely slower, although the Hampel filter is 
            actually faster in Python for very large windows. (Default = False)
    """
    
    # Use the sped-up cython function if available.
    if _cython_function_available and not force_python:
        if len(data.shape) == 1:
            signal = hampel_cython(data, k, n_sigma)
        else:
            signal = _parallelise_cython(data, hampel_cython, [k, n_sigma])
        return signal
    # Fall back on the (slower) Python function if we can't use the speedy one.
    else:
        return hampel_python(data, k=k, n_sigma=n_sigma)

def hampel_python(data, k=3, n_sigma=3.0):
    
    # Create a local copy of the data in which values will be filtered.
    signal = numpy.copy(data)
    
    # Get the shape of the data.
    n_channels, n_samples = signal.shape

    # Slide the window across the data.
    for i in range(0, n_samples):
        # Compute the start and end index of the current window. We correct
        # any windows that fall before the start or after the end of the data.
        si = max(0, i-k)
        ei = min(n_samples, i+k)
        # Compute the median in this window.
        med = numpy.nanmedian(data[:,si:ei], axis=1)
        # Compute the absolute deviation of data and local median.
        d = numpy.abs(data[:, si:ei] - med.reshape(-1,1))
        # Compute the median absolute deviation, and scale by a factor of 
        # kappa (roughly equal to 1.4826). This is an estimation of the 
        # standard deviation.
        sd = 1.4826 * numpy.median(d, axis=1)
        # Replace outliers by the median.
        replace = numpy.abs(data[:,i]-med) > n_sigma*sd
        signal[replace,i] = med[replace]
    
    return signal


def mad_filter(data, n_sigma=3.0):

    """Filters on the basis of mean absolute deviation (MAD), replacing values
    that deviate too far from the median by the median. This is akin to what
    happens within the window of a Hampel filter, but without its window 
    sliding across the timeseries. This makes the MAD filter much faster but
    also more sensitive to signal drift.
    
    Arguments
    
    data:
        type: numpy.ndarray
        desc: a NumPy array with shape (M,N), where M is the number of 
            channels and N the number of samples.

    Keyword Arguments

    n_sigma:
        type: float
        desc: Number of standard deviations a sample can be away from the
            median before it is replaced by that local median. (Default = 3)
    """
    
    signal = numpy.copy(data)
    med = numpy.nanmedian(signal, axis=1, keepdims=True)
    d = numpy.abs(signal - med)
    d_med = numpy.nanmedian(d, axis=1)
    sd = 1.4826 * d_med
    threshold = n_sigma * sd
    for channel in range(signal.shape[0]):
        replace = d[channel,:] > threshold[channel]
        signal[channel,replace] = med[channel]
    
    return signal


def movement_filter(data, sampling_rate, frequency_of_interest, window=1.0, \
    force_python=False):

    """Applies an LMMSE filter to reduce movement artefacts. For details of 
    this procedure, see:
    Gharibans, Smarr, Kunkel, Kriegsfeld, Mousa, & Coleman (2018). Artifact 
        Rejection Methodology Enables Continuous, Noninvasive Measurement of 
        Gastric Myoelectric Activity in Ambulatory Subjects. Scientific 
        Reports, 8:5019, doi:10.1038/s41598-018-23302-9
    
    Arguments
    
    data:
        type: numpy.ndarray
        desc: A NumPy array with shane (M,N) where M is the number of channels
           and N the number of observations (samples).
    
    sampling_rate:
        type: float
        desc: Sampling frequency for the board. (From the board description; or
            check timestamps in time array to compute empirical sampling rate.)

    frequency_of_interest:
        type: float
        desc: Frequency of interest in Herz. For example, in gastric signal 
        the main frequency is 3 cycles per minute, which is 0.05 Hz.
    
    Keyword Arguments

    window:
        type: float
        desc: Window length in cylces of the frequency of interest. (Default 
            is 1.0)
    
    force_python:
        type: bool
        desc: This function has a Cython and a Python implementation. Setting 
            force_python to True ensures that the Python implementation is 
            used. Note that this will be much slower. (Default = False)
    """

    # Use the sped-up cython function if available.
    if _cython_function_available and not force_python:
        if len(data.shape) == 1:
            x_hat = movement_filter_cython(data, sampling_rate, \
                frequency_of_interest, window)
        else:
            x_hat = _parallelise_cython(data, movement_filter_cython, \
                [sampling_rate, frequency_of_interest, window])
        signal = data - x_hat
        return signal, x_hat
    # Fall back on the (slower) Python function if we can't use the speedy one.
    else:
        return movement_filter_python(data, sampling_rate, \
            freq=frequency_of_interest, window=window)

# This is a Python implementation for the movement filter from:
# Gharibans, Smarr, Kunkel, Kriegsfeld, Mousa, & Coleman (2018). Artifact 
#   Rejection Methodology Enables Continuous, Noninvasive Measurement of 
#   Gastric Myoelectric Activity in Ambulatory Subjects. Scientific Reports,
#   8:5019, doi:10.1038/s41598-018-23302-9
def movement_filter_python(data, sfreq, freq=0.05, window=1.0):

    # Compute the window size in seconds.
    win_sec = window * (1.0 / freq)
    # Compute the window size in samples.
    win = win_sec * sfreq
    win_half = int(win//2)

    # Compute the start and end indices.
    si = 0 + win_half
    ei = data.shape[1] - win_half
    # Loop through the data to compute the average and variance in all windows.
    e_y = numpy.zeros(data.shape, dtype=numpy.float64)
    var_y = numpy.zeros(data.shape, dtype=numpy.float64)
    for i in range(0, data.shape[1]):
        if i < si:
            si_ = 0
        else:
            si_ = i - win_half
        if i > ei:
            ei_ = data.shape[1]
        else:
            ei_ = i + win_half
        y = data[:,si_:ei_]
        e_y[:,i] = numpy.mean(y, axis=1)
        var_y[:,i] = numpy.var(y, axis=1)

    # Compute an estimate of the variance for the signal of interest, as the 
    # average of all local variances for each window.
    var_e = numpy.mean(var_y, axis=1)

    # Loop through the data again, this time to compute the predicted noise.
    x_hat = numpy.zeros(data.shape, dtype=numpy.float64)    
    for i in range(0, data.shape[1]):
        a = var_y[:,i] - var_e
        below_zero = a < 0
        if numpy.any(below_zero):
            a[below_zero] = 0.0
        b = var_y[:,i]
        below_e_var = b < var_e
        if numpy.any(below_e_var):
            b[below_e_var] = var_e[below_e_var]
        x_hat[:,i] = e_y[:,i] + (a / b) * (data[:,i] - e_y[:,i])
    
    e = data - x_hat
    
    return e, x_hat


def ica_denoise(data, sampling_rate, high_pass, low_pass, bounds_of_interest, \
    snr_threshold=3.0, random_state=None):

    """This function denoises the data by decomposing it using independent 
    component analysis. For each component, the peak power within the bounds 
    of interest is considered the signal. The noise is computed as the average 
    power outside of the bounds of interest. Components with a signal-to-noise 
    ratio below the set threshold will be zero'd out. After this, the signal 
    is reconstituted into its original space.
    
    Arguments
    
    data:
        type: numpy.ndarray
        desc: a NumPy array with shape (M,N), where M is the number of 
            channels and N the number of samples.

    sampling_rate:
        type: float
        desc: The sampling rate (in Hz) that the passed data was acquired with.

    high_pass:
        type: float
        desc: The frequency (in Hz) above which data will be let through. This 
            is the lower cutoff of the band through which signal is allowed.

    low_pass:
        type: float
        desc: The frequency (in Hz) below which data will be let through. This 
            is the higher cutoff of the band through which signal is allowed.
    
    bounds_of_interest:
        type: list
        desc: The frequencies (in Hz) between which data is considered 
            "signal". For example, in electrogastrography this would be 
            2-4 cpm, so in Hz you would pass [0.033, 0.067]

    Keyword Arguments

    snr_threshold:
        type: float
        desc: The signal-to-noise threshold below which components will be
            excluded. (Default = 3.0)

    random_state:
        type: int
        desc: The random seed that will be used for the FastICA initialisation. 
            FastICA is stochastic, but passing a number allows for reproducible
            results. Pass None to not set a random state. (Default = None)
    """

    # Do an ICA decomposition of the signal. Note that this requires 
    # transposing the data from (n_channels, n_samples) to 
    # (n_samples, n_channels) to work with the FastICA class.
    ica = FastICA(random_state=random_state)
    ica_components = ica.fit_transform(data.T).T
    # Loop through all identified components.
    n_filtered_channels = 0
    for channel in range(ica_components.shape[0]):
        # Compute the signal magnitude for this component.
        f, p = compute_signal_magnitude(ica_components[channel,:], \
            ica_components.shape[1], sampling_rate, high_pass, low_pass)
        # Compute peak power in between the bounds of interest. This is 
        # considered the "signal".
        sel = (f >= bounds_of_interest[0]) & (f <= bounds_of_interest[1])
        p_signal = numpy.nanmax(p[sel])
        # Compute the mean power outside of the bounds of interest. This is
        # considered the "noise".
        p_noise = numpy.nanmean(p[numpy.invert(sel)])
        # Zero out this component if the signal-noise ratio is too low.
        snr = p_signal / p_noise
        if snr < snr_threshold:
            ica_components[channel,:] = 0.0
            n_filtered_channels += 1
    # Check if we have any components left.
    ica_denoising_success = n_filtered_channels < data.shape[0]
    if ica_denoising_success:
        # Recombine the components into the original signal space now that
        # non-gastric components have been filtered out.
        signal = ica.inverse_transform(ica_components.T).T
        # Due to previous transposition, we need to ensure the array is
        # C-contiguous. This is necessary for our Cythonised functions, which 
        # assume C-contiguous arrays for improved efficiency. (This step is 
        # optional if you do not use the Cythonised functions, but it does not 
        # take up much time, so for safety it's applied per default.)
        signal = numpy.ascontiguousarray(signal)
    else:
        signal = None
    
    return signal


def compute_signal_magnitude(signal, n, sampling_rate, high_pass, low_pass):
    # If the number of samples in the signal is fewer than the anticipated 
    # number, it will be zero-padded. In this case, applying a filter to 
    # the signal directly is fine. However, if there are more samples, the
    # signal will be truncated. In this case, part of the window would 
    # also be truncated. Hence, we need to truncate the signal first, and 
    # then the window will be safely applied.
    signal = numpy.copy(signal)
    if signal.shape[0] > n:
        signal = signal[:n]
    # Apply a Hanning window to the signal to prevent edge artefacts.
    w = numpy.hanning(signal.shape[0])
    signal = signal * w
    # Compute the fast Fournier transform.
    p = scipy.fft.rfft(signal, n=n)
    f = scipy.fft.rfftfreq(n, 1.0 / sampling_rate)
    # Take absolute values, and scale by half the window.
    p = numpy.abs(p) * 2.0 / numpy.sum(w)
    # Select only the frequencies within our filter.
    sel = (f >= high_pass) & (f <= low_pass)
    
    return f[sel], p[sel]


def spectrogram(data, sampling_rate, segment_secs, mode="magnitude"):
    
    n_per_segment = round(segment_secs * sampling_rate)

    if (len(data.shape) == 1):
        freqs, times, power = scipy.signal.spectrogram(data, \
            sampling_rate=sampling_rate, nperseg=n_per_segment, scaling="spectrum", \
            mode=mode)
    else:
        freqs, times, power_ = scipy.signal.spectrogram(data[0,:], \
            sampling_rate=sampling_rate, nperseg=n_per_segment, scaling="spectrum", \
            mode=mode)
        shape = (data.shape[0], power_.shape[0], power_.shape[1])
        power = numpy.zeros(shape, dtype=numpy.float64)
        power[0,:,:] = power_
        for channel in range(1, data.shape[0]):
            _, _, power[channel,:,:] = scipy.signal.spectrogram( \
                data[channel,:], sampling_rate=sampling_rate, \
                nperseg=n_per_segment, scaling="spectrum", mode=mode)
    
    return freqs, times, power


def fit_sine(signal, sampling_rate, signal_freq=None):
    
    # Construct the time array for the passed signal.
    n_samples = signal.shape[0]
    dt = 1.0 / sampling_rate
    dur = n_samples * dt
    t = numpy.linspace(0.0, dur, n_samples)
    
    # Set the parameters up for fitting the main signal frequency.
    if signal_freq is None:
        initial_guess = [10.0, 0.0, 1.0]
        bounds = [(0.0, None), (-numpy.pi, numpy.pi), (None, None)]
    # Set the parameters up for using a predetermined frequency.
    else:
        initial_guess = [0.0, 1.0]
        bounds = [(-numpy.pi, numpy.pi), (None, None)]
    
    # Fit the sine wave.
    model = minimize(sine_residuals, initial_guess, \
        args=(t, signal, signal_freq), method="L-BFGS-B", \
        bounds=bounds)
    
    # Extract the parameters.
    if model.x.shape[0] == 2:
        freq = signal_freq
        phase, amp = model.x
    else:
        freq, phase, amp = model.x
    
    return freq, phase, amp

def sine(x, freq, phase, amp):
    y = amp * numpy.sin(2*numpy.pi * freq * x + phase)
    return y

def sine_residuals(betas, x, y, signal_freq):
    # Collect the parameters.
    if betas.shape[0] == 3:
        freq, phase, amp = betas
    else:
        freq = signal_freq
        phase, amp = betas
    # Compute predicted signal.
    y_pred = sine(x, freq, phase, amp)
    # Compute residuals.
    res = y - y_pred
    # Return the sum of squared residuals.
    return numpy.nansum(res**2)

