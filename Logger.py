ansiRed = "\033[31m"
ansiGreen = "\033[32m"
ansiYellow = "\033[33m"
ansiBlue = "\033[34m"
ansiEnd = "\033[0m"


def log(message):
    print(ansiBlue + "[log]" + message + ansiEnd)


def logspi(message):
    print(ansiYellow + "[spi]" + message + ansiEnd)


def logtcp(message):
    print(ansiGreen + "[tcp]" + message + ansiEnd)


def error(message):
    print(ansiRed + "[error]" + message + ansiEnd)
