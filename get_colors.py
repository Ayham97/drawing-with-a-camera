import cv2
import numpy as np
hand_hist = None
traverse_point = []
total_rectangle = 7
hand_rect_one_x = None
hand_rect_one_y = None
hand_rect_two_x = None
hand_rect_two_y = None
blue_lower = np.array([100, 150, 0], np.uint8)
blue_upper = np.array([140, 255, 255], np.uint8)
green_lower = np.array([45,60,60], np.uint8)
green_upper = np.array([80,255,255], np.uint8)
red_lower1 = np.array([0, 70, 50], np.uint8)
red_upper1 = np.array([10, 255, 255], np.uint8)
red_lower2 = np.array([170, 70, 50], np.uint8)
red_upper2 = np.array([180, 255, 255], np.uint8)


def maximum(x1,x2,x3,x4):
    if x1>=x2 and x1>=x3 and x1>=x4:
        return blue_lower,blue_upper
    if x2>=x1 and x2>=x3 and x2>=x4:
        return green_lower,green_upper
    if x3>=x1 and x3>=x2 and x3>=x4:
        return red_lower1,red_upper1
    if x4>=x1 and x4>=x2 and x4>=x1:
        return red_lower2,red_upper2


def pen_color(frame):
    global hand_rect_one_x, hand_rect_one_y
    blue_cnt=0
    green_cnt = 0
    red1_cnt = 0
    red2_cnt = 0
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #creates
    roi = np.zeros([70, 10, 3], dtype=hsv_frame.dtype)

    for i in range(total_rectangle):
        roi[i * 10: i * 10 + 10, 0: 10] = hsv_frame[hand_rect_one_x[i]:hand_rect_one_x[i] + 10,
                                          hand_rect_one_y[i]:hand_rect_one_y[i] + 10]
    for i in range(len(roi)):
        for j in range(len(roi[i])):
            if roi[i][j][0] >= blue_lower[0] and roi[i][j][0] <= blue_upper[0] and roi[i][j][1] >= blue_lower[1] and roi[i][j][1] <= blue_upper[1] and roi[i][j][2] >= blue_lower[2] and roi[i][j][2] <= blue_upper[2]:
                blue_cnt=blue_cnt+1
            if roi[i][j][0] >= green_lower[0] and roi[i][j][0] <= green_upper[0] and roi[i][j][1] >= green_lower[1] and roi[i][j][1] <= green_upper[1] and roi[i][j][2] >= green_lower[2] and roi[i][j][2] <= green_upper[2]:
                green_cnt=green_cnt+1
            if (roi[i][j][0] >= red_lower1[0] and roi[i][j][0] <= red_upper1[0]) and roi[i][j][1] >= red_lower1[1] and roi[i][j][1] <= red_upper1[1] and roi[i][j][2] >= red_lower1[2] and roi[i][j][2] <= red_upper1[2]:
                red1_cnt=red1_cnt+1
            if (roi[i][j][0] >= red_lower2[0] and roi[i][j][0] <= red_upper2[0]) and roi[i][j][1] >= red_lower2[1] and roi[i][j][1] <= red_upper2[1] and roi[i][j][2] >= red_lower2[2] and roi[i][j][2] <= red_upper2[2]:
                red2_cnt=red2_cnt+1
    #creates a histogram for the frame using matrix roi
    #channels:0 (hue) and 1(saturation), no mask (none), histSize: 180 for hue and 256 for saturation
    #ranges 0 to 179 for hue and 0 to 255 for saturation
    #hand_hist = cv2.calcHist([roi], [0, 1], None, [180, 256], [0, 180, 0, 256])
    return maximum(blue_cnt,green_cnt,red1_cnt,red2_cnt)


def draw_rect(frame):
    rows, cols, _ = frame.shape
    global total_rectangle, hand_rect_one_x, hand_rect_one_y, hand_rect_two_x, hand_rect_two_y
    hand_rect_one_x = np.array(
        [4 * rows / 20,4.5 * rows / 20,5 * rows / 20, 5.5 * rows / 20, 6 * rows / 20, 6.5 * rows / 20, 7 * rows / 20], dtype=np.uint32)

    hand_rect_one_y = np.array(
        [10 * cols / 20, 10 * cols / 20, 10 * cols / 20,10 * cols / 20,10 * cols / 20,10 * cols / 20,10 * cols / 20], dtype=np.uint32)

    hand_rect_two_x = hand_rect_one_x + 10
    hand_rect_two_y = hand_rect_one_y + 10

    for i in range(total_rectangle):
        cv2.rectangle(frame, (hand_rect_one_y[i], hand_rect_one_x[i]),
                      (hand_rect_two_y[i], hand_rect_two_x[i]),
                      (0, 255, 0), 1)

    return frame