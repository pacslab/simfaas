import numpy as np

def convert_hist_pdf(_values, num_bins):
    values, base = np.histogram(_values, bins=num_bins, density=False)
    bin_size = base[1] - base[0]
    cumulative = np.cumsum(values)
    cumulative = cumulative / cumulative[-1]
    base = np.append([0, base[0]], base[:-1])
    cumulative = np.append([0, 0], cumulative)
    values = np.append([0, 0], values)
    values = values / np.sum(values)
    if bin_size > 0:
        values /= bin_size

    base += bin_size/2

    return base, values, cumulative

