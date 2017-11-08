#!/usr/bin/python
import errno
import socket
import sys
import time
from Queue import Queue
from threading import Thread

import Logger
from SendThread import SendThread
from GameController import GameController
from TCPClient import TCPClient
from tracking.tracking import Tracker

# from TriTracker import LaptopTracker

# Switch to disable or enable the SPIServer.
useSPI = False
useMotion = True

if useSPI:
    from SPIServer import SPIThread


class GameThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = False
        self.controller = GameController(True)

    def start(self):
        self.running = True
        super(GameThread, self).start()

    def run(self):
        lastFrameTime = time.time()
        result = None
        datared = 0
        datablue = 0

        while self.running:
            currentTime = time.time()
            dt = currentTime - lastFrameTime
            lastFrameTime = currentTime
            calibratedY = -1

            datagreen = q_camera_read_green.get()
            if motion_thread.calibrating:
                databluetemp = q_camera_read_blue.get()
                dataredtemp = q_camera_read_red.get()
                if dataredtemp is not None:
                    datared = dataredtemp
                if databluetemp is not None:
                    datablue = databluetemp
            # else:
            #     print "calibrated blue=" + str(datablue) + ", red=" + str(datared)

            if datagreen is not None and datablue is not None and datared is not None:
                print("red" + str(datared) + " blue" + str(datablue) + "green" + str(datagreen))
                if datablue < 0:
                    datablue = 0
                if datagreen < datablue:
                    datagreen = datablue
                if datagreen > datared:
                    datagreen = datared

                datagreen -= datablue
                if (datared - datablue) > 0:
                    calibratedY = 1 - (1 / (datared - datablue)) * datagreen

            self.controller.loop(dt, calibratedY)

    def cmdStart(self):
        motion_thread.calibrating = False
        self.controller.start()

    def cmdStop(self):
        self.controller.stop()

    def cmdReset(self):
        self.controller.reset()

    def get_gamestate(self):
        return self.controller.get_gamestate()

    def shutdown(self):
        self.running = False
        self.controller.stop()
        # self.controller.shutdown()


# Main method that initializes all variables and starts the TCPServer and SPIServer (if enabled).
# The TCPServer can be configured using command arguments <host> <port>.
# The SPIServer defaults to CLOCK_POLARITY = 0, CLOCK_PHASE = 0 BUS = 0 and DEVICE = 0.
if __name__ == "__main__":
    spi_thread = None
    game_thread = None
    motion_thread = None
    tcp_thread = None
    send_thread = None

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
        q_spi_write = Queue()  # Stores data to be written to the spi interface (should only contain bytes).
        q_tcp_read = Queue()  # Stores data read from the tcp interface (should only contain strings).
        q_tcp_write = Queue()  # Stores data to be written to the tcp interface (should only contain strings).
        q_camera_read_green = Queue()
        q_camera_read_blue = Queue()
        q_camera_read_red = Queue()
        Logger.log("Initialized queues")

        # INITIALIZATION

        # MOTION TRACKING
        if useMotion:
            Logger.log("Initializing Motion Tracking")
            motion_thread = Tracker(q_camera_read_green, q_camera_read_blue, q_camera_read_red,
                                    "pi")
            Logger.log("Initialized Motion Tracking")

        # SPI-SERVER
        if useSPI:
            Logger.log_spi(
                "Initializing spi-server with: " +
                "[mode:" + str(mode) + "] [bus:" + str(bus) + "] [device:" + str(device) + "]")
            spi_thread = SPIThread(q_spi_write, mode, bus, device)
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
        tcp_thread = TCPClient(host, port, q_tcp_read, q_tcp_write)
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

        # Send Thread
        send_thread = SendThread(game_thread, tcp_thread)

        # INPUT
        while True:
            # line = raw_input()
            # if line == "quit":
            #     break
            if not q_tcp_read.empty():
                recv = q_tcp_read.get()
                print recv
                if recv.startswith("start"):
                    print "START"
                    game_thread.cmdStart()
                if recv.startswith("stop"):
                    game_thread.cmdStop()
                if recv.startswith("reset"):
                    game_thread.cmdReset()

    except (ValueError, IndexError):
        print sys.argv[0]
        path, filename = str(sys.argv[0]).rsplit('/', 1)
        Logger.log_error("Usage: 'python " + filename + " <HOST> <PORT>'")

    except socket.error as socket_error:
        if socket_error.errno == errno.EADDRINUSE:
            Logger.log_error("Address already in use")
        else:
            print socket_error.errno
            raise socket_error

    except KeyboardInterrupt:
        Logger.log("Received KeyboardInterrupt")

    finally:
        # MOTION TRACKING
        if useMotion:
            Logger.log_game("Shutting down Motion Tracking")
            if motion_thread is not None:
                motion_thread.exit_handler()
                motion_thread.join()
            Logger.log_game("Shut down Motion Tracking")

        # GAME
        Logger.log_game("Shutting down game")
        if game_thread is not None:
            game_thread.shutdown()
            game_thread.join()
        Logger.log_game("Shut down game")

        # SPI
        if useSPI:
            Logger.log_spi("Shutting down spi-server")
            if spi_thread is not None:
                spi_thread.shutdown()
                spi_thread.join()
            Logger.log_spi("Shut down spi-server")

        # TCP-SERVER
        Logger.log_tcp("Shutting down tcp-server")
        if tcp_thread is not None:
            tcp_thread.shutdown()
            tcp_thread.join()
        Logger.log_tcp("Shut down tcp-server")

        Logger.log("Shutting down")
        exit(0)
