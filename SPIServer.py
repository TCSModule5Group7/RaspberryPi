import spidev

import Logger


class SPIServer(object):
    def __init__(self, mode):
        self.running = False
        self.txbuffer = []
        self.rxbuffer = []
        self.spi = spidev.SpiDev()
        self.spi.mode(mode)

    def serve_forever(self, bus, device):
        self.spi.open(bus, device)
        self.running = True
        while self.running:
            txdata = [0x00]
            rxdata = [0x00]
            if len(self.txbuffer) > 0:
                txdata[0] = self.txbuffer[0]
                rxdata = self.spi.xfer2(txdata)
                Logger.logspi("Sent: " + hex(txdata))

            if rxdata[0] != 0x00:
                # TODO send data to main controller
                self.rxbuffer.extend(rxdata)
                Logger.logspi("received: " + hex(rxdata[0]))

    def send(self, txdata):
        self.txbuffer.extend(txdata)

    def shutdown(self):
        self.running = False
        self.spi.close()
