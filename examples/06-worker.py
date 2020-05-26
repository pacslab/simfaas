import zmq
import time
import sys

from pacssim.SimProcess import ExpSimProcess
from pacssim.FunctionInstance import FunctionInstance
from pacssim.ServerlessTemporalSimulator import ServerlessTemporalSimulator

from tqdm import tqdm
import numpy as np
import struct
from threading import Thread

cold_service_rate = 1/2.163
warm_service_rate = 1/2.016
expiration_threshold = 600

arrival_rate = 0.9
max_time = 300

# number of simulations samples produced
num_sim = 1000

running_function_count = 3
idle_function_count = 5

cold_service_process = ExpSimProcess(rate=cold_service_rate)
warm_service_process = ExpSimProcess(rate=warm_service_rate)

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

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)
socket_addr = "tcp://127.0.0.1:%s" % port

worker_count = 32
stop_signal = False
def worker(context=None, name="worker"):
    context = context or zmq.Context.instance()
    worker = context.socket(zmq.ROUTER)
    worker.connect(socket_addr)

    print(f"Starting thread: {name}")

    poller = zmq.Poller()
    poller.register(worker, zmq.POLLIN)
    while not stop_signal:
        socks = dict(poller.poll(timeout=1000))

        if worker in socks and socks[worker] == zmq.POLLIN:
            ident, message = worker.recv_multipart()
            
            # calculate trace
            msg = struct.pack("d", generate_trace())
            
            worker.send_multipart([ident, msg])

# t = Thread(target=worker)
# t.start()

worker_names = [f"worker-{i}" for i in range(worker_count)]
worker_funcs = [lambda context=None,name=n: worker(context=context, name=name) for n in worker_names]
worker_threads = [Thread(target=f) for f in worker_funcs]
_ = [t.start() for t in worker_threads]

# wait for threads to stabilize
# time.sleep(5)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print("Ctrl-c pressed!")
        stop_signal = True
        [t.join() for t in worker_threads]
        break

