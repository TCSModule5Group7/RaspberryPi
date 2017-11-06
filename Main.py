#!/usr/bin/python
import errno
import socket
import sys

from Queue import Queue
from threading import Thread
import pygame
import Logger
from GameController import GameController
from TCPServer import TCPThread
from tracking.LaptopTracking import LaptopTracker

# Switch to disable or enable the SPIServer.
useSPI = False
useMotion = False

if useSPI:
    from SPIServer import SPIThread


# Test code to just forward tcp to spi.
class GameThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = False
        self.controller = GameController(True)

    def start(self):
        self.running = True
        self.controller.start()
        super(GameThread, self).start()

    def run(self):
        result = None
        while self.running:
            if not q_camera_read_green.empty():
                result = self.controller.loop(q_camera_read_green.get())  # Fill in coordinate from motion tracking
            else:
                result = self.controller.loop()
            q_tcp_write.put(result, False)

    def shutdown(self):
        self.running = False
        self.controller.stop()
        self.controller.shutdown()


# Main method that initializes all variables and starts the TCPServer and SPIServer (if enabled).
# The TCPServer can be configured using command arguments <host> <port>.
# The SPIServer defaults to CLOCK_POLARITY = 0, CLOCK_PHASE = 0 BUS = 0 and DEVICE = 0.
if __name__ == "__main__":
    spi_thread = None
    game_thread = None
    motion_thread = None
    tcp_thread = None

    try:
        # VARIABLES
        Logger.log("Initializing variables")

        host = sys.argv[1]
        port = int(sys.argv[2])
        if useSPI:
            mode = 0b00
            bus = 0
            device = 0

        Logger.log("Initialized variables")

        # QUEUES
        Logger.log("Initializing queues")
        q_spi_read = Queue()  # Stores data read from the spi interface (should only contain bytes).
        q_spi_write = Queue()  # Stores data to be written to the spi interface (should only contain bytes).
        q_tcp_read = Queue()  # Stores data read from the tcp interface (should only contain strings).
        q_tcp_write = Queue()  # Stores data to be written to the tcp interface (should only contain strings).
        q_camera_read_green = Queue()
        q_camera_read_blue = Queue()
        Logger.log("Initialized queues")

        # INITIALIZATION

        # MOTION TRACKING
        if useMotion:
            Logger.log("Initializing Motion Tracking")
            motion_thread = LaptopTracker(q_camera_read_green, q_camera_read_blue, False)
            Logger.log("Initialized Motion Tracking")

        # SPI-SERVER
        if useSPI:
            Logger.log_spi(
                "Initializing spi-server with: " +
                "[mode:" + str(mode) + "] [bus:" + str(bus) + "] [device:" + str(device) + "]")
            spi_thread = SPIThread(q_spi_read, q_spi_write, mode, bus, device)
            Logger.log_spi(
                "Initialized spi-server with: " +
                "[mode:" + str(mode) + "] [bus:" + str(bus) + "] [device:" + str(device) + "]")

        # GAME
        Logger.log_game("Initializing game")
        game_thread = GameThread()
        Logger.log_game("Initialized game")

        # TCP-SERVER
        Logger.log_tcp("Initializing tcp-server with: " +
                       "[host:" + str(host) + "] [port:" + str(port) + "]")
        tcp_thread = TCPThread(host, port, q_tcp_read, q_tcp_write)
        Logger.log_tcp("Initialized tcp-server with:" +
                       "[host:" + str(host) + "] [port:" + str(port) + "]")

        # START

        # MOTION TRACKING
        if useMotion:
            Logger.log_game("Starting Motion Tracking")
            motion_thread.start()
            Logger.log_game("Started Motion Tracking")

        # SPI-SERVER
        if useSPI:
            Logger.log_spi("Starting spi-server")
            spi_thread.start()
            Logger.log_spi("Started spi-server")

        # GAME
        Logger.log_game("Starting game")
        game_thread.start()
        Logger.log_game("Started game")

        # TCP-SERVER
        Logger.log_tcp("Starting tcp-server")
        tcp_thread.start()
        Logger.log_tcp("Started tcp-server")

        # INPUT
        while True:
            line = raw_input()
            if line == "quit":
                break
            if not q_tcp_read.empty():
                print q_tcp_read.get()

    except (ValueError, IndexError):
        Logger.log_error("Usage: 'python Main.py <HOST> <PORT>'")

    except socket.error as socket_error:
        if socket_error.errno == errno.EADDRINUSE:
            Logger.log_error("Address already in use")
        else:
            raise socket_error

    except KeyboardInterrupt:
        Logger.log("Received KeyboardInterrupt")

    finally:
        # TCP-SERVER
        Logger.log_tcp("Shutting down tcp-server")
        if tcp_thread is not None:
            tcp_thread.shutdown()
        Logger.log_tcp("Shut down tcp-server")

        # MOTION TRACKING
        if useMotion:
            Logger.log_game("Shutting down Motion Tracking")
            if motion_thread is not None:
                motion_thread.exit_handler()
            Logger.log_game("Shut down Motion Tracking")

        # GAME
        Logger.log_game("Shutting down game")
        if game_thread is not None:
            game_thread.shutdown()
        Logger.log_game("Shut down game")

        # SPI
        if useSPI:
            Logger.log_spi("Shutting down spi-server")
            if spi_thread is not None:
                spi_thread.shutdown()
            Logger.log_spi("Shut down spi-server")

        Logger.log("Shutting down")
