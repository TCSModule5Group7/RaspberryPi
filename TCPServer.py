from SocketServer import ThreadingTCPServer, BaseRequestHandler
from threading import Thread

import Logger


class TCPThread(Thread):
    def __init__(self, host, port, q_read, q_write):
        Thread.__init__(self)
        self.tcp_server = ThreadedTCPServer(host, port, q_read, q_write)

    def run(self):
        self.tcp_server.serve_forever()

    def shutdown(self):
        self.tcp_server.shutdown()
        self.tcp_server.server_close()


class ClientHandler(BaseRequestHandler):
    def handle(self):
        line = ""
        data = ""

        while True:
            received = self.request.recv(1024)
            data += received
            if "\n" in data:
                line, data = data.split("\n", 1)
                if not self.server.q_read.full():
                    self.server.q_read.put(line, False)
                    Logger.log_tcp("Received: '" + line + "'")
                    self.request.send("Received\n")
            if line == "quit":
                break


class ThreadedTCPServer(ThreadingTCPServer):
    def __init__(self, host, port, q_read, q_write):
        ThreadingTCPServer.__init__(self, (host, port), ClientHandler)
        self.daemon_threads = True
        self.q_read = q_read
        self.q_write = q_write
