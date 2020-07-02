# ServerlessTemporalSimulator extends the functionality of ServerlessSimulator
# by providing necessary functionality for temporal scenarios where initial
# state is important and the initial process might be different from the
# following service process.

from simfaas.FunctionInstance import FunctionInstance
from simfaas.ServerlessSimulator import ServerlessSimulator


class ServerlessTemporalSimulator(ServerlessSimulator):
    """ServerlessTemporalSimulator extends ServerlessSimulator to enable extraction of temporal characteristics. Also gets all of the arguments accepted by :class:`~simfaas.ServerlessSimulator.ServerlessSimulator`

    Parameters
    ----------
    running_function_instances : list[FunctionInstance]
        A list containing the running function instances
    idle_function_instances : list[FunctionInstance]
        A list containing the idle function instances
    """
    def __init__(self, running_function_instances, idle_function_instances,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        init_running_count = len(running_function_instances)
        init_idle_count = len(idle_function_instances)
        init_server_count = init_running_count + init_idle_count

        self.server_count = init_server_count
        self.running_count = init_running_count
        self.idle_count = init_server_count - init_running_count
        self.servers = [*running_function_instances, *idle_function_instances]



class ExponentialServerlessTemporalSimulator(ServerlessTemporalSimulator):
    """ExponentialServerlessTemporalSimulator is a simulator assuming exponential distribution for proceesing times which means each process is state-less and we can generate a service time and use that from now on. This class extends ServerlessTemporalSimulator which has functionality for other processes as well.

    Parameters
    ----------
    running_function_instance_count : integer
        running_function_instance_count is the number of instances currently processing a request
    idle_function_instance_next_terminations : list[float]
        idle_function_instance_next_terminations is an array of next termination scheduled for idle functions
        if they receive no new requests.
    """
    def __init__(self, running_function_instance_count, idle_function_instance_next_terminations,
                 *args, **kwargs):
        cold_service_process = ExpSimProcess(rate=cold_service_rate)
        warm_service_process = ExpSimProcess(rate=warm_service_rate)

        idle_functions = []
        for next_term in idle_function_instance_next_terminations:
            f = FunctionInstance(0,
                                cold_service_process,
                                warm_service_process,
                                expiration_threshold
                                )

            f.state = 'IDLE'
            f.is_cold = False
            # when will it be destroyed if no requests
            f.next_termination = next_term
            # so that they would be less likely to be chosen by scheduler
            f.creation_time = 0.01
            idle_functions.append(f)

        running_functions = []
        for _ in range(running_function_instance_count):
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

        super().__init__(
            running_function_instances=running_functions,
            idle_function_instances=idle_functions,
            *args, **kwargs
        )


if __name__ == "__main__":
    from simfaas.SimProcess import ExpSimProcess

    print("Performing Temporal Simulation")
    cold_service_rate = 1/2.163
    warm_service_rate = 1/2.016
    expiration_threshold = 600

    arrival_rate = 0.9
    max_time = 600

    running_function_count = 3
    idle_function_count = 10

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
    sim.generate_trace(debug_print=False, progress=True)
    sim.print_trace_results()


    print("Testing out the new functionality added.")
    idle_function_instance_next_terminations = [300] * idle_function_count
    sim = ExponentialServerlessTemporalSimulator(running_function_count, idle_function_instance_next_terminations, arrival_rate=arrival_rate, 
                                        warm_service_rate=warm_service_rate, cold_service_rate=cold_service_rate,
                                        expiration_threshold=expiration_threshold, max_time=max_time)
    sim.generate_trace(debug_print=False, progress=True)
    sim.print_trace_results()
