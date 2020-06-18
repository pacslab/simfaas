import zmq
import time
import sys
import pickle

import struct
import multiprocessing

from examples.sim_trace import generate_trace_api

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)
socket_addr = "tcp://127.0.0.1:%s" % port

worker_count = multiprocessing.cpu_count() * 2 + 1
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
            
            data = pickle.loads(message)

            # calculate trace
            msg = generate_trace_api(data)
            msg = pickle.dumps(msg)
            
            worker.send_multipart([ident, msg])

if __name__ == "__main__":
    worker_names = [f"worker-{i}" for i in range(worker_count)]
    worker_threads = [multiprocessing.Process(target=worker, args=(None,n)) for n in worker_names]
    _ = [t.start() for t in worker_threads]

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Ctrl-c pressed!")
            stop_signal = True
            [t.join() for t in worker_threads]
            break

