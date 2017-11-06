# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from collections import deque
from threading import Thread
import numpy as np
import time
import argparse
import imutils
import cv2
import Queue
import atexit
from decimal import Decimal


class LaptopTracker(Thread):
    def __init__(self, q_read_green, q_read_blue, q_read_red, campath):
        Thread.__init__(self)
        #print("initiated thread")
        self.q_read_blue = q_read_blue
        self.q_read_green = q_read_green
        self.q_read_red = q_read_red
        self.campath = campath
        self.buffersize = 64  # buffersize
        self.camera = None

    def exit_handler(self):
        self.camera.release()
        cv2.destroyAllWindows()
        self.join()
        self.q_read_blue.join()
        self.q_read_green.join()

    def run(self):
        self.track()

    def track(self):
        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space, then initialize the
        # list of tracked points

        #print("initiating colors")
        greenLower = (30, 50, 50)
        greenUpper = (75, 255, 255)

        # define lower and upper boundaries of blue
        blueLower = (100, 100, 100)
        blueUpper = (130, 255, 255)

        RedLower = (330, 70, 50)
        RedUpper = (30, 255, 255)

        #print("initiating pts")
        ptsgreen = deque([self.buffersize])
        ptsblue = deque([self.buffersize])
        ptsred = deque([self.buffersize])

        # if a video path was not supplied, grab the reference
        # to the webcam
        #print("print getting video")
        if not self.campath:
            self.camera = cv2.VideoCapture(0)

        # otherwise, grab a reference to the video file
        else:
            self.camera = cv2.VideoCapture(self.campath)

        #print("video selected")
        # keep looping
        while True:
            # grab the current frame
            (grabbed, frame) = self.camera.read()

            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if self.campath and not grabbed:
                break

            # resize the frame, blur it, and convert it to the HSV
            # color space

            #print("initiating frames")
            framegreen = imutils.resize(frame, width=600)
            frameblue = framegreen.copy()
            framered = framegreen.copy()

            frameblue = imutils.resize(frame, width=600)
            framered = imutils.resize(frame, width=600)
            # blurred = cv2.GaussianBlur(framegreen, (11, 11), 0)

            hsvgreen = cv2.cvtColor(framegreen, cv2.COLOR_BGR2HSV)
            hsvblue = cv2.cvtColor(frameblue, cv2.COLOR_BGR2HSV)
            hsvred = cv2.cvtColor(framered, cv2.COLOR_BGR2HSV)

            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask

            #print("initiating masks")
            maskgreen = cv2.inRange(hsvgreen, greenLower, greenUpper)
            maskgreen = cv2.erode(maskgreen, None, iterations=2)
            maskgreen = cv2.dilate(maskgreen, None, iterations=2)

            maskblue = cv2.inRange(hsvblue, blueLower, blueUpper)
            maskblue = cv2.erode(maskblue, None, iterations=2)
            maskblue = cv2.dilate(maskblue, None, iterations=2)

            maskred = cv2.inRange(hsvred, RedLower, RedUpper)
            maskred = cv2.erode(maskred, None, iterations=2)
            maskred = cv2.dilate(maskred, None, iterations=2)

            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            #print("initiating contours")
            cntsgreen = cv2.findContours(maskgreen.copy(), cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)[-2]
            centergreen = None

            cntsblue = cv2.findContours(maskblue.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)[-2]
            centerblue = None

            cntsred = cv2.findContours(maskred.copy(), cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)[-2]
            centerRed = None

            YBlue = None
            Ygreen = None
            YRed = None

            #GREEN
            # only proceed if at least one contour was found
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
            #print("centergreen" + str(centergreen))
            ptsgreen.appendleft(centergreen)
            self.q_read_green.put(Ygreen)


            #BLUE
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

            #RED
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

            #print("loop over green points")
            # loop over the set of tracked points
            for i in xrange(1, len(ptsgreen)):
                # if either of the tracked points are None, ignore
                # them
                if ptsgreen[i - 1] is None or ptsgreen[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(self.buffersize / float(i + 1)) * 2.5)
                try:
                    cv2.line(framegreen, ptsgreen[i - 1], ptsgreen[i], (0, 0, 255), thickness)
                except:
                    continue

            #print("loop over blue points")
            for i in xrange(1, len(ptsblue)):
                # if either of the tracked points are None, ignore
                # them
                if ptsblue[i - 1] is None or ptsblue[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(self.buffersize / float(i + 1)) * 2.5)
                try:
                    cv2.line(frameblue, ptsblue[i - 1], ptsblue[i], (0, 0, 255), thickness)
                except:
                    continue


            for i in xrange(1, len(ptsred)):
                # if either of the tracked points are None, ignore
                # them
                if ptsred[i - 1] is None or ptsred[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(self.buffersize / float(i + 1)) * 2.5)
                try:
                    cv2.line(framered, ptsred[i - 1], ptsred[i], (0, 0, 255), thickness)
                except:
                    continue

            #print("putting masks together")
            # show the frame to our screen
            mask = maskblue + maskgreen + maskred
            res = cv2.bitwise_and(framegreen, frameblue, framered, mask)
            #cv2.imshow("frame", res)
            cv2.imshow("Frameblue", framered)
            key = cv2.waitKey(1) & 0xFF
            #print("done with masks")

            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break

            # cleanup the camera and close any open windows at exit
            atexit.register(self.exit_handler)
