#!/usr/bin/python
import Queue
import sys

import Logger

###########################

useSPI = False

###########################

if useSPI:
    from SPIServer import SPIServer

from TCPServer import ThreadedTCPServer

if __name__ == "__main__":
    tcp_server = None

    if useSPI:
        spi_server = None

    try:
        if len(sys.argv) == 3:
            Logger.log("Initializing variables")
            host = sys.argv[1]
            port = int(sys.argv[2])
            Logger.log("Initializing queues")

            if useSPI:
                q_spi_read = Queue.Queue()  # Stores data read from the spi interface
                q_spi_write = Queue.Queue()  # Stores data to be written to the spi interface

            q_tcp_read = Queue.Queue()  # Stores data read from the tcp interface
            q_tcp_write = Queue.Queue()  # Stores data to be written to the tcp interface

            if useSPI:
                Logger.logspi("Initializing spi-server")
                spi_server = SPIServer(q_spi_read, q_spi_write, 0b00, 0, 0)

            Logger.logtcp("Initializing tcp-server")
            tcp_server = ThreadedTCPServer(host, port, q_tcp_read, q_tcp_write)

            if useSPI:
                Logger.logspi("Starting spi-server")
                spi_server.start()

            Logger.logtcp("Starting tcp-server")
            tcp_server.start()
            # Test code to just forward tcp to spi
            while True:
                try:
                    byte = q_tcp_read.get(False)
                    byte = int(byte, 16)

                    if useSPI:
                        q_spi_write.put(byte)

                except Queue.Full, Queue.Empty:
                    pass
        else:
            Logger.logerror("Usage 'python Pong.py <HOST> <PORT>'")
    except KeyboardInterrupt:
        Logger.log("Received KeyboardInterrupt")
    finally:

        if useSPI:
            Logger.logspi("Shutting down spi-server")
            if spi_server is not None:
                spi_server.shutdown()

        Logger.logtcp("Shutting down tcp-server")
        if tcp_server is not None:
            tcp_server.shutdown()
        Logger.log("Shutting down")
