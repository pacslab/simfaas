# The main simulator for serverless computing platforms

from pacssim.SimProcess import ExpSimProcess
from pacssim.FunctionInstance import FunctionInstance
import numpy as np

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

    def reset_trace(self):
        # an archive of previous servers
        self.prev_servers = []
        self.total_req_count = 0
        self.total_cold_count = 0
        self.total_warm_count = 0
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

    def has_server(self):
        return len(self.servers) > 0

    def __str__(self):
        return f"idle/running/total: \t {self.idle_count}/{self.running_count}/{self.server_count}"

    def req(self):
        return self.arrival_process.generate_trace()

    def cold_start_arrival(self, t):
        self.total_req_count += 1
        self.total_cold_count += 1

        self.server_count += 1
        self.running_count += 1
        new_server = FunctionInstance(t, self.cold_service_process, self.warm_service_process, self.expiration_threshold)
        self.servers.append(new_server)

    def schedule_warm_instance(self, t):
        self.total_req_count += 1
        self.total_warm_count += 1

        idle_instances = [s for s in self.servers if s.is_idle()]
        creation_times = [s.creation_time for s in idle_instances]
        
        # scheduling mechanism
        creation_times = np.array(creation_times)
        # find the newest instance
        idx = np.argmax(creation_times)
        idle_instances[idx].arrival_transition(t)

    def warm_start_arrival(self, t):
        # transition from idle to running
        self.idle_count -= 1
        self.running_count += 1
        self.schedule_warm_instance(t)

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

    def print_trace_results(self):
        self.calculate_time_lengths()

        print(f"Cold Starts / total requests: \t {self.total_cold_count} / {self.total_req_count}")
        print(f"Cold Start Probability: \t {self.total_cold_count / self.total_req_count:.4f}")

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
        assert len(values) == len(self.time_lengths), "Values shoud be same length as history array (number of transitions)"

        # how many initial values should be skipped
        skip_init = 0
        if skip_init_time is not None:
            skip_init = self.get_index_after_time(skip_init_time)
        if skip_init_index is not None:
            skip_init = max(skip_init, skip_init_index)

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

    def generate_trace(self, debug_print=False):
        # reset trace values
        self.reset_trace()

        t = 0
        next_arrival = t + self.req()
        while self.trace_condition(t):
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




if __name__ == "__main__":
    sim = ServerlessSimulator(arrival_rate=0.9, warm_service_rate=1/2.016, cold_service_rate=1/2.163,
            expiration_threshold=600, max_time=100000)
    sim.generate_trace(debug_print=False)
    sim.print_trace_results()
  