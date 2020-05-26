import zmq
import time
import sys

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
print("Connecting to server...")
socket = context.socket(zmq.DEALER)
socket.setsockopt(zmq.IDENTITY, b'A')
socket.connect("tcp://127.0.0.1:%s" % port)

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

while True:
    socks = dict(poller.poll(timeout=1000))
    print(socks)

    if socket in socks and socks[socket] == zmq.POLLIN:
        print("Message from socket: %s" % socket.recv())
        time.sleep(.1)
        socket.send(("World from %s" % port).encode())
    
