import socket
from threading import Thread

import Logger


class TCPServer(Thread):
    def __init__(self, qread, qwrite, host, port):
        Thread.__init__(self)
        self.qread = qread
        self.qwrite = qwrite
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))
        self.running = False
        self.handler = None

    def run(self):
        Logger.logtcp("Waiting for client")
        self.awaitclient()

    def awaitclient(self):
        self.running = True
        self.serversocket.listen(1)
        clientsocket, address = self.serversocket.accept()
        handler = TCPClientHandler(self, clientsocket)
        # print 'Connection address:', addr
        #
        # while 1:
        #     data = conn.recv(BUFFER_SIZE)
        #
        # if not data: break
        #
        # print "received data:", data
        #
        # conn.send(data)  # echo
        #
        # conn.close()


def shutdown(self):
    for handler in self.handlers:
        handler.shutdown()
    return


class TCPClientHandler(Thread):
    def __init__(self, server, clientsocket):
        Thread.__init__(self)
        self.clientsocket = clientsocket
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.clientsocket.recv(1024)

    def send(self):
        self.clientsocket

    def shutdown(self):
        self.clientsocket.close()
