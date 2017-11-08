import time
from threading import Thread
import threading

FREQ = 10


class SendThread(Thread):
    def __init__(self, game_thread, tcp_thread):
        Thread.__init__(self)
        self.game_thread = game_thread
        self.tcp_thread = tcp_thread
        self.running = True
        self.start()

    def run(self):
        while self.running:
            event = threading.Event()
            event.wait(timeout=(1 / FREQ * 1000))
            # time.sleep(1 / FREQ * 1000)
            self.tcp_thread.send(self.game_thread.get_gamestate())

    def shutdown(self):
        self.running = False
