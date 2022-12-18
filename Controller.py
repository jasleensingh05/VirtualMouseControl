import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import autopy
import pyautogui
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

####
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
####

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)  # to set width of the camera
cap.set(4, hCam)  # to set height of the camera


detector = htm.handDetector(detectionCon=0.8, maxHands=1)
wScr, hScr = autopy.screen.size()

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
colorBri = (255, 0, 0)
grabHand = False

while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter based on size
        area = ((bbox[2]-bbox[0])*(bbox[3]-bbox[1]))//100
        #print(area)
        if 250 < area < 1000:
            # working area of volume
            #print("yes")
            # Find Distance between index and Thumb
            length, img, lineinfo = detector.findDistance(4, 8, img, draw=False)
            #print(length)


            ######## Volume Control ########
            # Convert Volume
            # vol = np.interp(length, [50, 225], [minVol, maxVol])  # convert hand range to volume range
            volBar = np.interp(length, [35, 200], [400, 150]) #to set scale for volume
            volPer = np.interp(length, [35, 200], [0, 100])
            # print(int(length), vol)
            # volume.SetMasterVolumeLevel(vol, None)

            # Reduce Resolution to make it smoother
            smoothness = 2
            volPer = smoothness * round(volPer/smoothness)

            # Check fingers up
            fingers = detector.fingersUp()
            # print(fingers)
            # if pinky is down set volume
            if not fingers[4] and not fingers[3] and not fingers[2] and fingers[1] and fingers[0]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                detector.findDistance(4, 8, img, draw=True)
                #cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (0, 255, 0), cv2.FILLED)
                #cv2.circle(img, (lineinfo[0], lineinfo[1]), 15, (255, 0, 255), cv2.FILLED)
                #cv2.circle(img, (lineinfo[2], lineinfo[3]), 15, (255, 0, 255), cv2.FILLED)
                #cv2.line(img, (lineinfo[0], lineinfo[1]), (lineinfo[2], lineinfo[3]), (255, 0, 255), 3)

                # Drawing
                cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
                cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
                cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (255, 0, 0), 3)
                colorVol = (0, 255, 0)  # Green Color  # set volume color
            else:
                colorVol = (255, 0, 0)  # Blue Color


            ######## Brightness Control #######
            briBar = np.interp(length, [35, 150], [400, 150])
            briPer = np.interp(length, [35, 150], [0, 100])

            smoothnessB = 10
            briPer = smoothnessB * round(briPer/smoothnessB)

            # Check fingers up
            fingers = detector.fingersUp()
            # print(fingers)
            # if pinky is down set volume
            if not fingers[3] and not fingers[2] and fingers[1] and fingers[0] and fingers[4]:
                sbc.set_brightness(int(briPer))
                detector.findDistance(4, 8, img, draw=True)

                # Drawing
                cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
                cv2.rectangle(img, (50, int(briBar)), (85, 400), (255, 0, 0), cv2.FILLED)
                cv2.putText(img, f'{int(briPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (255, 0, 0), 3)
                colorBri = (0, 255, 0)
            else:
                colorBri = (255, 0, 0)

        ########### Mouse Control ##############
        x1, y1 = lmList[8][1:]  # coordinates of 8 landmark
        x2, y2 = lmList[12][1:]  # coordinates of 12 landmark
        # print(x1, y1, x2, y2)

        # 3. check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
        # 4. only index finger : moving mode
        if fingers[0] == 0 and fingers[3] == 0 and fingers[4] == 0:
            length, img, lineinfo = detector.findDistance(8, 12, img)
            # 8. Both index and middle fingers are up: Clicking mode
            if fingers[1] == 1 and fingers[2] == 0:
                # 9. Find Distance between  fingers

                # print(lineinfo[0], lineinfo[1], lineinfo[2], lineinfo[3])
                # 10. Click mouse if distance short
                '''if length < 40 and lineinfo[3] > lineinfo[1]:
                    cv2.circle(img, (lineinfo[4], lineinfo[5]),10, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click() '''
                pyautogui.click(button='right')

            elif fingers[1] == 0 and fingers[2] == 1:
                pyautogui.click(button='left', clicks=1, interval=0.8)

            elif fingers[1] == 0 and fingers[2] == 0:
                pyautogui.doubleClick()

            elif fingers[1] == 1 and fingers[2] == 1 and length < 40:

                # 5. Convert coordinates
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                # 6. Smoothen values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                # 7. Move mouse
                autopy.mouse.move(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

                if grabHand:
                    grabHand = False
                    pyautogui.mouseUp(button="left")

            elif fingers[1] == 1 and fingers[2] == 1 and length>60:

                # 5. Convert coordinates
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                # 6. Smoothen values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                # 7. Move mouse
                autopy.mouse.move(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

                if not grabHand:
                    grabHand = True
                    pyautogui.mouseDown(button="left")
            #### Scroll ####
        elif fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 1:
            pyautogui.scroll(300)
        elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            pyautogui.scroll(-300)

    # Drawings

    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (420, 40), cv2.FONT_HERSHEY_COMPLEX, 0.9,
                colorVol, 3)
    cBri = sbc.get_brightness()
    cv2.putText(img, f'Bri Set: {cBri}', (420, 80), cv2.FONT_HERSHEY_COMPLEX, 0.9,
                colorBri, 3)

    # Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 0, 0), 3)
    cv2.imshow("Img", img)
    cv2.waitKey(1)
