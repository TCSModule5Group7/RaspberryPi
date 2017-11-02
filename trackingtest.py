import Queue
from threading import Thread

import tracking
import cv2
import atexit
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')

class TrackingTest(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.q_camera_read_green = Queue.Queue()
        self.q_camera_read_blue = Queue.Queue()
        self.tracker = tracking.Tracker(self.q_camera_read_green, self.q_camera_read_blue,
                                        False)  # "C:\\Users\\Sander\\Downloads\\ball-tracking\\ball_tracking_example.mp4")

    def exit_handler(self, listener):
        self.tracker.join()
        self.running = False
        listener.join()

    def run(self):
        listener = Thread(target=self.listen)
        listener.start()
        #self.tracker.join()
        self.tracker.start()

        atexit.register(self.exit_handler(listener))

    def listen(self):
        while self.running:
            try:
                datagreen = self.q_camera_read_green.get()
                print("green"+ str(datagreen))
                datablue = self.q_camera_read_blue.get()
                print("blue" + str(datablue))
            except Queue.Empty:
                continue


if __name__ == '__main__':
    tester = TrackingTest()
    tester.start()
