import socket
from threading import Thread

import Logger


class TCPServer(Thread):
    def __init__(self, q_read, q_write, host, port):
        Thread.__init__(self)
        self.q_read = q_read
        self.q_write = q_write
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.client_socket = None
        self.client_address = None
        self.running = False

    def run(self):
        Logger.logtcp("Waiting for client")
        self.running = True
        self.await_client()
        self.listen()

    def await_client(self):
        self.server_socket.listen(1)
        self.client_socket, self.client_address = self.server_socket.accept()

    def listen(self):
        while self.running:
            received = self.client_socket.receive(1024)
            self.send(self, "received:" + received)
            self.q_write.put(received)

    def shutdown(self):
        self.running = False
        self.client_socket.close()
        self.server_socket.close()


    def send(self, data):
        while True:
            data = self.q_read.get()
            if data is None:
                break
            self.q_read.task_done()
            self.client.socket.sendall(data)


