import socket
import sys
from threading import Thread

import Logger


class TCPClient(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        self.running = False
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def run(self):
        self.running = True
        try:
            writer = Thread(target=self.write)
            writer.start()
            self.read()
            writer.join()
        except KeyboardInterrupt:
            Logger.log("Received KeyboardInterrupt")
        finally:
            self.running = False
            self.socket.close()

    def write(self):
        while self.running:
            line = raw_input(">")
            self.socket.sendall(line)
            Logger.logtcp("Sent: " + line)

    # Some code from https://www.experts-exchange.com/questions/22056190/Sockets-recv-function-on-a-new-line.html
    def read(self):
        data = ""
        while self.running:
            received = self.socket.recv(1024)
            data += received
            if "\n" in data:
                line, data = data.split("\n", 1)
                Logger.logtcp("Received: " + line)


if __name__ == "__main__":
    client_host = sys.argv[1]
    client_port = int(sys.argv[2])
    client = TCPClient(client_host, client_port)
    client.run()
