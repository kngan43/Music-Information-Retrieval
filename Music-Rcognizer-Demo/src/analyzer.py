from __future__ import division
import hashlib
import numpy as np
import matplotlib.mlab as mlab
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)
from operator import itemgetter


DEFAULT_FS = 44100
DEFAULT_WINDOW_SIZE = 4096
DEFAULT_OVERLAP_RATIO = 0.5
DEFAULT_FAN_VALUE = 15
DEFAULT_AMP_MIN = 20
PEAK_NEIGHBORHOOD_SIZE = 20
MAX_HASH_TIME_DELTA = 200
FINGERPRINT_REDUCTION = 20

def fingerprint(channel_samples, Fs=DEFAULT_FS,
                wsize=DEFAULT_WINDOW_SIZE,
                wratio=DEFAULT_OVERLAP_RATIO,
                fan_value=DEFAULT_FAN_VALUE,
                amp_min=DEFAULT_AMP_MIN):
    # compute a spectrogram
    arr2D = mlab.specgram(
        channel_samples,
        NFFT=wsize,
        Fs=Fs,
        window=mlab.window_hanning,
        noverlap=int(wsize * wratio))[0]

    arr2D = 10 * np.log10(replace_zero_with_min(arr2D))
    arr2D[arr2D == -np.inf] = 0 

    local_maxima = peak_finding(arr2D, amp_min=amp_min)

    return generate_hashes(local_maxima, fan_value=fan_value)

# peak finding algorithm
def peak_finding(arr2D, amp_min=DEFAULT_AMP_MIN):
    # find peaks matrix
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D

    # eliminate "zero area" in our peaks matrix
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood,
                                       border_value=1)
    detected_peaks = local_max ^ eroded_background

    # peaks amplitudes
    amps = arr2D[detected_peaks]
    # peaks row indexs, and column indexs
    j, i = np.where(detected_peaks)
    amps = amps.flatten()
    
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min] 

    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    # return peak amplitude and time idx
    return zip(frequency_idx, time_idx)

def generate_hashes(peaks, fan_value=DEFAULT_FAN_VALUE):
    peaks = list(peaks)
    peaks.sort(key=itemgetter(1))

    for i in range(len(peaks)):
      for j in range(1, fan_value):
        if (i + j) < len(peaks):
          freq1 = peaks[i][0]
          freq2 = peaks[i + j][0]
          
          t1 = peaks[i][1]
          t2 = peaks[i + j][1]
          t_delta = t2 - t1
          # generate hashes
          if t_delta >= 0 and t_delta <= MAX_HASH_TIME_DELTA:
            result = "{freq1}|{freq2}|{delta}".format(freq1=freq1, freq2=freq2, delta= t_delta)
            result = result.encode('utf-8')
            h = hashlib.sha1(result)
            yield (h.hexdigest()[0:FINGERPRINT_REDUCTION],
                   t1)

# replace zero with min value
def replace_zero_with_min(data):
  min_nonzero = np.min(data[np.nonzero(data)])
  data[data == 0] = min_nonzero
  return data