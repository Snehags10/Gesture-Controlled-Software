import mediapipe as mp
import cv2
import numpy as np
import time
import HandTracking as ht_t1
detector_t1 = ht_t1.handDetector(maxHands=2)  # Detecting one hand at max

#contents
ml = 150
max_x, max_y = 299+ml, 50
curr_tool = "select tool"
time_init = True
rad = 40
var_inits = False
thick = 4
prevx, prevy = 0,0
#get tools function
def getTool(x):
    global ml
    if x < 50 + ml:
        return "line"

    elif x<100 + ml:
        return "rectangle"

    elif x < 150 + ml:
        return "draw"

    elif x<200 + ml:
        return "circle"

    elif x<250 + ml:
        return "erase"

    else:
        return "erase_all"

def index_raised(yi, y9):
    if (y9 - yi) > 40:
        return True

    return False

def start_virtual_painter():
    global curr_tool, var_inits
    hands = mp.solutions.hands
    hand_landmark = hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6, max_num_hands=1)
    draw = mp.solutions.drawing_utils

    # drawing tools
    tools = cv2.imread("tools.png")
    tools = tools.astype('uint8')

    mask = np.ones((480, 640))*255
    mask = mask.astype('uint8')
    '''
    tools = np.zeros((max_y+5, max_x+5, 3), dtype="uint8")
    cv2.rectangle(tools, (0,0), (max_x, max_y), (0,0,255), 2)
    cv2.line(tools, (50,0), (50,50), (0,0,255), 2)
    cv2.line(tools, (100,0), (100,50), (0,0,255), 2)
    cv2.line(tools, (150,0), (150,50), (0,0,255), 2)
    cv2.line(tools, (200,0), (200,50), (0,0,255), 2)
    '''
    vp_loop_flag = True
    cap = cv2.VideoCapture(0)
    while vp_loop_flag:
        _, frm = cap.read()
        frm = cv2.flip(frm, 1)

        frame_t1 = frm
        frame_t1 = detector_t1.findHands(frame_t1, draw=False)  # Finding the hand
        fingers_statuses_t1, detected_hand_t1 = detector_t1.countFingers(frame_t1, display=False)
        all_finger_up_t1 = all(value == True for value in fingers_statuses_t1.values())
        if all_finger_up_t1:
            print("Close the current operation")
            #time.sleep(1)
            #cv2.destroyAllWindows()
            cv2.destroyWindow("paint app")
            #cap.release()
            vp_loop_flag = False

        else:
            rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
            op = hand_landmark.process(rgb)

            if op.multi_hand_landmarks:

                for i in op.multi_hand_landmarks:
                    draw.draw_landmarks(frm, i, hands.HAND_CONNECTIONS)
                    x, y = int(i.landmark[8].x*640), int(i.landmark[8].y*480)

                    if x < max_x and y < max_y and x > ml:
                        if time_init:
                            ctime = time.time()
                            time_init = False
                        ptime = time.time()

                        cv2.circle(frm, (x, y), rad, (0,255,255), 2)
                        rad -= 1

                        if (ptime - ctime) > 0.8:
                            curr_tool = getTool(x)
                            print("your current tool set to : ", curr_tool)
                            time_init = True
                            rad = 40

                    else:
                        time_init = True
                        rad = 40

                    if curr_tool == "draw":
                        xi, yi = int(i.landmark[12].x*640), int(i.landmark[12].y*480)
                        y9 = int(i.landmark[9].y*480)

                        if index_raised(yi, y9):
                            cv2.line(mask, (prevx, prevy), (x, y), 0, thick)
                            prevx, prevy = x, y

                        else:
                            prevx = x
                            prevy = y

                    elif curr_tool == "line":
                        xi, yi = int(i.landmark[12].x*640), int(i.landmark[12].y*480)
                        y9 = int(i.landmark[9].y*480)

                        if index_raised(yi, y9):
                            if not(var_inits):
                                xii, yii = x, y
                                var_inits = True

                            cv2.line(frm, (xii, yii), (x, y), (50,152,255), thick)

                        else:
                            if var_inits:
                                cv2.line(mask, (xii, yii), (x, y), 0, thick)
                                var_inits = False

                    elif curr_tool == "rectangle":
                        xi, yi = int(i.landmark[12].x*640), int(i.landmark[12].y*480)
                        y9  = int(i.landmark[9].y*480)

                        if index_raised(yi, y9):
                            if not(var_inits):
                                xii, yii = x, y
                                var_inits = True

                            cv2.rectangle(frm, (xii, yii), (x, y), (0,255,255), thick)

                        else:
                            if var_inits:
                                cv2.rectangle(mask, (xii, yii), (x, y), 0, thick)
                                var_inits = False

                    elif curr_tool == "circle":
                        xi, yi = int(i.landmark[12].x*640), int(i.landmark[12].y*480)
                        y9 = int(i.landmark[9].y*480)

                        if index_raised(yi, y9):
                            if not(var_inits):
                                xii, yii = x, y
                                var_inits = True

                            cv2.circle(frm, (xii, yii), int(((xii-x)**2 + (yii-y)**2)**0.5), (255,255,0), thick)

                        else:
                            if var_inits:
                                cv2.circle(mask, (xii, yii), int(((xii-x)**2 + (yii-y)**2)**0.5), (0,255,0), thick)
                                var_inits = False

                    elif curr_tool == "erase":
                        xi, yi = int(i.landmark[12].x*640), int(i.landmark[12].y*480)
                        y9  = int(i.landmark[9].y*480)

                        if index_raised(yi, y9):
                            cv2.circle(frm, (x, y), 30, (0,0,0), -1)
                            cv2.circle(mask, (x, y), 30, 255, -1)

                    elif curr_tool == "erase_all":
                        xi, yi = int(i.landmark[12].x*640), int(i.landmark[12].y*480)
                        y9  = int(i.landmark[9].y*480)

                        if index_raised(yi, y9):
                            cv2.circle(frm, (x, y), 30, (0,0,0), -1)
                            cv2.rectangle(mask, (5, 5), (2000, 2000), 255, -1)

            op = cv2.bitwise_and(frm, frm, mask=mask)
            frm[:, :, 1] = op[:, :, 1]
            frm[:, :, 2] = op[:, :, 2]

            frm[:max_y, ml:max_x] = cv2.addWeighted(tools, 0.7, frm[:max_y, ml:max_x], 0.3, 0)
            cv2.putText(frm, curr_tool, (299+ml,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            cv2.imshow("paint app", frm)

        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            cap.release()
            break
