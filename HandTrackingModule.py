import cv2
import mediapipe as mp
import time
import math


class handDetector():
    def __init__(self, mode=False, maxHands=2, model_complexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.model_complexity = model_complexity
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.model_complexity,
                                        self.detectionCon, self.trackCon)  # default parameters
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        RED_COLOR = (0, 0, 255)
        GREEN_COLOR = (8, 255, 8)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # mediapipe can only work on rgb images
        self.results = self.hands.process(imgRGB)  # now we can use hand tracking as the hand is readable
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:  # hand landmarks point to all the different landmarks in the hand.
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                      self.mpHands.HAND_CONNECTIONS, self.mpDraw.DrawingSpec(color=RED_COLOR),
                                      self.mpDraw.DrawingSpec(color=GREEN_COLOR))  # mediapipe predefined function to draw 21 points
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []  # for finding min and max point on x-axis for making a box
        yList = []  # for finding min and max point on x-axis for making a box
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):  #  id defines the indexing for the landmarks
                # print(id, lm)
                h, w, c = img.shape  # tells about the height and width of image in the camera.
                cx, cy = int(lm.x * w), int(lm.y * h)  # coordinates with the unit as pixels.
                #  print(id, cx, cy)  # coordinates (x,y) with indexing
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                #  if id == 4 or id == 8 or id == 12 or id == 16 or id == 20:
                if draw:
                    cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax  # it will provide with the bounding box

            if draw:
                cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        #  Thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 Fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True):
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]  # coordinates of landmark 4
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]  # coordinates of landmark 8
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        #if len(lmList) != 0:
        #    print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()
