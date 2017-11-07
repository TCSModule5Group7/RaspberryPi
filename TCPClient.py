import socket
from threading import Thread


class TCPClient(Thread):
    def __init__(self, host, port, q_read, q_write):
        Thread.__init__(self)
        self.running = False
        self.host = host
        self.port = port
        self.q_write = q_write
        self.q_read = q_read
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connected = False

    def start(self):
        self.running = True
        super(TCPClient, self).start()

    def run(self):
        self.socket.connect((self.host, self.port))
        self.connected = True
        print "connected"

        while self.running:
            buffer = self.socket.recv(53)
            buffer = buffer.split('\r')[0]
            print "recv: " + str(buffer)
            self.q_read.put(buffer)

    def send(self, message):
        if self.connected:
            self.socket.send(message)

    def shutdown(self):
        self.running = False
        self.send("shutdown")
        self.socket.close()
