# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

import Queue
import atexit
import cv2
import imutils
import numpy as np
import time
# import the necessary packages
from collections import deque
from picamera import PiCamera
from picamera.array import PiRGBArray
from threading import Thread


class Tracker(Thread):
    def __init__(self, q_read_green, q_read_blue, q_read_red, campath):
        Thread.__init__(self)
        self.q_read_blue = q_read_blue
        self.q_read_green = q_read_green
        self.q_read_red = q_read_red
        self.campath = campath
        self.buffersize = 64  # buffersize
        self.camera = None

        self.calibrating = True

    def exit_handler(self):
        self.camera.release()
        cv2.destroyAllWindows()
        self.join()

    def run(self):
        self.track()

    def track(self):
        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space, then initialize the
        # list of tracked points
        try:
            pi = False

            greenLower = (40, 122, 129)
            greenUpper = (86,255,255)

            # define lower and upper boundaries of blue
            blueLower = (97, 100, 117)
            blueUpper = (117,255,255)

            RedLower = (23, 59, 119) # yellow
            RedUpper = (54,255,255) # yellow

            ptsgreen = deque([self.buffersize])
            ptsblue = deque([self.buffersize])
            ptsred = deque([self.buffersize])

            # if a video path was not supplied, grab the reference
            # to the webcam
            if self.campath == "pi":
                self.camera = PiCamera()
                self.camera.resolution = (320, 240)
                self.camera.framerate = 16
                rawCapture = PiRGBArray(self.camera, size=(320, 240))
                pi = True
                time.sleep(0.1)
                print("picam setup")

            # keep looping
            while True:
                print("entering loop")
                # grab the current frame
                if pi == True:
                    for frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                        # grab the raw NumPy array representing the image, then initialize the timestamp
                        # and occupied/unoccupied text
                        frame = frame.array

                        # resize the frame, blur it, and convert it to the HSV
                        # color space
                        framegreen = imutils.resize(frame, width=320)
                        if self.calibrating:
                            frameblue = framegreen.copy()
                            framered = framegreen.copy()

                            frameblue = imutils.resize(frame, width=320)
                            framered = imutils.resize(frame, width=320)

                        # blurred = cv2.GaussianBlur(framegreen, (11, 11), 0)
                        hsvgreen = cv2.cvtColor(framegreen, cv2.COLOR_BGR2HSV)
                        if self.calibrating:
                            hsvblue = cv2.cvtColor(frameblue, cv2.COLOR_BGR2HSV)
                            hsvred = cv2.cvtColor(framered, cv2.COLOR_BGR2HSV)

                        # construct a mask for the color "green", then perform
                        # a series of dilations and erosions to remove any small
                        # blobs left in the mask
                        maskgreen = cv2.inRange(hsvgreen, greenLower, greenUpper)
                        maskgreen = cv2.erode(maskgreen, None, iterations=2)
                        maskgreen = cv2.dilate(maskgreen, None, iterations=2)

                        if self.calibrating:
                            maskblue = cv2.inRange(hsvblue, blueLower, blueUpper)
                            maskblue = cv2.erode(maskblue, None, iterations=2)
                            maskblue = cv2.dilate(maskblue, None, iterations=2)

                            maskred = cv2.inRange(hsvred, RedLower, RedUpper)
                            maskred = cv2.erode(maskred, None, iterations=2)
                            maskred = cv2.dilate(maskred, None, iterations=2)

                        # find contours in the mask and initialize the current
                        # (x, y) center of the ball
                        cntsgreen = cv2.findContours(maskgreen.copy(), cv2.RETR_EXTERNAL,
                                                     cv2.CHAIN_APPROX_SIMPLE)[-2]
                        centergreen = None

                        if self.calibrating:
                            cntsblue = cv2.findContours(maskblue.copy(), cv2.RETR_EXTERNAL,
                                                        cv2.CHAIN_APPROX_SIMPLE)[-2]
                            centerblue = None

                            cntsred = cv2.findContours(maskred.copy(), cv2.RETR_EXTERNAL,
                                                       cv2.CHAIN_APPROX_SIMPLE)[-2]
                            centerRed = None

                        # GREEN
                        # only proceed if at least one contour was found
                        Ygreen = None
                        if len(cntsgreen) > 0:
                            # find the largest contour in the mask, then use
                            # it to compute the minimum enclosing circle and
                            # centroid
                            c = max(cntsgreen, key=cv2.contourArea)
                            ((x, y), radius) = cv2.minEnclosingCircle(c)
                            M = cv2.moments(c)
                            centergreen = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                            Ygreen = (float(centergreen[1]) / 450)

                            # only proceed if the radius meets a minimum size
                            if radius > 10:
                                # draw the circle and centroid on the frame,
                                # then update the list of tracked points
                                cv2.circle(framegreen, (int(x), int(y)), int(radius),
                                           (0, 255, 255), 2)
                                cv2.circle(framegreen, centergreen, 5, (0, 0, 255), -1)

                        # update the points queue
                        # print("centergreen" + str(centergreen))
                        ptsgreen.appendleft(centergreen)
                        self.q_read_green.put(Ygreen)

                        if self.calibrating:
                            YBlue = None
                            # BLUE
                            # only proceed if at least one contour was found
                            if len(cntsblue) > 0:
                                # find the largest contour in the mask, then use
                                # it to compute the minimum enclosing circle and
                                # centroid
                                c = max(cntsblue, key=cv2.contourArea)
                                ((x, y), radius) = cv2.minEnclosingCircle(c)
                                M = cv2.moments(c)
                                centerblue = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                                YBlue = (float(centerblue[1]) / 450)

                                # only proceed if the radius meets a minimum size
                                if radius > 10:
                                    # draw the circle and centroid on the frame,
                                    # then update the list of tracked points
                                    cv2.circle(frameblue, (int(x), int(y)), int(radius),
                                               (0, 255, 255), 2)
                                    cv2.circle(frameblue, centerblue, 5, (0, 0, 255), -1)
                                    # only proceed if at least one contour was found

                            ptsblue.appendleft(centerblue)
                            self.q_read_blue.put(YBlue)
                            YRed = None

                            # RED
                            if len(cntsred) > 0:
                                # find the largest contour in the mask, then use
                                # it to compute the minimum enclosing circle and
                                # centroid
                                c = max(cntsred, key=cv2.contourArea)
                                ((x, y), radius) = cv2.minEnclosingCircle(c)
                                M = cv2.moments(c)
                                centerRed = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                                YRed = (float(centerRed[1]) / 450)

                                # only proceed if the radius meets a minimum size
                                if radius > 10:
                                    # draw the circle and centroid on the frame,
                                    # then update the list of tracked points
                                    cv2.circle(frameblue, (int(x), int(y)), int(radius),
                                               (0, 255, 255), 2)
                                    cv2.circle(frameblue, centerblue, 5, (0, 0, 255), -1)

                            # update the points queue
                            ptsred.appendleft(centerRed)
                            self.q_read_red.put(YRed)

                        rawCapture.truncate(0)


        # cleanup the camera and close any open windows at exit
        except KeyboardInterrupt:
            self.camera.release()
            cv2.destroyAllWindows()
