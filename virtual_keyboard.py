import cv2
import mediapipe as mp
import numpy as np
import math
from pynput.keyboard import Controller
import time
import HandTracking as ht_t2

detector_t2 = ht_t2.handDetector(maxHands=2)  # Detecting one hand at max

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpdraw = mp.solutions.drawing_utils

keyboard = Controller()

cap = cv2.VideoCapture(0)
cap.set(2, 150)

text = ""
tx = ""
app = 0
delay = 0
buttonList = []
buttonList1 = []
list = []
win_xaxis = 100
win_yaxis = 100

class Button():
    def __init__(self, pos, text, size=[70, 70]):
        self.pos = pos
        self.size = size
        self.text = text


keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BP", "CLR"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "/", "SP"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "UP", "DN", "CAP"]]

keys1 = [["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "BP", "CLR"],
         ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "/", "SP"],
         ["z", "x", "c", "v", "b", "n", "m", ",", ".", "LT", "RT", "CAP"]]


def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (96, 96, 96), cv2.FILLED)
        cv2.putText(img, button.text, (x + 10, y + 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return img


but_xaxis: int = 80
but_yaxis: int = 80

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([but_xaxis * j + 10, but_yaxis * i + 10], key))
for i in range(len(keys1)):
    for j, key in enumerate(keys1[i]):
        buttonList1.append(Button([but_xaxis * j + 10, but_yaxis * i + 10], key))


def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def start_virtual_keyboard():
    global app, delay, text, win_xaxis, win_yaxis
    offset = 25
    x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
    y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
    coff = np.polyfit(x, y, 2)
    vkb_loop_flag = True
    while vkb_loop_flag == True:
        sucess, frame = cap.read()
        frame = cv2.resize(frame, (1000, 580))
        frame = cv2.flip(frame, 1)

        frame_t2 = frame
        frame_t2 = detector_t2.findHands(frame_t2, draw=False)  # Finding the hand
        fingers_statuses_t2, detected_hand_t2 = detector_t2.countFingers(frame_t2, display=False)
        all_finger_up_t2 = all(value == True for value in fingers_statuses_t2.values())
        if all_finger_up_t2:
            print("Close the current operation")
            time.sleep(1)
            cv2.destroyWindow("virtual keyboard")
            # cap.release()
            vkb_loop_flag = False
        else:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(img)
            lanmark = []
            if app == 0:
                frame = drawAll(frame, buttonList)
                list = buttonList
                r = "on"

            if app == 1:
                frame = drawAll(frame, buttonList1)
                list = buttonList1
                r = "off"

            if results.multi_hand_landmarks:
                for hn in results.multi_hand_landmarks:
                    for id, lm in enumerate(hn.landmark):
                        hl, wl, cl = frame.shape
                        cx, cy = int(lm.x * wl), int(lm.y * hl)
                        lanmark.append([id, cx, cy])

            if lanmark != 0:
                try:
                    x5, y5 = lanmark[5][1], lanmark[5][2]
                    x17, y17 = lanmark[17][1], lanmark[17][2]
                    dis = calculate_distance(x5, y5, x17, y17)
                    A, B, C = coff
                    distanceCM = A * dis ** 2 + B * dis + C
                    if 20 < distanceCM < 50:

                        x, y = lanmark[8][1], lanmark[8][2]
                        x2, y2 = lanmark[6][1], lanmark[6][2]
                        x3, y3 = lanmark[12][1], lanmark[12][2]
                        cv2.circle(frame, (x, y), 20, (255, 0, 255), cv2.FILLED)
                        cv2.circle(frame, (x3, y3), 20, (255, 0, 255), cv2.FILLED)

                        if y2 > y:

                            for button in list:
                                xb, yb = button.pos
                                wb, hb = button.size

                                if (xb < x < xb + wb) and (yb < y < yb + hb):
                                    cv2.rectangle(frame, (xb - 5, yb - 5), (xb + wb + 5, yb + hb + 5), (160, 160, 160),
                                                  cv2.FILLED)
                                    cv2.putText(frame, button.text, (xb + 20, yb + 65), cv2.FONT_HERSHEY_PLAIN, 4,
                                                (255, 255, 255), 4)
                                    dis = calculate_distance(x, y, x3, y3)
                                    print(dis)
                                    if dis < 50 and delay == 0:
                                        k = button.text
                                        cv2.rectangle(frame, (xb - 5, yb - 5), (xb + wb + 5, yb + hb + 5),
                                                      (255, 255, 255),
                                                      cv2.FILLED)
                                        cv2.putText(frame, k, (xb + 20, yb + 65), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0),
                                                    4)

                                        if k == "SP":
                                            tx = ' '
                                            text += tx
                                            keyboard.press(tx)

                                        elif k == "BP":
                                            tx = text[: -1]
                                            text = ""
                                            text += tx
                                            keyboard.press('\b')

                                        elif k == "CLR":
                                            text = ""

                                        elif k == "CAP" and r == "on":
                                            app = 1
                                            time.sleep(0.1)

                                        elif k == "CAP" and r == "off":
                                            app = 0
                                            time.sleep(0.1)

                                        elif k == "UP":
                                            time.sleep(0.1)
                                            if win_yaxis>50:
                                                win_yaxis = win_yaxis - offset

                                        elif k == "DN":
                                            time.sleep(0.1)
                                            win_yaxis = win_yaxis + offset

                                        elif k == "LT":
                                            time.sleep(0.1)
                                            if win_xaxis > 50:
                                                win_xaxis = win_xaxis - offset

                                        elif k == "RT":
                                            time.sleep(0.1)
                                            win_xaxis = win_xaxis + offset

                                        else:
                                            text += k
                                            keyboard.press(k)
                                        delay = 1


                except:
                    pass

            if delay != 0:
                delay += 1
                if delay > 10:
                    delay = 0
            cv2.namedWindow('virtual keyboard', cv2.WINDOW_AUTOSIZE)
            cv2.rectangle(frame, (20, 250), (850, 400), (255, 255, 255), cv2.FILLED)
            cv2.putText(frame, text, (30, 300), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
            cv2.imshow('virtual keyboard', frame)
            cv2.moveWindow('virtual keyboard', win_xaxis, win_yaxis)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
