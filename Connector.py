import socket


class Connector(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def update(self, paddleL, paddleR, ballX, ballY, scoreL, scoreR):
        self.socket.send(str(paddleL) + "/" + str(paddleR) + "/" + str(ballX) + "/" + str(ballY) + "/" + str(scoreL) +
                         "/" + str(scoreR) + "\n")
        return self.socket.makefile().readline()

    def update(self, string):
        self.socket.send(string)
        return self.socket.makefile().readline()

    def close(self):
        self.socket.send("quit\n")

    def shutdown(self):
        self.socket.send("shutdown\n")
