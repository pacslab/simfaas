import numpy as np

from pacssim.SimProcess import ExpSimProcess
from pacssim.FunctionInstance import FunctionInstance
from pacssim.ServerlessTemporalSimulator import ServerlessTemporalSimulator
from pacssim.ServerlessSimulator import ServerlessSimulator

cold_service_rate = 1/2.163
warm_service_rate = 1/2.016
expiration_threshold = 600

arrival_rate = 0.9
max_time = 300

running_function_count = 3
idle_function_count = 5

cold_service_process = ExpSimProcess(rate=cold_service_rate)
warm_service_process = ExpSimProcess(rate=warm_service_rate)

def generate_trace_api(data):
    sim = ServerlessSimulator(**data)
    sim.generate_trace(debug_print=False, progress=False)
    results = sim.get_result_dict()
    results.update(data)
    return results

def generate_trace():
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
    sim.generate_trace(debug_print=False, progress=False)
    return sim.get_cold_start_prob()

if __name__ == "__main__":
    print([generate_trace() for _ in range(10)])
