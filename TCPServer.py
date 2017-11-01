import Queue
import socket
from threading import Thread

import SocketServer

import Logger

class ClientHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        line = ""
        data = ""

        while line != "quit":
                received = self.request.recv(1024)
                data += received
                if "\n" in data:
                    line, data = data.split("\n", 1)
                    Logger.logtcp("received: " + line)
                    try:
                        self.server.q_read.put(line,False)
                    except Queue.Full:
                        pass

                    self.request.send(line.upper() + "\n")
        self.request.close()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self,host,port,q_read,q_write):
        SocketServer.TCPServer.__init__(self,(host,port), ClientHandler)
        self.q_read = q_read
        self.q_write = q_write
        self.serve_forever()

if __name__ == "__main__":
    HOST, PORT = "localhost", 9998

    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

#####################################################################################################
# class TCPServer(Thread):
#     def __init__(self, q_read, q_write, host, port):
#         Thread.__init__(self)
#         self.running = False
#         self.q_read = q_read
#         self.q_write = q_write
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server_socket.bind((host, port))
#         self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#     def run(self):
#         self.running = True
#         self.await_client()
#         writer = Thread(target=self.write)
#         writer.start()
#         self.read()
#         writer.join()
#
#     def await_client(self):
#         self.server_socket.listen(1)
#         self.client_socket, client_address = self.server_socket.accept()
#
#     def write(self):
#         while self.running:
#             try:
#                 line = self.q_write.get()
#                 self.client_socket.sendall(line)
#             except Queue.Empty:
#                 pass
#
#     # Some code from https://www.experts-exchange.com/questions/22056190/Sockets-recv-function-on-a-new-line.html
#     def read(self):
#         data = ""
#         while self.running:
#             try:
#                 received = self.client_socket.recv(1024)
#                 data += received
#                 if "\n" in data:
#                     line, data = data.split("\n", 1)
#                     self.q_read.put(line)
#                     Logger.logtcp("received: " + line)
#             except Queue.Full:
#                 pass
#
#     def shutdown(self):
#         self.running = False
#         self.client_socket.close()
#         self.server_socket.close()
