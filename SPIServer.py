import spidev
from threading import Thread


class SPIServer(Thread):
    def __init__(self, qread, qwrite, mode, bus, device):
        Thread.__init__(self)
        self.qread = qread
        self.qwrite = qwrite
        self.running = False
        self.spi = spidev.SpiDev()
        self.spi.mode = mode
        self.spi.open(bus, device)

    def run(self):
        self.serve_forever()

    def serve_forever(self):
        self.running = True
        while self.running:
            txdata = [0x00]
            rxdata = [0x00]
            data = self.getter(self.qread)
            # if there is data in qread:
            if data > 0:
                txdata[0] = data
                rxdata = self.spi.xfer2(txdata)
            else:
                txdata[0] = [0x00]
                rxdata = self.spi.xfer2(txdata)
            # if we received data
            if rxdata[0] > 0:
                # put data to qwrite
                self.producer(self.qwrite, rxdata)

    def shutdown(self):
        self.running = False
        self.spi.close()

    # gets data from queue
    def getter(self, q):
        while True:
            data = q.get()
            if data is None:
                break
            q.task_done()
            return data

    # writes data to write queue
    def producer(self, q, data):
        while True:
            # put data on queue
            q.put(data)
