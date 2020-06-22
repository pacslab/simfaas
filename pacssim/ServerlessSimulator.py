# The main simulator for serverless computing platforms

from pacssim.SimProcess import ExpSimProcess
from pacssim.FunctionInstance import FunctionInstance
import numpy as np
import pandas as pd

from tqdm import tqdm

class ServerlessSimulator:
    def __init__(self, arrival_process=None, warm_service_process=None, 
            cold_service_process=None, expiration_threshold=600, max_time=24*60*60,
            maximum_concurrency=1000, **kwargs):
        super().__init__()
        
        # setup arrival process
        self.arrival_process = arrival_process
        # if the user wants a exponentially distributed arrival process
        if 'arrival_rate' in kwargs:
            self.arrival_process = ExpSimProcess(rate=kwargs.get('arrival_rate'))
        # in the end, arrival process should be defined
        if self.arrival_process is None:
            raise Exception('Arrival process not defined!')

        # if both warm and cold service rate is provided (exponential distribution)
        # then, warm service rate should be larger than cold service rate
        if 'warm_service_rate' in kwargs and 'cold_service_rate' in kwargs:
            if kwargs.get('warm_service_rate') < kwargs.get('cold_service_rate'):
                raise Exception("Warm service rate cannot be smaller than cold service rate!")

        # setup warm service process
        self.warm_service_process = warm_service_process
        if 'warm_service_rate' in kwargs:
            self.warm_service_process = ExpSimProcess(rate=kwargs.get('warm_service_rate'))
        if self.warm_service_process is None:
            raise Exception('Warm Service process not defined!')

        # setup cold service process
        self.cold_service_process = cold_service_process
        if 'cold_service_rate' in kwargs:
            self.cold_service_process = ExpSimProcess(rate=kwargs.get('cold_service_rate'))
        if self.cold_service_process is None:
            raise Exception('Cold Service process not defined!')

        self.expiration_threshold = expiration_threshold
        self.max_time = max_time
        self.maximum_concurrency = maximum_concurrency

        # reset trace values
        self.reset_trace()

    def reset_trace(self):
        # an archive of previous servers
        self.prev_servers = []
        self.total_req_count = 0
        self.total_cold_count = 0
        self.total_warm_count = 0
        self.total_reject_count = 0
        # current state of instances
        self.servers = []
        self.server_count = 0
        self.running_count = 0
        self.idle_count = 0
        # history results
        self.hist_times = []
        self.hist_server_count = []
        self.hist_server_running_count = []
        self.hist_server_idle_count = []
        self.hist_req_cold_idxs = []
        self.hist_req_warm_idxs = []
        self.hist_req_rej_idxs = []

    def has_server(self):
        return len(self.servers) > 0

    def __str__(self):
        return f"idle/running/total: \t {self.idle_count}/{self.running_count}/{self.server_count}"

    def req(self):
        return self.arrival_process.generate_trace()

    def cold_start_arrival(self, t):
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
        new_server = FunctionInstance(t, self.cold_service_process, self.warm_service_process, self.expiration_threshold)
        self.servers.append(new_server)

    def schedule_warm_instance(self, t):
        idle_instances = [s for s in self.servers if s.is_idle()]
        creation_times = [s.creation_time for s in idle_instances]
        
        # scheduling mechanism
        creation_times = np.array(creation_times)
        # find the newest instance
        idx = np.argmax(creation_times)
        return idle_instances[idx]

    def warm_start_arrival(self, t):
        self.total_req_count += 1

        # reject request if maximum concurrency reached
        if self.running_count == self.maximum_concurrency:
            self.total_reject_count += 1
            self.hist_req_rej_idxs.append(len(self.hist_times) - 1)
            return

        self.hist_req_warm_idxs.append(len(self.hist_times) - 1)

        # schedule the request
        instance = self.schedule_warm_instance(t)
        instance.arrival_transition(t)

        # transition from idle to running
        self.total_warm_count += 1
        self.idle_count -= 1
        self.running_count += 1

    def get_trace_end(self):
        return self.hist_times[-1]

    def calculate_time_lengths(self):
        self.time_lengths = np.diff(self.hist_times)

    def get_average_server_count(self):
        avg_server_count = (self.hist_server_count * self.time_lengths).sum() / self.get_trace_end()
        return avg_server_count

    def get_average_server_running_count(self):
        avg_running_count = (self.hist_server_running_count * self.time_lengths).sum() / self.get_trace_end()
        return avg_running_count

    def get_average_server_idle_count(self):
        avg_idle_count = (self.hist_server_idle_count * self.time_lengths).sum() / self.get_trace_end()
        return avg_idle_count

    def get_index_after_time(self, t):
        return np.min(np.where(np.array(self.hist_times) > t))

    def get_skip_init(self, skip_init_time=None, skip_init_index=None):
        # how many initial values should be skipped
        skip_init = 0
        if skip_init_time is not None:
            skip_init = self.get_index_after_time(skip_init_time)
        if skip_init_index is not None:
            skip_init = max(skip_init, skip_init_index)
        return skip_init

    def get_request_custom_states(self, hist_states, skip_init_time=None, skip_init_index=None):
        req_skip_init = self.get_skip_init(skip_init_time=skip_init_time, 
                                        skip_init_index=skip_init_index)

        state_req_colds = {}
        state_req_warm = {}
        state_req_rejs = {}
        for s in hist_states[req_skip_init:]:
            if s not in state_req_colds:
                state_req_colds[s] = 0
                state_req_warm[s] = 0
                state_req_rejs[s] = 0

        hist_req_cold = [i for i in self.hist_req_cold_idxs if i > req_skip_init]
        hist_req_warm = [i for i in self.hist_req_warm_idxs if i > req_skip_init]
        hist_req_rej = [i for i in self.hist_req_rej_idxs if i > req_skip_init]


        for idx in hist_req_cold:
            state_req_colds[hist_states[idx]] += 1
        for idx in hist_req_warm:
            state_req_warm[hist_states[idx]] += 1
        for idx in hist_req_rej:
            state_req_warm[hist_states[idx]] += 1

        states = list(state_req_colds.keys())
        state_req_colds = list(state_req_colds.values())
        state_req_warm = list(state_req_warm.values())
        state_req_rejs = list(state_req_rejs.values())

        reqdf = pd.DataFrame(data = {'state': states, 'cold': state_req_colds, 'warm': state_req_warm, 'rej': state_req_rejs})
        reqdf['total'] = reqdf['cold'] + reqdf['warm'] + reqdf['rej']
        reqdf['p_cold'] = reqdf['cold'] / reqdf['total']
        return reqdf

    def analyze_custom_states(self, hist_states, skip_init_time=None, skip_init_index=None):
        skip_init = self.get_skip_init(skip_init_time=skip_init_time, 
                                        skip_init_index=skip_init_index)

        values = hist_states[skip_init:]
        time_lengths = self.time_lengths[skip_init:]

        residence_times = {}
        transition_times = {}
        curr_time_sum = time_lengths[0]
        # encode states
        for idx in range(1,len(values)):
            if values[idx] == values[idx-1]:
                curr_time_sum += time_lengths[idx]
            else:
                if values[idx-1] in residence_times:
                    residence_times[values[idx-1]].append(curr_time_sum)
                else:
                    residence_times[values[idx-1]] = [curr_time_sum]

                transition_pair = (values[idx-1], values[idx])
                if transition_pair in transition_times:
                    transition_times[transition_pair].append(curr_time_sum)
                else:
                    transition_times[transition_pair] = [curr_time_sum]
                
                curr_time_sum = time_lengths[idx]

        return residence_times, transition_times

    def get_average_residence_times(self, hist_states, skip_init_time=None, skip_init_index=None):
        residence_times, _ = self.analyze_custom_states(hist_states, skip_init_time, skip_init_index)

        residence_time_avgs = {}
        for s in residence_times:
            residence_time_avgs[s] = np.mean(residence_times[s])

        return residence_time_avgs

    def get_cold_start_prob(self):
        return self.total_cold_count / self.total_req_count


    def get_average_lifespan(self):
        life_spans = np.array([s.get_life_span() for s in self.prev_servers])
        return life_spans.mean()

    
    def get_result_dict(self):
        return {
            "reqs_cold": self.total_cold_count,
            "reqs_total": self.total_req_count,
            "reqs_warm": self.total_warm_count,
            "prob_cold": self.get_cold_start_prob(),
            "reqs_reject": self.total_reject_count,
            "prob_reject": self.total_reject_count / self.total_req_count,
            "lifespan_avg": self.get_average_lifespan(),
            "inst_count_avg": self.get_average_server_count(),
            "inst_running_count_avg": self.get_average_server_running_count(),
            "inst_idle_count_avg": self.get_average_server_idle_count(),
        }

    def print_trace_results(self):
        self.calculate_time_lengths()

        print(f"Cold Starts / total requests: \t {self.total_cold_count} / {self.total_req_count}")
        print(f"Cold Start Probability: \t {self.total_cold_count / self.total_req_count:.4f}")

        print(f"Rejection / total requests: \t {self.total_reject_count} / {self.total_req_count}")
        print(f"Rejection Probability: \t\t {self.total_reject_count / self.total_req_count:.4f}")

        # average instance life span
        life_spans = np.array([s.get_life_span() for s in self.prev_servers])
        print(f"Average Instance Life Span: \t {life_spans.mean():.4f}")

        # average instance count
        print(f"Average Server Count:  \t\t {self.get_average_server_count():.4f}")
        # average running count
        print(f"Average Running Count:  \t {self.get_average_server_running_count():.4f}")
        # average idle count
        print(f"Average Idle Count:  \t\t {self.get_average_server_idle_count():.4f}")

    def trace_condition(self, t):
        return t < self.max_time

    @staticmethod
    def print_time_average(vals, probs, column_width=15):
        print(f"{'Value'.ljust(column_width)} Prob")
        print("".join(["="]*int(column_width*1.5)))
        for val, prob in zip(vals, probs):
            print(f"{str(val).ljust(column_width)} {prob:.4f}")

    def calculate_time_average(self, values, skip_init_time=None, skip_init_index=None):
        """calculate_time_average calculates the time-averaged of the values passed in with
        optional skipping a specific number of time steps (skip_init_index) and a specific
        amount of time (skip_init_time).

        Parameters
        ----------
        values : list
            A list of values with the same dimensions as history array (number of transitions)
        skip_init_time : Float, optional
            Amount of time skipped in the beginning to let the transient part of the solution pass, by default None
        skip_init_index : [type], optional
            Number of steps skipped in the beginning to let the transient behaviour of system pass, by default None

        Returns
        -------
        (list, list)
            returns (unq_vals, val_times) where unq_vals is the unique values inside the values list
            and val_times is the portion of the time that is spent in that value.
        """
        assert len(values) == len(self.time_lengths), "Values shoud be same length as history array (number of transitions)"

        skip_init = self.get_skip_init(skip_init_time=skip_init_time, 
                                        skip_init_index=skip_init_index)

        values = values[skip_init:]
        time_lengths = self.time_lengths[skip_init:]

        # get unique values
        unq_vals = list(set(values))
        val_times = []
        for val in unq_vals:
            t = time_lengths[[v == val for v in values]].sum()
            val_times.append(t)

        # convert to percent
        val_times = np.array(val_times)
        val_times = val_times / val_times.sum()
        return unq_vals, val_times

    def generate_trace(self, debug_print=False, progress=False):
        pbar = None
        if progress:
            pbar = tqdm(total=int(self.max_time))

        t = 0
        pbar_t_update = 0
        pbar_interval = int(self.max_time / 100)
        next_arrival = t + self.req()
        while self.trace_condition(t):
            if progress:
                if int(t - pbar_t_update) > pbar_interval:
                    pbar.update(int(t) - pbar_t_update)
                    pbar_t_update = int(t)
            self.hist_times.append(t)
            self.hist_server_count.append(self.server_count)
            self.hist_server_running_count.append(self.running_count)
            self.hist_server_idle_count.append(self.idle_count)
            if debug_print:
                print()
                print(f"Time: {t:.2f} \t NextArrival: {next_arrival:.2f}")
                print(self)
                # print state of all servers
                [print(s) for s in self.servers]

            # if there are no servers, next transition is arrival
            if self.has_server() == False:
                t = next_arrival
                next_arrival = t + self.req()
                # no servers, so cold start
                self.cold_start_arrival(t)
                continue

            # if there are servers, next transition is the soonest one
            server_next_transitions = np.array([s.get_next_transition_time(t) for s in self.servers])

            # if next transition is arrival
            if (next_arrival - t) < server_next_transitions.min():
                t = next_arrival
                next_arrival = t + self.req()

                # if warm start
                if self.idle_count > 0:
                    self.warm_start_arrival(t)
                # if cold start
                else:
                    self.cold_start_arrival(t)
                continue

            # if next transition is a state change in one of servers
            else:
                # find the server that needs transition
                idx = server_next_transitions.argmin()
                t = t + server_next_transitions[idx]
                new_state = self.servers[idx].make_transition()
                # delete instance if it was just terminated
                if new_state == 'TERM':
                    self.prev_servers.append(self.servers[idx])
                    self.idle_count -= 1
                    self.server_count -= 1
                    del self.servers[idx]
                    if debug_print:
                        print(f"Termination for: # {idx}")
                
                # if request has done processing (exit event)
                elif new_state == 'IDLE':
                    # transition from running to idle
                    self.running_count -= 1
                    self.idle_count += 1
                else:
                    raise Exception(f"Unknown transition in states: {new_state}")

        # after the trace loop, append the last time recorded
        self.hist_times.append(t)
        self.calculate_time_lengths()
        if progress:
            pbar.update(int(self.max_time) - pbar_t_update)
            pbar.close()
        




if __name__ == "__main__":
    sim = ServerlessSimulator(arrival_rate=0.9, warm_service_rate=1/2.016, cold_service_rate=1/2.163,
            expiration_threshold=600, max_time=100000)
    sim.generate_trace(debug_print=False, progress=True)
    sim.print_trace_results()
  