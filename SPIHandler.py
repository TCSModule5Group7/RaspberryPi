import spidev

import Logger

spi = spidev.SpiDev()
spi.mode(0b00)
spi.open(0, 0)
byte0 = 0x00
byte31 = 0xFF


def send(byte):
    resp = spi.xfer2(byte)
    for hex in bytearraytohexarray(resp):
        print(hex)
    print(str(bytearraytohexarray(resp)))


def bytearraytohexarray(bytearray):
    result = []
    for byte in bytearray:
        result.append(hex(byte))
    return result


class SPIHandler():
    Logger.log("started spi")
