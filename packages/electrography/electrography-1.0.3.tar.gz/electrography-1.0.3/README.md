electrography
=============

This Python package is intended for use with OpenBCI boards and/or their data. You can use it to stream data from any of the OpenBCI boards, add triggers to data files, and to analyse the results.

Dependencies
------------

- [BrainFlow](https://brainflow.org/)
- [Matplotlib](https://matplotlib.org/)
- [NumPy](https://numpy.org/)
- [SciPy](https://scipy.org/)

Citation
--------

A tutorial paper associated with this package will be made avalable soon. Please cite this if you use **electrography** in your work.

- *Citation to follow!*

Example Data Acquisition
========================

```.python
import time
from electrography.boards import OpenBCI

# Create a new OpenBCI instance, in this example for a Ganglion board.
# Note that the `serial_port` address may be different on your system!
board = OpenBCI("ganglion", serial_port="/dev/ttyACM0", \
    log_file="example_egg.tsv")

# Stream for 30 seconds, sending a trigger after 1 second.
board.start_stream()
time.sleep(1)
board.trigger(200)
time.sleep(29)
board.stop_stream()

# Close the connection
board.close()
```

Example Data Analysis
=====================

```.python
from openbci.data import read_file, get_physiology, hampel, butter_bandpass_filter, movement_filter

raw = read_file(fpath)
data, t, triggers, sampling_rate = get_physiology(raw, "ganglion")

# Mean-centre the data.
m_per_channel = numpy.nanmean(data, axis=1, keepdims=True)
data = data - m_per_channel

# Hampel-filter the data.
data = hampel(data, k=2000, n_sigma=3)

# Filter the data for electrogastrography (EGG) frequencies (1-10 cpm).
for channel in range(data.shape[0]):
    data[channel,:] = butter_bandpass_filter(data[channel,:], \
        0.0083, 0.17, sampling_rate, bidirectional=True)

# Employ a movement filter for frequencies below the normogastric frequency 
# (3 cpm, 0.05 Hz).
data, noise = movement_filter(data, sampling_rate, freq=0.05, window=1.0)
```

