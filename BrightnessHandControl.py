import cv2
import time
import numpy as np
import HandTrackingModule as htm
import screen_brightness_control as sbc
import math

####
wCam, hCam = 640, 480
####

cap = cv2.VideoCapture(0)
cap.set(3, wCam)  # to set width of the camera
cap.set(4, hCam)  # to set height of the camera
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)
area = 0
while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter based on size
        area = ((bbox[2]-bbox[0])*(bbox[3]-bbox[1]))//100
        # print(area)
        if 250 < area < 1000:
            # print("yes")>
            # Find Distance between index and Thumb
            length, img, lineinfo = detector.findDistance(4, 8, img, draw=False)
            print(length)

            briPer = np.interp(length, [50, 150], [0, 100])

            smoothnessB = 10
            briPer = smoothnessB * round(briPer/smoothnessB)

            # Check fingers up
            fingers = detector.fingersUp()
            # print(fingers)
            # if pinky is down set volume
            if not fingers[3] and not fingers[2] and fingers[4]:
                sbc.set_brightness(int(briPer))
                detector.findDistance(4, 8, img, draw=True)
                #cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (0, 255, 0), cv2.FILLED)
                #cv2.circle(img, (lineinfo[0], lineinfo[1]), 15, (255, 0, 255), cv2.FILLED)
                #cv2.circle(img, (lineinfo[2], lineinfo[3]), 15, (255, 0, 255), cv2.FILLED)
                #cv2.line(img, (lineinfo[0], lineinfo[1]), (lineinfo[2], lineinfo[3]), (255, 0, 255), 3
    # Drawings

    # Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 0, 0), 3)
    cv2.imshow("Img", img)
    cv2.waitKey(1)
