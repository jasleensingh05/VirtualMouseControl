import numpy as np
import cv2
import HandTrackingModule as htm
import time
import autopy
import pyautogui

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
detector = htm.handDetector(detectionCon=0.7, maxHands=1)
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2. Get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]  # coordinates of 8 landmark
        x2, y2 = lmList[12][1:]  # coordinates of 12 landmark
        # print(x1, y1, x2, y2)

        # 3. check which fingers are up
        fingers = detector.fingersUp()
        #print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
        # 4. only index finger : moving mode
        if fingers[0] ==0 and fingers[3] == 0 and fingers[4] == 0:
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
                pyautogui.click(button='left')

            elif fingers[1] == 0 and fingers[2] == 0:
                pyautogui.doubleClick()

            elif fingers[1] == 1 and fingers[2] == 1 and length < 40:

                # 5. Convert coordinates
                x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

                # 6. Smoothen values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                # 7. Move mouse
                autopy.mouse.move(wScr-clocX, clocY)
                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 0, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)