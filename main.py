import cv2
import numpy as np
import time
import HandTracking as ht
import autopy  # Install using "pip install autopy"
import pptControl as pt
import virtual_paint_app as vp
import virtual_keyboard as vkb
import mouse

### Variables Declaration
pTime = 0  # Used to calculate frame rate
width = 640  # Width of Camera
height = 480  # Height of Camera
frameR = 100  # Frame Rate
smoothening = 8  # Smoothening Factor
prev_x, prev_y = 0, 0  # Previous coordinates
curr_x, curr_y = 0, 0  # Current coordinates

ppt_flag: int = 0
vm_flag: int = 0
vpaint_flag: int = 0
vkeyboard_flag: int = 0
active_slide: int = 0
all_finger_up: int = 0
close_flag: int = 0

lm_List = []
cap = cv2.VideoCapture(0)  # Getting video feed from the webcam
cap.set(3, width)  # Adjusting size
cap.set(4, height)
detector = ht.handDetector(maxHands=2)  # Detecting one hand at max

def detect_gesture():
    global pTime, ppt_flag, vm_flag, vpaint_flag, vkeyboard_flag, active_slide, close_flag
    global prev_x, prev_y, curr_x, curr_y, all_finger_up
    global cap
    # Use a breakpoint in the code line below to debug your script.
    print(f'Waiting for gesture detection...')  # Press Ctrl+F8 to toggle the breakpoint.
    screen_width, screen_height = autopy.screen.size()  # Getting the screen size

    while True:
        success, img = cap.read()

        # Check if frame is not read properly then continue to the next iteration to read the next frame.
        if not success:
            continue

        img = cv2.flip(img, 1)

        img = detector.findHands(img)  # Finding the hand

        fingers_statuses, detected_hand = detector.countFingers(img, display=False)
        # print(detected_hand)
        #print(fingers_statuses)
        #time.sleep(0.5)
        #vkb.start_virtual_keyboard()
        lefthand_fingerstatus = dict(list(fingers_statuses.items())[5: 10])
        all_lefthand_finger_up = all(value == True for value in lefthand_fingerstatus.values())
        if detected_hand['LEFT'] == 1 and all_lefthand_finger_up == True:
            print("Command Mode")
            all_finger_up = all(value == True for value in fingers_statuses.values())
            if all_finger_up:
                print("Close the current operation")
                time.sleep(1)
                close_flag = 1

            # 5 + 4
            if fingers_statuses.get('RIGHT_THUMB') == False and fingers_statuses.get('RIGHT_INDEX') == True \
                    and fingers_statuses.get('RIGHT_MIDDLE') == True and fingers_statuses.get('RIGHT_RING') == True \
                    and fingers_statuses.get('RIGHT_PINKY') == True:
                if vpaint_flag == 0:
                    print("Open Virtual Painter")
                    vp.start_virtual_painter()
                    vpaint_flag = 1
                    time.sleep(1)
                    print("Closed Virtual Painter")
                    cap = cv2.VideoCapture(0)


            # 5 + 3
            if fingers_statuses.get('RIGHT_THUMB') == False and fingers_statuses.get('RIGHT_INDEX') == True \
                    and fingers_statuses.get('RIGHT_MIDDLE') == True and fingers_statuses.get('RIGHT_RING') == True \
                    and fingers_statuses.get('RIGHT_PINKY') == False:
                if vkeyboard_flag == 0:
                    print("Enable Virtual Keyboard")
                    vkb.start_virtual_keyboard()
                    vkeyboard_flag = 1
                    time.sleep(1)
                    print("Closed Virtual Keyboard")
                    cap = cv2.VideoCapture(0)

            # 5 + 2
            if fingers_statuses.get('RIGHT_THUMB') == False and fingers_statuses.get('RIGHT_INDEX') == True \
                    and fingers_statuses.get('RIGHT_MIDDLE') == True and fingers_statuses.get('RIGHT_RING') == False \
                    and fingers_statuses.get('RIGHT_PINKY') == False:
                if ppt_flag == 0:
                    print("Open PPT")
                    pt.openPPT()
                    ppt_flag = 1
                    active_slide = 1
                    print(pt.max_slide_len)
                    time.sleep(0.1)
            # 5 + 1
            if fingers_statuses.get('RIGHT_THUMB') == False and fingers_statuses.get('RIGHT_INDEX') == True \
                    and fingers_statuses.get('RIGHT_MIDDLE') == False and fingers_statuses.get('RIGHT_RING') == False \
                    and fingers_statuses.get('RIGHT_PINKY') == False:
                if vm_flag == 0:
                    print("Open Virtual Mouse")
                    vm_flag = 1
                time.sleep(1)

        elif detected_hand['LEFT'] == 0 and detected_hand['RIGHT'] == 1:
                print("Operational Mode")

        lm_List, bbox = detector.findPosition(img)  # Getting xy position of hand landmarks
        if len(lm_List) != 0:
            # print(lmList[8]) # XY coordinate of hand landmarks (8 corresponds to index finger tip)
            fingers = detector.fingersUp()  # Checking if fingers are upwards
            # print(fingers)

            #vm_flag = 1
            if vm_flag == 1:
                x1, y1 = lm_List[8][1:]
                x2, y2 = lm_List[12][1:]
                # Creating boundary box
                cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR), (255, 0, 255), 2)
                if fingers[1] == 1 and fingers[2] == 0:  # If fore finger is up and middle finger is down
                    x3 = np.interp(x1, (frameR, width - frameR), (0, screen_width))
                    y3 = np.interp(y1, (frameR, height - frameR), (0, screen_height))

                    curr_x = prev_x + (x3 - prev_x) / smoothening
                    curr_y = prev_y + (y3 - prev_y) / smoothening

                    autopy.mouse.move(curr_x, curr_y)  # Moving the cursor
                    #mouse.move(curr_x, curr_y, absolute=False, duration=0.2)
                    cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
                    prev_x, prev_y = curr_x, curr_y
                    time.sleep(0.1)

                if fingers[0] == 0 and fingers[1] == 1:  # If fore finger & middle finger both are up
                    length, img, lineInfo = detector.findDistance(4, 8, img)

                    if length < 25:  # If both fingers are really close to each other
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                        #autopy.mouse.click()    # Perform Click
                        mouse.click('left')
                        print("mouse.left single click..")
                        time.sleep(0.5)

                if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:  # If fore finger & middle finger both are up
                    length, img, lineInfo = detector.findDistance(4, 12, img)

                    if length < 25:  # If both fingers are really close to each other
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                        #autopy.mouse.click()    # Perform Click
                        mouse.click('right')
                        print("mouse.right single click..")
                        time.sleep(0.5)

                if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:  # If fore finger & middle finger both are up
                    length, img, lineInfo = detector.findDistance(8, 12, img)

                    if length < 25:  # If both fingers are really close to each other
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                        #autopy.mouse.click()    # Perform Click
                        mouse.click('left')
                        mouse.click('left')
                        print("mouse.left double click..")
                        time.sleep(0.5)


        if ppt_flag == 1:
            if fingers_statuses.get('LEFT_THUMB') == True and fingers_statuses.get('LEFT_MIDDLE') == False:
                if active_slide < pt.max_slide_len:
                    pt.moveNextSlide()
                    active_slide = active_slide + 1
                    print("Right -> Next Slide")
                else:
                    print("Please Check Slide Position")
                time.sleep(1)
            elif fingers_statuses.get('RIGHT_THUMB') == True and fingers_statuses.get('RIGHT_MIDDLE') == False:
                if active_slide > 1:
                    pt.movePreviousSlide()
                    active_slide = active_slide - 1
                    print("Left -> previous Slide")
                else:
                    print("Please Check Slide Position")
                time.sleep(1)

            if close_flag == 1:
                    pt.closePPT()
                    print("PPT Closed")
                    ppt_flag = 0
                    close_flag = 0
                    vpaint_flag = 0
                    vkeyboard_flag = 0

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    detect_gesture()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
