# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
import atexit
from collections import deque
from threading import Thread

import cv2
import imutils
import numpy as np


class LaptopTracker(Thread):
    def __init__(self, q_read_green, q_read_blue, q_read_red, camera_path):
        Thread.__init__(self)
        # print("initiated thread")
        self.q_read_blue = q_read_blue
        self.q_read_green = q_read_green
        self.q_read_red = q_read_red
        self.camera_path = camera_path
        self.buffer_size = 64  # buffer_size
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

        # print("initiating colors")
        green_lower = (30, 50, 50)
        green_upper = (75, 255, 255)

        # define lower and upper boundaries of blue
        blue_lower = (100, 100, 100)
        blue_upper = (130, 255, 255)

        red_lower = (166, 84, 141)
        red_upper = (186, 255, 255)

        # print("initiating pts")
        points_green = deque([self.buffer_size])
        points_blue = deque([self.buffer_size])
        points_red = deque([self.buffer_size])

        # if a video path was not supplied, grab the reference
        # to the web-cam
        # print("print getting video")
        if not self.camera_path:
            self.camera = cv2.VideoCapture(0)

        # otherwise, grab a reference to the video file
        else:
            self.camera = cv2.VideoCapture(self.camera_path)

        # print("video selected")
        # keep looping
        while True:
            # grab the current frame
            (grabbed, frame) = self.camera.read()

            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if self.camera_path and not grabbed:
                break

            # resize the frame, blur it, and convert it to the HSV
            # color space

            # print("initiating frames")
            frame_green = imutils.resize(frame, width=600)
            frame_blue = frame_green.copy()
            frame_red = frame_green.copy()

            frame_blue = imutils.resize(frame, width=600)
            frame_red = imutils.resize(frame, width=600)
            # blurred = cv2.GaussianBlur(frame_green, (11, 11), 0)

            hsv_green = cv2.cvtColor(frame_green, cv2.COLOR_BGR2HSV)
            hsv_blue = cv2.cvtColor(frame_blue, cv2.COLOR_BGR2HSV)
            hsv_red = cv2.cvtColor(frame_red, cv2.COLOR_BGR2HSV)

            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask

            # print("initiating masks")
            mask_green = cv2.inRange(hsv_green, green_lower, green_upper)
            mask_green = cv2.erode(mask_green, None, iterations=2)
            mask_green = cv2.dilate(mask_green, None, iterations=2)

            mask_blue = cv2.inRange(hsv_blue, blue_lower, blue_upper)
            mask_blue = cv2.erode(mask_blue, None, iterations=2)
            mask_blue = cv2.dilate(mask_blue, None, iterations=2)

            mask_red = cv2.inRange(hsv_red, red_lower, red_upper)
            mask_red = cv2.erode(mask_red, None, iterations=2)
            mask_red = cv2.dilate(mask_red, None, iterations=2)

            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            # print("initiating contours")
            contours_green = cv2.findContours(mask_green.copy(), cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)[-2]
            center_green = None

            contours_blue = cv2.findContours(mask_blue.copy(), cv2.RETR_EXTERNAL,
                                             cv2.CHAIN_APPROX_SIMPLE)[-2]
            center_blue = None

            contours_red = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)[-2]
            center_red = None

            y_blue = None
            y_green = None
            y_red = None

            # GREEN
            # only proceed if at least one contour was found
            if len(contours_green) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                contour = max(contours_green, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(contour)
                moment = cv2.moments(contour)
                center_green = (int(moment["m10"] / moment["m00"]), int(moment["m01"] / moment["m00"]))
                y_green = (float(center_green[1]) / 450)

                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame_green, (int(x), int(y)), int(radius),
                               (0, 255, 255), 2)
                    cv2.circle(frame_green, center_green, 5, (0, 0, 255), -1)

            # update the points queue
            # print("center_green" + str(center_green))
            points_green.appendleft(center_green)
            self.q_read_green.put(y_green)

            # BLUE
            # only proceed if at least one contour was found
            if len(contours_blue) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                contour = max(contours_blue, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(contour)
                moment = cv2.moments(contour)
                center_blue = (int(moment["m10"] / moment["m00"]), int(moment["m01"] / moment["m00"]))
                y_blue = (float(center_blue[1]) / 450)

                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame_blue, (int(x), int(y)), int(radius),
                               (0, 255, 255), 2)
                    cv2.circle(frame_blue, center_blue, 5, (0, 0, 255), -1)
                    # only proceed if at least one contour was found

            points_blue.appendleft(center_blue)
            self.q_read_blue.put(y_blue)

            # RED
            if len(contours_red) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                contour = max(contours_red, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(contour)
                moment = cv2.moments(contour)
                center_red = (int(moment["m10"] / moment["m00"]), int(moment["m01"] / moment["m00"]))
                y_red = (float(center_red[1]) / 450)

                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame_blue, (int(x), int(y)), int(radius),
                               (0, 255, 255), 2)
                    cv2.circle(frame_blue, center_blue, 5, (0, 0, 255), -1)

            # update the points queue
            points_red.appendleft(center_red)
            self.q_read_red.put(y_red)

            # print("loop over green points")
            # loop over the set of tracked points
            for i in xrange(1, len(points_green)):
                # if either of the tracked points are None, ignore
                # them
                if points_green[i - 1] is None or points_green[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(self.buffer_size / float(i + 1)) * 2.5)
                try:
                    cv2.line(frame_green, points_green[i - 1], points_green[i], (0, 0, 255), thickness)
                except:
                    continue

            # print("loop over blue points")
            for i in xrange(1, len(points_blue)):
                # if either of the tracked points are None, ignore
                # them
                if points_blue[i - 1] is None or points_blue[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(self.buffer_size / float(i + 1)) * 2.5)
                try:
                    cv2.line(frame_blue, points_blue[i - 1], points_blue[i], (0, 0, 255), thickness)
                except:
                    continue

            for i in xrange(1, len(points_red)):
                # if either of the tracked points are None, ignore
                # them
                if points_red[i - 1] is None or points_red[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(self.buffer_size / float(i + 1)) * 2.5)
                try:
                    cv2.line(frame_red, points_red[i - 1], points_red[i], (0, 0, 255), thickness)
                except:
                    continue

            # print("putting masks together")
            # show the frame to our screen
            mask = mask_blue + mask_green + mask_red
            res = cv2.bitwise_and(frame_green, frame_blue, frame_red, mask)
            # cv2.imshow("frame", res)
            cv2.imshow("tracking", frame_red)
            key = cv2.waitKey(1) & 0xFF
            # print("done with masks")

            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break

            # cleanup the camera and close any open windows at exit
            atexit.register(self.exit_handler)
