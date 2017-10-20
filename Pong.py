import sys
from Queue import Queue

import Logger
from SPIServer import SPIServer
from TCPServer import TCPServer

if __name__ == "__main__":
    tcpserver = None
    spiserver = None
    try:
        Logger.log("Initializing variables")
        if len(sys.argv) == 3:
            host = sys.argv[1]
            port = int(sys.argv[2])
            qspiread = Queue()
            qspiwrite = Queue()
            qtcpread = Queue()
            qtcpwrite = Queue()
            Logger.logspi("Initializing spiserver")
            spiserver = SPIServer(qspiread, qspiwrite, 0b00, 0, 0)
            Logger.logtcp("Initializing tcpserver")
            tcpserver = TCPServer(qtcpread, qtcpwrite, host, port)
            Logger.logspi("Starting spiserver")
            spiserver.start()
            Logger.logtcp("Starting tcpserver")
            tcpserver.start()
            spiserver.join()
            tcpserver.join()

        else:
            Logger.error("Usage 'Pong.py <HOST> <PORT>'")
    except KeyboardInterrupt:
        Logger.logtcp("Shutting down tcpserver")
        if tcpserver is not None:
            tcpserver.shutdown()
        Logger.logspi("Shutting down spiserver")
        if spiserver is not None:
            spiserver.shutdown()
