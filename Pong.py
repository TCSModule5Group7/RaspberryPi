#!/usr/bin/python
from Queue import Queue
from errno import EADDRINUSE
from socket import error
from sys import argv
from threading import Thread

import Logger
from TCPServer import TCPThread

# Switch to disable or enable the SPIServer
useSPI = False

if useSPI:
    from SPIServer import SPIThread


# Test code to just forward tcp to spi
class GameThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            if not q_tcp_read.empty():
                byte = q_tcp_read.get(False)
                try:
                    byte = int(byte, 16)

                    if useSPI:
                        q_spi_write.put(byte)
                except ValueError:
                    Logger.log_error("Could not convert text to byte")

    def shutdown(self):
        self.running = False


# Main method that initializes all variables and starts the TCPServer and SPIServer (if enabled)
# The TCPServer can be configured using command arguments <host> <port>
# The SPIServer defaults to CLOCK_POLARITY = 0, CLOCK_PHASE = 0 BUS = 0 and DEVICE = 0
if __name__ == "__main__":
    if useSPI:
        spi_thread = None

    tcp_thread = None

    game_thread = None

    try:
        # VARIABLES
        Logger.log("Initializing variables")

        host = argv[1]
        port = int(argv[2])
        if useSPI:
            mode = 0b00
            bus = 0
            device = 0

        Logger.log("Initialized variables")
        # QUEUES
        Logger.log("Initializing queues")

        if useSPI:
            q_spi_read = Queue()  # Stores data read from the spi interface (should only contain bytes)
            q_spi_write = Queue()  # Stores data to be written to the spi interface (should only contain bytes)

        q_tcp_read = Queue()  # Stores data read from the tcp interface (should only contain strings)
        q_tcp_write = Queue()  # Stores data to be written to the tcp interface (should only contain strings)

        Logger.log("Initialized queues")
        # SPI-SERVER
        if useSPI:
            Logger.log_spi(
                "Initializing spi-server with: " +
                "[mode:" + str(mode) + "] [bus:" + str(bus) + "] [device:" + str(device) + "]")

            spi_thread = SPIThread(q_spi_read, q_spi_write, mode, bus, device)

            Logger.log_spi(
                "Initialized spi-server with: " +
                "[mode:" + str(mode) + "] [bus:" + str(bus) + "] [device:" + str(device) + "]")
        # TCP-SERVER
        Logger.log_tcp("Initializing tcp-server with: " +
                       "[host:" + str(host) + "] [port:" + str(port) + "]")

        tcp_thread = TCPThread(host, port, q_tcp_read, q_tcp_write)

        Logger.log_tcp("Initialized tcp-server with:" +
                       "[host:" + str(host) + "] [port:" + str(port) + "]")
        # GAME
        Logger.log_game("Initializing game")

        game_thread = GameThread()

        Logger.log_game("Initialized game")
        # SPI-SERVER
        if useSPI:
            Logger.log_spi("Starting spi-server")

            spi_thread.start()

            Logger.log_spi("Started spi-server")
        # TCP-SERVER
        Logger.log_tcp("Starting tcp-server")

        tcp_thread.start()

        Logger.log_tcp("Started tcp-server")
        # GAME
        Logger.log_game("Starting game")

        game_thread.start()

        Logger.log_game("Started game")
        # INPUT
        while True:
            line = raw_input()
            if line == "quit":
                break

    except (ValueError, IndexError):
        Logger.log_error("Usage: 'python Pong.py <HOST> <PORT>'")

    except error as socket_error:
        if socket_error.errno == EADDRINUSE:
            Logger.log_error("Address already in use")
        else:
            raise socket_error

    except KeyboardInterrupt:
        Logger.log("Received KeyboardInterrupt")

    finally:
        Logger.log_game("Shutting down game")
        if game_thread is not None:
            game_thread.shutdown()
        Logger.log_game("Shut down game")

        Logger.log_tcp("Shutting down tcp-server")
        if tcp_thread is not None:
            tcp_thread.shutdown()
        Logger.log_tcp("Shut down tcp-server")

        if useSPI:
            Logger.log_spi("Shutting down spi-server")
            if spi_thread is not None:
                spi_thread.shutdown()
            Logger.log_spi("Shut down spi-server")

        Logger.log("Shutting down")
