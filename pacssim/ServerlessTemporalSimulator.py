# ServerlessTemporalSimulator extends the functionality of ServerlessSimulator
# by providing necessary functionality for temporal scenarios where initial
# state is important and the initial process might be different from the
# following service process.

from pacssim.FunctionInstance import FunctionInstance
from pacssim.ServerlessSimulator import ServerlessSimulator


class ServerlessTemporalSimulator(ServerlessSimulator):
    def __init__(self, running_function_instances, idle_function_instances,
                 arrival_process=None, warm_service_process=None,
                 cold_service_process=None, expiration_threshold=600, max_time=24*60*60,
                 maximum_concurrency=1000, **kwargs):

        super().__init__(arrival_process=arrival_process,
                         warm_service_process=warm_service_process,
                         cold_service_process=cold_service_process,
                         expiration_threshold=expiration_threshold,
                         max_time=max_time,
                         maximum_concurrency=maximum_concurrency,
                         **kwargs)

        init_running_count = len(running_function_instances)
        init_idle_count = len(idle_function_instances)
        init_server_count = init_running_count + init_idle_count

        self.server_count = init_server_count
        self.running_count = init_running_count
        self.idle_count = init_server_count - init_running_count
        self.servers = [*running_function_instances, *idle_function_instances]


if __name__ == "__main__":
    from pacssim.SimProcess import ExpSimProcess

    print("Performing Temporal Simulation")
    cold_service_rate = 1/2.163
    warm_service_rate = 1/2.016
    expiration_threshold = 600

    arrival_rate = 0.9
    max_time = 300

    running_function_count = 3
    idle_function_count = 5

    cold_service_process = ExpSimProcess(rate=cold_service_rate)
    warm_service_process = ExpSimProcess(rate=warm_service_rate)

    idle_functions = []
    for _ in range(idle_function_count):
        f = FunctionInstance(0,
                             cold_service_process,
                             warm_service_process,
                             expiration_threshold
                             )

        f.state = 'IDLE'
        f.is_cold = False
        # when will it be destroyed if no requests
        f.next_termination = 300
        # so that they would be less likely to be chosen by scheduler
        f.creation_time = 0.01
        idle_functions.append(f)

    running_functions = []
    for _ in range(running_function_count):
        f = FunctionInstance(0,
                             cold_service_process,
                             warm_service_process,
                             expiration_threshold
                             )

        f.state = 'IDLE'
        f.is_cold = False
        # transition it into running mode
        f.arrival_transition(0)

        running_functions.append(f)

    sim = ServerlessTemporalSimulator(running_functions, idle_functions, arrival_rate=arrival_rate, warm_service_rate=warm_service_rate, cold_service_rate=cold_service_rate,
                                      expiration_threshold=expiration_threshold, max_time=max_time)
    sim.generate_trace(debug_print=True, progress=True)
    sim.print_trace_results()
