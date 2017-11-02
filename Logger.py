from sys import stdin
from termios import tcflush, TCIFLUSH

ansiRed = "\033[31m"
ansiGreen = "\033[32m"
ansiYellow = "\033[33m"
ansiBlue = "\033[34m"
ansiMagenta = "\033[35m"
ansiEnd = "\033[0m"


def log(message):
    tcflush(stdin, TCIFLUSH)
    print(ansiBlue + "[log]" + message + ansiEnd)


def log_spi(message):
    tcflush(stdin, TCIFLUSH)
    print(ansiYellow + "[spi]" + message + ansiEnd)


def log_tcp(message):
    tcflush(stdin, TCIFLUSH)
    print(ansiGreen + "[tcp]" + message + ansiEnd)


def log_game(message):
    tcflush(stdin, TCIFLUSH)
    print(ansiMagenta + "[game]" + message + ansiEnd)


def log_error(message):
    tcflush(stdin, TCIFLUSH)
    print(ansiRed + "[error]" + message + ansiEnd)
