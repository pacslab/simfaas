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
socket.connect("tcp://127.0.0.1:%s" % port)

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

while True:
    socks = dict(poller.poll(timeout=1000))
    print(socks)

    if socket in socks and socks[socket] == zmq.POLLIN:
        # ident, message = socket.recv_multipart()
        # print(f"Message from {ident.decode()}: {message}")
        print("Message from socket: %s" % socket.recv_multipart())
        # print("Message from socket: %s" % socket.recv())
        time.sleep(.1)
        # socket.send_multipart([b"master", ("World from %s" % port).encode()])
        socket.send_multipart([("World from %s" % port).encode()])
    
