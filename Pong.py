#!/usr/bin/python
import Queue
import sys
from threading import Thread

import Logger
from TCPServer import ThreadedTCPServer

###########################

useSPI = False

###########################

if useSPI:
    from SPIServer import SPIThread

if __name__ == "__main__":
    tcp_server = None

    if useSPI:
        spi_thread = None

    try:
        if len(sys.argv) == 3:
            Logger.log("Initializing variables")
            host = sys.argv[1]
            port = int(sys.argv[2])
            mode = 0b00
            bus = 0
            device = 0
            Logger.log("Initializing queues")

            if useSPI:
                q_spi_read = Queue.Queue()  # Stores data read from the spi interface
                q_spi_write = Queue.Queue()  # Stores data to be written to the spi interface

            q_tcp_read = Queue.Queue()  # Stores data read from the tcp interface
            q_tcp_write = Queue.Queue()  # Stores data to be written to the tcp interface

            if useSPI:
                Logger.logspi(
                    "Initializing spi-server with: "
                    "[mode:" + str(mode) + "] "
                                           "[bus:" + str(bus) + "] " +
                    "[device:" + str(device) + "]")
                spi_thread = SPIThread(q_spi_read, q_spi_write, mode, bus, device)

            Logger.logtcp("Initializing tcp-server with:" +
                          "[host:" + str(host) + "] " +
                          "[port:" + str(port) + "]")
            tcp_server = ThreadedTCPServer(host, port, q_tcp_read, q_tcp_write)
            tcp_thread = Thread(target=tcp_server.start)
            if useSPI:
                Logger.logspi("Starting spi-server")
                spi_thread.start()

            Logger.logtcp("Starting tcp-server")
            tcp_thread.start()
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
            if spi_thread is not None:
                spi_thread.shutdown()

        Logger.logtcp("Shutting down tcp-server")
        if tcp_server is not None:
            tcp_server.shutdown()
        Logger.log("Shutting down")
