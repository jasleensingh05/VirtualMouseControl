import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()  # default parameters
mpDraw = mp.solutions.drawing_utils
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (8,255,8)

pTime = 0
cTime = 0

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # mediapipe can only work on rgb images
    results = hands.process(imgRGB)  # now we can use hand tracking as the hand is readable
    print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:  # hand landmarks point to all the different landmarks in the hand.
            for id, lm in enumerate(handLms.landmark):  # id defines the indexing for the landmarks
                # print(id, lm)
                h, w, c = img.shape  # tells about the height and width of image in the camera.
                cx, cy = int(lm.x*w), int(lm.y*h)  # coordinates with the unit as pixels.
                print(id, cx, cy)  # coordinates (x,y) with indexing
                if id == 4 or id == 8 or id == 12 or id == 16 or id == 20:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            mpDraw.draw_landmarks(img, handLms,
                                  mpHands.HAND_CONNECTIONS, mpDraw.DrawingSpec(color=RED_COLOR),
            mpDraw.DrawingSpec(color=GREEN_COLOR))  # mediapipe predefined function to draw 21 points

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 255), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
