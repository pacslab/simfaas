import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import expon, poisson, norm

from simfaas.Utility import convert_hist_pdf

# import warnings
# warnings.simplefilter(action='ignore', category=FutureWarning)
# warnings.simplefilter(action='ignore', category=NotImplementedError)
# import modin.pandas as pd

class SimProcess:
    """SimProcess gives us a single interface to simulate different processes.
This will later on be used to simulated different processes and compare them agaist a
custom analytical model. In the child class, after performing `super().__init__()`,
properties `self.has_pdf` and `self.has_cdf` by default value of `False` will
be created. In case your class has the proposed PDF and CDF functions available,
you need to override these values in order for your model PDF to show up in the output
plot.
    """
    def __init__(self):
        super().__init__()
        # if your class has pdf or cdf functions, switch the booleans to True
        self.has_pdf = False
        self.has_cdf = False

    def pdf(self, x):
        """pdf function is called for visualization for classes with `self.has_pdf = True`.

        Parameters
        ----------
        x : float
            The time for which the pdf value (density) should be returned

        Raises
        ------
        NotImplementedError
            By default, this function raises NotImplementedError unless overriden by a child class.
        """
        raise NotImplementedError

    def cdf(self, x):
        """cdf function is called for visualization for classes with `self.has_cdf = True`.

        Parameters
        ----------
        x : float
            The time for which the cdf value (density) should be returned

        Raises
        ------
        NotImplementedError
            By default, this function raises NotImplementedError unless overriden by a child class.
        """
        raise NotImplementedError

    def generate_trace(self):
        """generate_trace function is supposed to be replaced with the override function of each
of the child classes.

        Raises
        ------
        NotImplementedError
            By default, this function raises NotImplementedError unless overriden by a child class.
        """
        raise NotImplementedError

    def visualize(self, num_traces=10000, num_bins=100):
        """visualize function visualizes the PDF and CDF of the simulated process by generating
traces from your function using :func:`~simfaas.SimProcess.SimProcess.generate_trace` and
converting the resulting histogram values (event counts) to densities to be comparable with
PDF and CDF functions calculated analytically.

        Parameters
        ----------
        num_traces : int, optional
            Number of traces we want to generate for calculating the histogram, by default 10000
        num_bins : int, optional
            Number of bins for the histogram which created the density probabilities, by default 100
        """
        traces = np.array([self.generate_trace() for i in range(num_traces)])
        print(f"Simulated Average Inter-Event Time: {np.mean(traces):.6f}")
        print(f"Simulated Average Event Rate: {num_traces / np.sum(traces):.6f}")

        base, hist_values, cumulative = convert_hist_pdf(traces, num_bins)

        plt.figure()
        plt.plot(base, hist_values, label='Sim Hist')
        if self.has_pdf:
            pdf_vals = np.array([0,0] + [self.pdf(x) for x in base[2:]])
            plt.plot(base, pdf_vals, ls='--', label="Model PDF")
        plt.legend()
        plt.grid(True)

        plt.figure()
        plt.plot(base, cumulative, label='Sim Cumulative')
        if self.has_cdf:
            cdf_vals = np.array([0, 0] + [self.cdf(x) for x in base[2:]])
            plt.plot(base, cdf_vals, ls='--', label="Model CDF")
        plt.legend()
        plt.grid(True)


class ExpSimProcess(SimProcess):
    """ExpSimProcess extends the functionality of :class:`~simfaas.SimProcess.SimProcess` for
exponentially distributed processes. This class also implements the `pdf` and `cdf` functions
which can be used for visualization purposes.

    Parameters
    ----------
    rate : float
        The rate at which the process should fire off
    """
    def __init__(self, rate):
        super().__init__()

        self.has_pdf = True
        self.has_cdf = True
        self.rate = rate

    def pdf(self, x):
        return expon.pdf(x, scale=1/self.rate)

    def cdf(self, x):
        return expon.cdf(x, scale=1/self.rate)

    def generate_trace(self):
        return np.random.exponential(1/self.rate)


class ConstSimProcess(SimProcess):
    """ConstSimProcess extends the functionality of :class:`~simfaas.SimProcess.SimProcess` for
constant processes, meaning this is a deterministic process and fires exactly every
`1/rate` seconds. This class does not implement the `pdf` and `cdf` functions.

    Parameters
    ----------
    rate : float
        The rate at which the process should fire off
    """
    def __init__(self, rate):
        super().__init__()

        self.has_pdf = False
        self.has_cdf = False
        self.rate = rate

    def generate_trace(self):
        return 1/self.rate


class GaussianSimProcess(SimProcess):
    """GaussianSimProcess extends the functionality of :class:`~simfaas.SimProcess.SimProcess` for
gaussian processes. This class also implements the `pdf` and `cdf` functions
which can be used for visualization purposes.

    Parameters
    ----------
    rate : float
        The rate at which the process should fire off
    std : float
        The standard deviation of the simulated process
    """
    def __init__(self, rate, std):
        super().__init__()
        self.has_pdf = True
        self.has_cdf = True
        self.rate = rate
        self.std = std

    def generate_trace(self):
        return max(0, np.random.normal(loc=1/self.rate, scale=self.std))

    def pdf(self, x):
        return norm.pdf(x, loc=1/self.rate, scale=self.std)

    def cdf(self, x):
        return norm.cdf(x, loc=1/self.rate, scale=self.std)

if __name__ == "__main__":
    print([ConstSimProcess(rate=5).generate_trace() for _ in range(10)])

    GaussianSimProcess(rate=5, std=0.01).visualize(num_traces=10000, num_bins=100)
    plt.show()

    exp_arr = ExpSimProcess(rate=5)
    exp_arr.visualize(num_traces=10000, num_bins=100)
    plt.show()
