import Queue
import spidev
from threading import Thread


class SPIServer(Thread):
    def __init__(self, q_read, q_write, mode, bus, device):
        Thread.__init__(self)
        self.q_read = q_read
        self.q_write = q_write
        self.running = False
        self.spi = spidev.SpiDev()
        self.spi.mode = mode
        self.spi.open(bus, device)

    def run(self):
        self.serve_forever()

    def serve_forever(self):
        self.running = True
        while self.running:
            try:
                write_data = self.q_write.get(False)
            except Queue.Empty:
                write_data = [0x00]

            read_data = self.spi.xfer2(write_data)
            if read_data[0] != 0x00:
                self.q_read.put(read_data, False)
            self.q_write.task_done()

    def shutdown(self):
        self.running = False
        self.spi.close()
