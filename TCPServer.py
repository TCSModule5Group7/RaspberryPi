import Queue
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
                    self.server.q_read.put(line, False)
                except Queue.Full:
                    Logger.logtcp("Queue is full")
            self.request.send("received\n")
        self.request.close()
        Logger.logtcp("Client disconnected")


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, host, port, q_read, q_write):
        SocketServer.TCPServer.__init__(self, (host, port), ClientHandler)
        self.daemon_threads = True
        self.q_read = q_read
        self.q_write = q_write
        self.serve_forever()