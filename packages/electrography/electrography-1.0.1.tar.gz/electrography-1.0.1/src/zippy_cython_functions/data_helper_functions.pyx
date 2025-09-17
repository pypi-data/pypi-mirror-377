from statistics import median
import numpy
cimport cython

DTYPE = numpy.float64

@cython.boundscheck(False)
@cython.wraparound(False)
def mean(double[::1] a):
    cdef int n, i
    cdef double s, m
    # Count the number of samples in this array.
    n = len(a)
    # Compute the sum of the array.
    s = 0
    for i in range(n):
        s += a[i]
    # Compute the average.
    m = s / n
    return m

@cython.boundscheck(False)
@cython.wraparound(False)
def var(double[::1] a, double m):
    cdef int n, i
    cdef double s, v
    # Count the number of samples in this array.
    n = len(a)
    # Compute the sum of the array.
    s = 0
    for i in range(n):
        s += (a[i] - m)**2
    v = s / n
    return v

@cython.boundscheck(False)
@cython.wraparound(False)
def mad(double[::1] a, double m):
    cdef int n, i
    cdef double mad
    n = len(a)
    cdef double[::1] d = numpy.zeros(n)
    for i in range(n):
        d[i] = abs(a[i] - m)
    mad = median(d)
    return mad


@cython.boundscheck(False)
@cython.wraparound(False)
def hampel(double[::1] data, int k, double n_sigma):

    cdef Py_ssize_t n_samples = data.shape[0]
    cdef double[::1] data_view = data

    cdef int i, j, si, ei, win_len
    cdef double med, d_med, sd, threshold, dev

    win_len = 2*k + 1
    signal = numpy.zeros(n_samples, dtype=DTYPE)
    cdef double[::1] signal_view = signal

    for i in range(n_samples):
        si = max(i-k, 0)
        ei = min(i+k, n_samples)
        med = median(data_view[si:ei])
        d_med = mad(data_view[si:ei], med)

        sd = 1.4826 * d_med
        threshold = n_sigma * sd

        dev = abs(data_view[i]-med)
        if dev > threshold:
            signal_view[i] = med
        else:
            signal_view[i] = data_view[i]

    return signal


# The implementation for this movement filter comes from:
# Gharibans, Smarr, Kunkel, Kriegsfeld, Mousa, & Coleman (2018). Artifact 
#   Rejection Methodology Enables Continuous, Noninvasive Measurement of 
#   Gastric Myoelectric Activity in Ambulatory Subjects. Scientific Reports,
#   8:5019, doi:10.1038/s41598-018-23302-9
# Because we only use positive indices that are within the bounds of each
# array, we can deactivate bounds checking and wrap arounds. Deactivating
# these checks speeds up array lookups.
@cython.boundscheck(False)
@cython.wraparound(False)
def movement_filter(double[::1] data, double sfreq, double freq, double window):

    # Count the number of samples in this array.
    cdef Py_ssize_t n_samples = data.shape[0]

    # Create a memory view for the data.
    cdef double[::1] data_view = data
    
    # Compute the window size in seconds.
    cdef double win_sec = window * (1.0 / freq)
    # Compute the window size in samples.
    cdef double win = win_sec * sfreq
    cdef int win_half = round(win//2)

    # Loop through the data to compute the average and variance in all windows.
    cdef int i, si, ei
    e_y = numpy.zeros(n_samples, dtype=DTYPE)
    var_y = numpy.zeros(n_samples, dtype=DTYPE)
    cdef double[::1] e_y_view = e_y
    cdef double[::1] var_y_view = var_y
    for i in range(n_samples):
        # Compute the start and end index of the current window. We correct
        # any windows that fall before the start or after the end of the data.
        si = max(0, i-win_half)
        ei = min(n_samples, i+win_half)
        e_y_view[i] = mean(data_view[si:ei])
        var_y_view[i] = var(data_view[si:ei], e_y_view[i])

    # Compute an estimate of the variance for the signal of interest, as the 
    # average of all local variances for each window.
    cdef double var_e
    var_e = mean(var_y)

    # Loop through the data again, this time to compute the predicted noise.
    cdef double a, b, d
    x_hat = numpy.zeros(n_samples, dtype=DTYPE)
    cdef double[::1] x_hat_view = x_hat
    for i in range(n_samples):
        a = max(0, var_y_view[i] - var_e)
        b = max(var_e, var_y_view[i])
        d = data_view[i] - e_y_view[i]
        x_hat_view[i] = e_y_view[i] + ((a / b) * d)
        
    return x_hat


