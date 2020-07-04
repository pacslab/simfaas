# The main simulator for serverless computing platforms

import numpy as np

from simfaas.ServerlessSimulator import ServerlessSimulator
from simfaas.ParFunctionInstance import ParFunctionInstance

class ParServerlessSimulator(ServerlessSimulator):
    """ParServerlessSimulator is responsible for executing simulations of a sample serverless computing platform with the ability to handle concurrent request in each instance, mainly for the performance analysis and performance model evaluation purposes. For parameters, refer to :class:`~simfaas.ServerlessSimulator.ServerlessSimulator`.

    Parameters
    ----------
    concurrency_value : int
        The number of concurrent requests allowed for each function instance.
    """
    def __init__(self, concurrency_value: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.concurrency_value = concurrency_value

    def cold_start_arrival(self, t):
        """Goes through the process necessary for a cold start arrival which includes generation of a new function instance in the `COLD` state and adding it to the cluster.

        Parameters
        ----------
        t : float
            The time at which the arrival has happened. This is used to record the creation time for the server and schedule the expiration of the instance if necessary.
        """
        self.total_req_count += 1

        # reject request if maximum concurrency reached
        if self.running_count == self.maximum_concurrency:
            self.total_reject_count += 1
            self.hist_req_rej_idxs.append(len(self.hist_times) - 1)
            return

        self.total_cold_count += 1
        self.hist_req_cold_idxs.append(len(self.hist_times) - 1)

        self.server_count += 1
        self.running_count += 1
        new_server = ParFunctionInstance(self.concurrency_value, t, self.cold_service_process, self.warm_service_process, self.expiration_threshold)
        self.servers.append(new_server)

    def reset_trace(self):
        """resets all the historical data to prepare the class for a new simulation with additional functionality added to base class.
        """
        super().reset_trace()
        self.hist_conc_levels = []
        self.hist_conc_avgs = []

    def update_hist_arrays(self, t):
        """Update history arrays

        Parameters
        ----------
        t : float
            Current time
        """
        super().update_hist_arrays(t)
        conc_levels = [s.get_concurrency() for s in self.servers]
        self.hist_conc_levels.append(conc_levels)

        if len(conc_levels) > 0:
            conc_level_avg = np.mean(conc_levels)
        else:
            conc_level_avg = -1

        self.hist_conc_avgs.append(conc_level_avg)

    def get_average_conc_avgs(self):
        """Get the time-averaged average concurrency levels among all instances.

        Returns
        -------
        float
            Average concurrency levels of instances
        """
        avg_conc = (self.hist_conc_avgs * self.time_lengths)
        idxs = avg_conc > 0
        avg_conc = avg_conc[idxs].sum() / self.time_lengths[idxs].sum()
        return avg_conc

    
    def get_result_dict(self):
        """Get the results of the simulation as a dict, which can easily be integrated into web services.

        Returns
        -------
        dict
            A dictionary of different characteristics.
        """

        # TODO: add results regarding concurrency value
        ret = super().get_result_dict()
        ret.update({
            "conc_level_avg": self.get_average_conc_avgs(),
        })
        return ret

    def print_trace_results(self):
        """Print a brief summary of the results of the trace.
        """
        super().print_trace_results()

        # average concurrency value
        print(f"Average Concurrency Value: \t {self.get_average_conc_avgs():.4f}")
    
    def is_warm_available(self, t):
        """Whether we have at least one available instance in the warm pool that can process requests

        Parameters
        ----------
        t : float
            Current time

        Returns
        -------
        bool
            True if at least one server is able to accept a request
        """
        for s in self.servers:
            if s.is_ready():
                return True

        return False

    
        




if __name__ == "__main__":
    sim = ParServerlessSimulator(concurrency_value=1, arrival_rate=0.9, warm_service_rate=1/2.016, cold_service_rate=1/(2.163 - 2.016),
            expiration_threshold=600, max_time=1e5)
    sim.generate_trace(debug_print=False, progress=True)
    sim.print_trace_results()
  