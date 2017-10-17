import SocketServer

import Logger


class TCPHandler(SocketServer.StreamRequestHandler):
    # Does nothing yet
    def setup(self):
        return

    # Returns uppercase version of the received data back to the sender
    def handle(self):
        rxdata = self.rfile.readline().strip()
        Logger.logtcp("[rcv] '{}' [fr] '{}'".format(rxdata, self.client_address))
        txdata = rxdata.upper()
        self.wfile.write(txdata)
        Logger.logtcp("[snd] '{}' [to] '{}'".format(txdata, self.client_address))
        return

    # Does nothing yet
    def finish(self):
        return
