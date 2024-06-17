
import cv2
import numpy as np
import time
import HandTracking as ht
import autopy   # Install using "pip install autopy"
import pptControl as pt

### Variables Declaration
pTime = 0               # Used to calculate frame rate
width = 640             # Width of Camera
height = 480            # Height of Camera
frameR = 100            # Frame Rate
smoothening = 8         # Smoothening Factor
prev_x, prev_y = 0, 0   # Previous coordinates
curr_x, curr_y = 0, 0   # Current coordinates

cap = cv2.VideoCapture(0)   # Getting video feed from the webcam
cap.set(3, width)           # Adjusting size
cap.set(4, height)

detector = ht.handDetector(maxHands=1)                  # Detecting one hand at max
screen_width, screen_height = autopy.screen.size()      # Getting the screen size
while True:
    success, img = cap.read()

    # Check if frame is not read properly then continue to the next iteration to read the next frame.
    if not success:
        continue

    #img = cv2.flip(img, 1)

    img = detector.findHands(img)                       # Finding the hand

    fingers_statuses, count = detector.countFingers(img, display=False)
    print(fingers_statuses) # Show the which all fingers are up or not for right & left hand
    print(count) # Show the which hand is up (right & left hand)
    time.sleep(1)
    ppt_open = True
    if ppt_open == True:
        if fingers_statuses.get('RIGHT_THUMB') == True and fingers_statuses.get('RIGHT_MIDDLE') == False:
            print("Right -> Next Slide")
            pt.moveNextSlide()
            time.sleep(1)

        elif fingers_statuses.get('LEFT_THUMB') == True and fingers_statuses.get('LEFT_MIDDLE') == False:
            print("Left -> previous Slide")
            pt.movePreviousSlide()
            time.sleep(1)

    lmlist, bbox = detector.findPosition(img)           # Getting position of hand
    if len(lmlist)!=0:
        x1, y1 = lmlist[8][1:]
        x2, y2 = lmlist[12][1:]

        fingers = detector.fingersUp()      # Checking if fingers are upwards
        cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR), (255, 0, 255), 2)   # Creating boundary box
        if fingers[1] == 1 and fingers[2] == 0:     # If fore finger is up and middle finger is down
            x3 = np.interp(x1, (frameR,width-frameR), (0,screen_width))
            y3 = np.interp(y1, (frameR, height-frameR), (0, screen_height))

            curr_x = prev_x + (x3 - prev_x)/smoothening
            curr_y = prev_y + (y3 - prev_y) / smoothening

            autopy.mouse.move(screen_width - curr_x, curr_y)    # Moving the cursor
            cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
            prev_x, prev_y = curr_x, curr_y

        if fingers[0] == 0 and fingers[1] == 0:     # If fore finger & middle finger both are up
            length, img, lineInfo = detector.findDistance(4, 8, img)

            if length < 40:     # If both fingers are really close to each other
                #cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                #autopy.mouse.click()    # Perform Click
                print("mouse.click..")
                time.sleep(0.5)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)