import spidev
from threading import Thread

import Logger

TRANSFER = 0b00000000
READ = 0b10000000
WRITE = 0b01000000
NO_OPERATION = 0b110000000

NO_DATA = 0b00000000


class SPIThread(Thread):
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
        self.running = True
        while self.running:
            if not self.q_write.empty():
                write_data = [TRANSFER, self.q_write.get(False)]
            else:
                write_data = [READ, NO_DATA]
                write_data = [NO_OPERATION, NO_DATA]  # Temporary line to not overflow queues

            read_data = self.spi.xfer2(write_data)
            if not self.q_read.full():
                if read_data[0] == TRANSFER:
                    Logger.log_spi("Sent: '" + hex(write_data[0]) + "|" + hex(write_data[1]) + "'")
                    Logger.log_spi("Received: '" + (read_data[0]) + "|" + hex(read_data[1]) + "'")
                    self.q_read.put(read_data[1], False)
                elif read_data[0] == READ:
                    Logger.log_spi("Received: '" + (read_data[0]) + "|" + hex(read_data[1]) + "'")
                    self.q_read.put(read_data[1], False)

    def shutdown(self):
        self.running = False
        self.spi.close()
