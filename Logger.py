from sys import stdin
from termios import tcflush, TCIFLUSH

ansi_red = "\033[31m"
ansi_green = "\033[32m"
ansi_yellow = "\033[33m"
ansi_blue = "\033[34m"
ansi_magenta = "\033[35m"
ansi_cyan = "\033[36m"
ansi_end = "\033[0m"


def log(message):
    tcflush(stdin, TCIFLUSH)
    print(ansi_blue + "[log]" + message + ansi_end)


def log_spi(message):
    tcflush(stdin, TCIFLUSH)
    print(ansi_yellow + "[spi]" + message + ansi_end)


def log_tcp(message):
    tcflush(stdin, TCIFLUSH)
    print(ansi_green + "[tcp]" + message + ansi_end)


def log_game(message):
    tcflush(stdin, TCIFLUSH)
    print(ansi_magenta + "[game]" + message + ansi_end)


def log_tracking(message):
    tcflush(stdin, TCIFLUSH)
    print(ansi_cyan + "[game]" + message + ansi_end)


def log_error(message):
    tcflush(stdin, TCIFLUSH)
    print(ansi_red + "[error]" + message + ansi_end)
