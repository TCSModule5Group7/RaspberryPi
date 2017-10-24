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
            tx_data = [0x00]
            rx_data = [0x00]
            data = self.getter(self.q_read)
            # if there is data in q_read:
            if data > 0:
                tx_data[0] = data
                rx_data = self.spi.xfer2(tx_data)
            else:
                tx_data[0] = [0x00]
                rx_data = self.spi.xfer2(tx_data)
            # if we received data
            if rx_data[0] > 0:
                # put data to q_write
                self.producer(self.q_write, rx_data)

    def shutdown(self):
        self.running = False
        self.spi.close()

    # gets data from queue
    def getter(self, queue):
        while True:
            data = queue.get()
            if data is None:
                break
            queue.task_done()
            return data

    # writes data to write queue
    def producer(self, queue, data):
        while True:
            # put data on queue
            queue.put(data)
