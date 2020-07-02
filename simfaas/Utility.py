import numpy as np

def convert_hist_pdf(_values, num_bins):
    """convert_hist_pdf converts the histogram resulting from _values and
num_bins to a density plot by dividing the probability of falling into a
bin by the bin size, converting the values to density. The resulting values
could be plotted and compared with the analytical pdf and cdf functions.

    Parameters
    ----------
    _values : list[float]
        A list of values that we want to analyze and calculate the histogram for
    num_bins : int
        Number of bins used for generating the histogram

    Returns
    -------
    list[float], list[float], list[float]
        base, values, cumulative are returned which are the histogram bases, density values, and cumulative densities which can be compared with the analytical cdf function
    """
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

