from threader import Thread
from queue import Queue
import Logger

class SPIThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, qread, qwrite)
        self.qread = qread
        self.qwrite = qwrite
        self.running = False
        self.spi = spidev.SpiDev()
        self.spi.mode(mode)
        # self.bus = bus
        # self.device = device

    def run(self):
        serve_forever(self, qread, qwrite)


def serve_forever(self, qread, qwrite):
    self.spi.open(0, 0)
    self.running = True
    while self.running:
        txdata = [0x00]
        rxdata = [0x00]
        data = getter(qread)
        # if there is data in qread:
        if data > 0:
            txdata[0] = data
            rxdata = self.spi.xfer2(txdata)
            Logger.logspi("Sent: " + hex(txdata))
        else:
            txdata[0] = [0x00]
            rxdata = self.spi.xfer2(txdata)
        # if we received data
        if rxdata[0] != 0x00:
            # end data to qwrite
            producer(qwrite, rxdata)
            Logger.logspi("received: " + hex(rxdata[0]))



def shutdown(self):
    self.running = False
    self.spi.close()


# gets data from queue
def getter(q):
    while True:
        data = q.get()
        if data is None:
            break
        q.task_done()
        return data


# writes data to write queue
def producer(q, data):
    while True:
        # put data on queue
        q.put(data)


