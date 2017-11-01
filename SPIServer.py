import Queue
import spidev
from threading import Thread

import Logger

TRANSFER = 0b00000000
READ = 0b10000000
WRITE = 0b01000000
NO_OPERATION = 0b110000000

NO_DATA = 0b00000000


class SPIServer(Thread):
    def __init__(self, q_read, q_write, mode, bus, device):
        Thread.__init__(self)
        self.running = False
        self.q_read = q_read
        self.q_write = q_write
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.mode = mode
        self.spi.max_speed_hz = 31200000

    def run(self):
        self.transfer()

    def transfer(self):
        self.running = True
        while self.running:
            write_data = [NO_OPERATION, NO_DATA]
            try:
                write_data = [TRANSFER, self.q_write.get(False)]
                Logger.logspi("Found: " + hex(write_data[0]) + " " + hex(write_data[1]))
            except Queue.Empty:
                write_data = [READ, NO_DATA]
                write_data = [NO_OPERATION, NO_DATA]  # Temporary line to not overflow queues
                Logger.logspi("Found: no data")

            read_data = self.spi.xfer2(write_data)
            Logger.logspi("Sent: " + hex(write_data[0]) + " " + hex(write_data[1]))
            if read_data[0] == READ | read_data[0] == TRANSFER:
                try:
                    self.q_read.put(read_data[1], False)
                    Logger.logspi("Received: " + hex(read_data[0]) + " " + hex(read_data[1]))
                except Queue.Full:
                    pass

    def shutdown(self):
        self.running = False
        self.spi.close()
