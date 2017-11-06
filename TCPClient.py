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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.running = True
        super(TCPClient, self).start()

    def run(self):
        self.socket.connect((self.host, self.port))
        print "connected"

        while self.running:
            buffer = ''
            while not buffer.endswith("\n"):
                data = self.socket.recv(1)
                buffer += data
            print "recv: " + buffer
            self.q_read.put(buffer)

    def send(self, message):
        if self.running:
            self.socket.send(message)

    def shutdown(self):
        self.running = False
        self.send("shutdown")
        self.socket.close()
