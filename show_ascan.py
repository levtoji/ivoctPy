import os.path
import sys

import matplotlib.pyplot as plt
import numpy as np
from skimage import filters, feature


def load_data():
    """Load binary data into scaled matrix."""
    file_name = sys.argv[1]
    if os.path.isfile(file_name):
        f = open(file_name, "r")
        # Load file from binary file
        a = np.fromfile(f, np.float32, sep="")
        # Reshape to matrix dimensions
        a = np.reshape(a, (512, np.size(a) // 512), order='F')
        a = scale_interval_zero_one(a)
        return a
    else:
        print("Error loading file.")
        return -1


def scale_interval_zero_one(matrix):
    """Scale matrix values down to interval [0, 1]."""
    matrix = np.array(matrix)
    min_v = np.min(matrix)
    max_v = np.max(matrix)
    quotient = 1.0 / (max_v - min_v)
    return matrix * quotient


def remove_second_column(matrix):
    """Remove every second column of the matrix."""
    new_matrix = np.empty((np.shape(matrix)[0], np.shape(matrix)[1] // 2))
    for i in range(0, np.shape(matrix)[1]):
        if i % 2 == 0:
            new_matrix[:, (i - 1) // 2] = matrix[:, i]
    return new_matrix


def find_peaks(matrix):
    """Find peaks from matrix showing a sinus curve."""
    debug = False
    min_width = 850
    max_width = 1400

    skin_layer_cut = matrix[85:120, :]
    skin_layer_med = filters.median(skin_layer_cut, np.ones([5, 5]))
    skin_layer = feature.canny(skin_layer_med, sigma=1)

    if debug:
        plt.figure(), plt.imshow(skin_layer_med)
        plt.figure(), plt.imshow(skin_layer)
        plt.figure(), plt.imshow(skin_layer)

    skin_layer_shape = np.shape(skin_layer)
    peaks = []
    min_value = skin_layer_shape[0]

    # Find first peak
    for c in range(0, 800):
        for a in range(skin_layer_shape[0] - 1, 0, -1):
            if skin_layer[a, c] and a < min_value:
                min_value = a
                peak_at = c
    peaks.append(peak_at)

    # Find following peaks
    while peak_at + max_width < skin_layer_shape[1]:
        min_value = skin_layer_shape[0]
        temp_matrix = skin_layer[:, peaks[-1] + min_width: peaks[-1] + max_width]
        for c in range(0, np.shape(temp_matrix)[1]):
            for a in range(skin_layer_shape[0] - 1, 0, -1):
                if skin_layer[a, c] and a < min_value:
                    min_value = a
                    peak_at = c
        peak_at = peaks[-1] + min_width + peak_at
        peaks.append(peak_at)
    print("Found peaks: " + str(peaks))

    for i in peaks:
        skin_layer[:, i] = 1
    plt.figure(), plt.imshow(skin_layer)
    return peaks


def main():
    raw_matrix = load_data()
    sliced_matrix = raw_matrix[:, 0:5000]
    # plt.figure(), plt.imshow(sliced_matrix)
    peaks = find_peaks(sliced_matrix)


if __name__ == "__main__":
    main()
    # Really important for showing of plot.
    plt.show(block=True)
