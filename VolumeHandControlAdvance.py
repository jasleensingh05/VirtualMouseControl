import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

####
wCam, hCam = 640, 480
####

cap = cv2.VideoCapture(0)
cap.set(3, wCam)  # to set width of the camera
cap.set(4, hCam)  # to set height of the camera
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
# Template for audio control

minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)
while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img, draw=True)
    if len(lmlist) != 0:

        # Filter based on size
        area = ((bbox[2]-bbox[0])*(bbox[3]-bbox[1]))//100
        #print(area)
        if 250 < area < 1000:
            #print("yes")
            # Find Distance between index and Thumb
            length, img, lineinfo = detector.findDistance(4, 8, img, draw=False)
            print(length)

            # Convert Volume
            # vol = np.interp(length, [50, 225], [minVol, maxVol])  # convert hand range to volume range
            volBar = np.interp(length, [50, 200], [400, 150]) #to set scale for volume
            volPer = np.interp(length, [50, 200], [0, 100])
            # print(int(length), vol)
            # volume.SetMasterVolumeLevel(vol, None)

            # Reduce Resolution to make it smoother
            smoothness = 2
            volPer = smoothness * round(volPer/smoothness)

            # Check fingers up
            fingers = detector.fingersUp()
            # print(fingers)
            # if pinky is down set volume
            if not fingers[4] and not fingers[3] and not fingers[2]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                detector.findDistance(4, 8, img, draw=True)
                #cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (0, 255, 0), cv2.FILLED)
                #cv2.circle(img, (lineinfo[0], lineinfo[1]), 15, (255, 0, 255), cv2.FILLED)
                #cv2.circle(img, (lineinfo[2], lineinfo[3]), 15, (255, 0, 255), cv2.FILLED)
                #cv2.line(img, (lineinfo[0], lineinfo[1]), (lineinfo[2], lineinfo[3]), (255, 0, 255), 3)
                colorVol = (0, 255, 0)  # set volume color
            else:
                colorVol = (255, 0, 0)
    # Drawings
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 0, 0), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                colorVol, 3)

    # Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 0, 0), 3)
    cv2.imshow("Img", img)
    cv2.waitKey(1)
