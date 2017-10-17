import SocketServer
import sys

import Logger
from TCPHandler import TCPHandler


def starttcp(server):
    server.serve_forever()


def startspi(master):
    # master.serve_forever()
    return


if __name__ == "__main__":
    global tcpserver
    # global spiserver
    try:
        Logger.log("Initializing variables")
        if len(sys.argv) == 3:
            HOST = sys.argv[1]
            PORT = int(sys.argv[2])
            # Logger.logspi("Initializing spiserver")
            # spiserver = 1  # SPIServer(0b00)
            Logger.logtcp("Initializing tcpserver")
            tcpserver = SocketServer.TCPServer((HOST, PORT), TCPHandler)
            # Logger.logspi("Starting spiserver")
            # thread.start_new(startspi, (spiserver,))
            Logger.logtcp("Starting tcpserver")
            starttcp(tcpserver)
        else:
            Logger.error("Usage 'Pong.py <HOST> <PORT>'")
    except KeyboardInterrupt:
        Logger.logtcp("Shutting down tcpserver")
        tcpserver.shutdown()
        # Logger.logspi("Shutting down spiserver")
        # spiserver.shutdown()
