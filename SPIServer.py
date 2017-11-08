import time
from threading import Thread

import spidev

goal_animation_time = 5.0
goal_array_array = [[0b00000000, 0b00000110],
                    [0b00000000, 0b10000000],
                    [0b00000000, 0b10000000],
                    [0b00000000, 0b01000000],
                    [0b00000000, 0b00100000],
                    [0b00000000, 0b00010000],
                    [0b00000000, 0b00001000],
                    [0b00000000, 0b00000100],
                    [0b00000000, 0b00000010],
                    [0b00000000, 0b11000000],
                    [0b00000000, 0b01100000],
                    [0b00000000, 0b00110000],
                    [0b00000000, 0b00011000],
                    [0b00000000, 0b00001100]]
l_scored_array = [0b00000000, 0b00000000]
r_scored_array = [0b00000000, 0b00000001]


class SPIThread(Thread):
    def __init__(self, q_write, mode, bus, device):
        Thread.__init__(self)
        self.running = False
        self.q_write = q_write
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 3900000
        self.spi.mode = 0b00

    def run(self):
        self.running = True
        while self.running:
            if not self.q_write.empty():
                line = self.q_write.get(False)
                print str(line)
                if line == "":
                    pass
                elif line == "l":
                    print "l scored"
                    for message in goal_array_array:
                        self.spi.writebytes(message)
                        time.sleep(goal_animation_time / len(goal_array_array))
                    self.spi.writebytes(l_scored_array)
                elif line == "r":
                    print "r scored"
                    for message in goal_array_array:
                        self.spi.writebytes(message)
                        time.sleep(goal_animation_time / len(goal_array_array))
                    self.spi.writebytes(r_scored_array)
        self.cleanup()

    def shutdown(self):
        self.running = False

    def cleanup(self):
        self.spi.close()
