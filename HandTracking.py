import cv2  # Can be installed using "pip install opencv-python"
import mediapipe as mp  # Can be installed using "pip install mediapipe"
import time
import math
import numpy as np


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=False, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):    # Finds all hands in a frame
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):   # Fetches the position of hands
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                              (0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self):    # Checks which fingers are up
        fingers = []
        # Thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):

            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # totalFingers = fingers.count(1)

        return fingers

    def findDistance(self, p1, p2, img, draw=True,r=15, t=3):   # Finds distance between two fingers
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]

    def countFingers(self, img, display=True):

        # Initialize a dictionary to store the count of fingers of both hands.
        count = {'RIGHT': 0, 'LEFT': 0}

        # Store the indexes of the tips landmarks of each finger of a hand in a list.
        fingers_tips_ids = [self.mpHands.HandLandmark.INDEX_FINGER_TIP, self.mpHands.HandLandmark.MIDDLE_FINGER_TIP,
                            self.mpHands.HandLandmark.RING_FINGER_TIP, self.mpHands.HandLandmark.PINKY_TIP]

        # Initialize a dictionary to store the status (i.e., True for open and False for close) of each finger of both hands.
        fingers_statuses = {'RIGHT_THUMB': False, 'RIGHT_INDEX': False, 'RIGHT_MIDDLE': False, 'RIGHT_RING': False,
                            'RIGHT_PINKY': False, 'LEFT_THUMB': False, 'LEFT_INDEX': False, 'LEFT_MIDDLE': False,
                            'LEFT_RING': False, 'LEFT_PINKY': False}

        if self.results.multi_hand_landmarks:
            # Get the height and width of the input image.
            height, width, _ = img.shape

            # Iterate over the found hands in the image.
            for hand_index, hand_info in enumerate(self.results.multi_handedness):

                # Retrieve the label of the found hand.
                hand_label = hand_info.classification[0].label

                # Retrieve the landmarks of the found hand.
                hand_landmarks = self.results.multi_hand_landmarks[hand_index]

                # Iterate over the indexes of the tips landmarks of each finger of the hand.
                for tip_index in fingers_tips_ids:

                    # Retrieve the label (i.e., index, middle, etc.) of the finger on which we are iterating upon.
                    finger_name = tip_index.name.split("_")[0]

                    # Check if the finger is up by comparing the y-coordinates of the tip and pip landmarks.
                    if (hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y):
                        # Update the status of the finger in the dictionary to true.
                        fingers_statuses[hand_label.upper() + "_" + finger_name] = True

                        # Increment the count of the fingers up of the hand by 1.
                        # count[hand_label.upper()] += 1

                # Retrieve the y-coordinates of the tip and mcp landmarks of the thumb of the hand.
                thumb_tip_x = hand_landmarks.landmark[self.mpHands.HandLandmark.THUMB_TIP].x
                thumb_mcp_x = hand_landmarks.landmark[self.mpHands.HandLandmark.THUMB_TIP - 2].x
                thumb_tip_y = hand_landmarks.landmark[self.mpHands.HandLandmark.THUMB_TIP].y
                index_tip_y = hand_landmarks.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP].y


                # Check if the thumb is up by comparing the hand label and the x-coordinates of the retrieved landmarks.
                if (hand_label == 'Right' and (thumb_tip_x < thumb_mcp_x)):
                    # Update the status of the thumb in the dictionary to true.
                    fingers_statuses[hand_label.upper() + "_THUMB"] = True

                    # Increment the count of the fingers up of the hand by 1.
                    count[hand_label.upper()] += 1
                    #print("Right -> Next Slide")


                    # Check if the thumb is up by comparing the hand label and the x-coordinates of the retrieved landmarks.
                if (hand_label == 'Left' and (thumb_tip_x > thumb_mcp_x)):
                    # Update the status of the thumb in the dictionary to true.
                    fingers_statuses[hand_label.upper() + "_THUMB"] = True

                    # Increment the count of the fingers up of the hand by 1.
                    count[hand_label.upper()] += 1
                    #print("Left -> Previous Slide")


        else:
            print("No hand..")
            # Return the output image, the status of each finger and the count of the fingers up of both hands.
        return fingers_statuses, count


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()