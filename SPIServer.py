import Queue
import spidev
from threading import Thread

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
        self.spi.mode = mode
        self.spi.open(bus, device)

    def run(self):
        self.transfer()

    def transfer(self):
        self.running = True
        while self.running:
            write_data = [NO_OPERATION, NO_DATA]
            try:
                write_data = [TRANSFER, self.q_write.get(False)]
            except Queue.Empty:
                write_data = [READ, NO_DATA]
                write_data = [NO_OPERATION, NO_DATA]  # Temporary line to not overflow queues

            read_data = self.spi.xfer2(write_data)
            if read_data[0] == READ | read_data[0] == TRANSFER:
                try:
                    self.q_read.put(read_data[1], False)
                except Queue.Full:
                    pass

            self.q_write.task_done()

    def shutdown(self):
        self.running = False
        self.spi.close()
