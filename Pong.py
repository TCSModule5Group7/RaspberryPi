import sys
from Queue import Queue

import Logger
from SPIServer import SPIServer
from TCPServer import TCPServer

if __name__ == "__main__":
    tcp_server = None
    spi_server = None
    try:
        if len(sys.argv) == 3:
            Logger.log("Initializing variables")
            host = sys.argv[1]
            port = int(sys.argv[2])
            Logger.log("Initializing queues")
            q_spi_read = Queue()  # Stores data read from the spi interface
            q_spi_write = Queue()  # Stores data to be written to the spi interface
            q_tcp_read = Queue()  # Stores data read from the tcp interface
            q_tcp_write = Queue()  # Stores data to be written to the tcp interface
            Logger.logspi("Initializing spi-server")
            spi_server = SPIServer(q_spi_read, q_spi_write, 0b00, 0, 0)
            Logger.logtcp("Initializing tcp-server")
            tcp_server = TCPServer(q_tcp_read, q_tcp_write, host, port)
            Logger.logspi("Starting spi-server")
            spi_server.start()
            Logger.logtcp("Starting tcp-server")
            tcp_server.start()
            spi_server.join()
            tcp_server.join()

        else:
            Logger.error("Usage 'python Pong.py <HOST> <PORT>'")
    except KeyboardInterrupt:
        Logger.logtcp("Shutting down tcp-server")
        if tcp_server is not None:
            tcp_server.shutdown()
        Logger.logspi("Shutting down spi-server")
        if spi_server is not None:
            spi_server.shutdown()
