import Queue
import socket
from threading import Thread

import Logger


class TCPServer(Thread):
    def __init__(self, q_read, q_write, host, port):
        Thread.__init__(self)
        print("Thread init")
        self.running = False
        self.q_read = q_read
        self.q_write = q_write
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.client_socket = None
        self.client_address = None
        print("TCPServer init")

    def run(self):
        self.running = True
        self.await_client()
        writer = Thread(target=self.write)
        writer.start()
        self.read()

    def await_client(self):
        self.server_socket.listen(1)
        self.client_socket, self.client_address = self.server_socket.accept()

    def write(self):
        while self.running:
            try:
                line = self.q_write.get()
                self.q_write.task_done()
                self.client_socket.sendall(line)
            except Queue.Empty:
                pass

    # Some code from https://www.experts-exchange.com/questions/22056190/Sockets-recv-function-on-a-new-line.html
    def read(self):
        data = ""
        while self.running:
            try:
                received = self.client_socket.receive(1024)
                data += received
                if "\n" in data:
                    line, data = data.split("\n", 1)
                    self.q_read.put(line)
                    Logger.logtcp("received: " + line)
            except Queue.Full:
                pass

    def shutdown(self):
        self.running = False
        self.client_socket.close()
        self.server_socket.close()
