import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import expon, poisson, norm

from pacssim.Utility import convert_hist_pdf

# import warnings
# warnings.simplefilter(action='ignore', category=FutureWarning)
# warnings.simplefilter(action='ignore', category=NotImplementedError)
# import modin.pandas as pd

class SimProcess:
    """SimProcess gives us a single interface to simulate different processes
    """    
    def __init__(self):
        super().__init__()
        # if your class has pdf or cdf functions, switch the booleans to True
        self.has_pdf = False
        self.has_cdf = False

    def generate_trace(self):
        raise NotImplementedError

    def visualize(self, num_traces=10000, num_bins=100):
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
    def __init__(self, rate):
        super().__init__()

        self.has_pdf = False
        self.has_cdf = False
        self.rate = rate

    def generate_trace(self):
        return 1/self.rate


class GaussianSimProcess(SimProcess):
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
