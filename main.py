import numpy as np
import cv2
import os
import time
import fix_paper
import get_colors
import keyboard
from tkinter import *
import tkinter
import PIL.Image, PIL.ImageTk
from collections import deque
import math



class App:
    def __init__(self, window, window_title,width,height, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width = width, height = height)
        self.canvas.pack()

        # Button that lets the user take a snapshot
        #self.btn_snapshot = tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
        #self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        # creating a menu instance
        menu = Menu(self.window)
        self.window.config(menu=menu)
        file = Menu(menu)
        file.add_command(label="Exit",command=self.my_exit)
        self.btn_snapshot = tkinter.Button(window, text="Snapshot", width=10, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        # added "file" to our menu
        menu.add_cascade(label="File", menu=file)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
    def my_exit(self):
        os._exit(1)
    def snapshot(self):
        cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(wraped_white, cv2.COLOR_RGB2BGR))

    def my_update(self,frame):
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        self.image_on_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.window.update()

# construct the argument parse and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-i", "--image", help = "path to the image")
#args = vars(ap.parse_args())
# load the image
def get_shadow_min(image,x0,x1,y0,y1,lower,upper):
    cropped_image = image[y0:y1, x0:x1]
    tmp_img = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    output = cv2.inRange(tmp_img, lower, upper)
    re, mask_shadow = cv2.threshold(cropped_image, 80, 255, cv2.THRESH_BINARY_INV)
    closing = mask_shadow - output
    kernel = np.ones((5, 5), np.uint8)
    img_dilation = cv2.erode(closing, kernel, iterations=1)
    closing = cv2.morphologyEx(img_dilation, cv2.MORPH_CLOSE, kernel)
    img_dilation = cv2.dilate(closing, kernel, iterations=1)
    closing = cv2.morphologyEx(img_dilation, cv2.MORPH_CLOSE, kernel)
    shadow_contours, im2 = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    y = 0
    topmost_shadow = (0, 0)
    for shape in shadow_contours:
        tmp = tuple(shape[shape[:, :, 1].argmax()][0])
        if tmp[1] > y:
            y = tmp[1]
            topmost_shadow = tuple(shape[shape[:, :, 1].argmax()][0])
    return topmost_shadow

def get_color_min_point(image,lower,upper):
    tmp_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    output = cv2.inRange(tmp_img, lower, upper)
    # Taking a matrix of size 5 as the kernel (for erosion and dilation)
    kernel = np.ones((5, 5), np.uint8)
    # The first parameter is the original image,
    # kernel is the matrix with which image is
    # convolved and third parameter is the number
    # of iterations, which will determine how much
    # you want to erode/dilate a given image.
    img_dilation = cv2.dilate(output, kernel, iterations=1)
    kernel = np.ones((10, 10), np.uint8)
    closing = cv2.morphologyEx(img_dilation, cv2.MORPH_CLOSE, kernel)
    contours, im2 = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    y = 0
    topmost = (100, 100)
    for shape in contours:
        tmp = tuple(shape[shape[:, :, 1].argmax()][0])
        if tmp[1] > y:
            y = tmp[1]
            topmost = tuple(shape[shape[:, :, 1].argmax()][0])
    return topmost,closing


## gesture_index low_pass filter
white_pic = cv2.imread('white_pic.png')
gesture_filter_size = 5
gesture_matching_filter_draw = deque([0.0, 0.0, 0.0, 0.0, 0.0], gesture_filter_size)
gesture_matching_filter_stop = deque([0.0, 0.0, 0.0, 0.0, 0.0], gesture_filter_size)
gesture_index_thres = 3
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
cyan = (180, 180, 0)
white = (255, 255, 255)
trans = (180, 188, 17)
color = cyan
colors = [color]
pol_x = []
pol_y = []
func_colors = [color]
## background segmentation
kernel_size = 5
kernel1 = np.ones((kernel_size, kernel_size), np.float32) / kernel_size / kernel_size
cap = cv2.VideoCapture(1)
count = 1
points = []
do_once = 0
func = 0
draw_circle = 0
draw_rec = 0
draw_rec_cords = []
draw_circle_cords = []
circle_colors=[]
rec_colors=[]
while cap.isOpened():
    ret, frame = cap.read()
    frame=get_colors.draw_rect(frame)
    cv2.imshow("frame",frame)
    if cv2.waitKey(1) & 0xFF == ord('z'):
        lower,upper=get_colors.pen_color(frame)
        cv2.destroyAllWindows()
        break


while cap.isOpened():
    ret, image = cap.read()
    image_original = image
    image=cv2.resize(image,(600,500))
    white_pic_org=cv2.resize(white_pic,(600,500))
    blue = (0, 0, 255)
    topmost,closing=get_color_min_point(image,lower,upper)
    tmp_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(tmp_img, lower, upper)
    mask=255-mask
    res = cv2.bitwise_and(image, image, mask=mask)  # -- Contains pixels having the gray color--
    res[mask==0] = [255,255,255]
    #################### here starts the cropping and detecting shadow##################
    x0=(topmost[0]-70)
    x1=(topmost[0]+70)
    y0=(topmost[1]-70)
    y1=(topmost[1]+70)
    if x0<0:
        x0=0
    if x1>600:
        x1=600
    if y0<0:
        y0=0
    if y1>500:
        y1=500
    ############## choosing the 4 points of the paper###################################
    if do_once==0:
        pressed_key = cv2.waitKey(1)
        if pressed_key & 0xFF == ord('c'):
            points.append(topmost)
            print("point "+str(count)+" choosen")
            count=count+1
        if count ==5:
            tmp_point=points[3]
            points[3]=points[2]
            points[2]=tmp_point
            do_once=1
            warped, M = fix_paper.fix(image, points)
            wraped_white, M = fix_paper.fix(white_pic_org, points)
            dims = warped.shape
            height = int(dims[0])
            width = int(dims[1])
            gui = App(tkinter.Toplevel(), "hg", width, height)

        tmp_image=image
        cv2.circle(tmp_image, topmost, 10, blue, 3)
        cv2.imshow("tmp_image", tmp_image)
        traj = np.array([], np.uint16)
        traj = np.append(traj, topmost)
        dist_pts = 0
        dist_records = [dist_pts]
        func_points = np.array([], np.uint16)
        func_points = np.append(func_points, topmost)
        dist_records_func=[dist_pts]

        ## finger cursor position low_pass filter
        low_filter_size = 5
        low_filter = deque([topmost, topmost, topmost, topmost, topmost],
                           low_filter_size)  # filter size is 5
        if do_once == 1:
            cv2.destroyAllWindows()

    if do_once == 1:

        topmost_shadow = get_shadow_min(res, x0, x1, y0, y1,lower,upper)
        cv2.circle(image, topmost, 10, red, 3)
        cv2.circle(image, (topmost_shadow[0] + x0, topmost_shadow[1] + y0), 10, blue, 3)
        cv2.circle(white_pic_org, topmost, 10, blue, 3)
        cv2.circle(white_pic_org, (topmost_shadow[0] + x0, topmost_shadow[1] + y0), 10, red, 3)
        #########################initial position of finger cursor#########################
        try:
            low_filter.append(topmost)
            sum_x = 0
            sum_y = 0
            for i in low_filter:
                sum_x += i[0]
                sum_y += i[1]
            topmost = (sum_x // low_filter_size, sum_y // low_filter_size)
            if func==0:
                traj = np.append(traj, topmost)
                dist_records.append(dist_pts)
                draw=0
                if topmost_shadow[0]+x0 <= topmost[0]+15 and topmost_shadow[0]+x0 >= topmost[0]-15:
                    if topmost_shadow[1] + y0 <= topmost[1] + 15 and topmost_shadow[1]+y0 >= topmost[1]-15:
                        colors.append(color)
                        draw=1
                if(draw==0):
                    colors.append(trans)
            if func ==2:
                func_points=np.append(func_points, topmost)
                dist_records_func.append(dist_pts)
                draw=0
                if topmost_shadow[0]+x0 <= topmost[0]+15 and topmost_shadow[0]+x0 >= topmost[0]-15:
                    if topmost_shadow[1] + y0 <= topmost[1] + 15 and topmost_shadow[1] + y0 >= topmost[1] - 15:
                        func_colors.append(color)
                        draw = 1
                if draw == 0:
                    func_colors.append(trans)
            # update cursor position
        except:
            print('error')
            pass

        for i in range(1, len(dist_records)):
            # try:
            thickness = 4
            if colors[i] != trans:
                cv2.line(image, (traj[i * 2 - 2], traj[i * 2 - 1]), (traj[i * 2], traj[i * 2 + 1]), colors[i],thickness)
                cv2.line(white_pic_org, (traj[i * 2 - 2], traj[i * 2 - 1]), (traj[i * 2], traj[i * 2 + 1]), colors[i],thickness)
        for i in range(2,len(dist_records_func)):
            if func_colors[i] != trans:
                cv2.line(image, (func_points[i * 2 - 2], func_points[i * 2 - 1]), (func_points[i * 2], func_points[i * 2 + 1]), func_colors[i],thickness)
                cv2.line(white_pic_org, (func_points[i * 2 - 2], func_points[i * 2 - 1]), (func_points[i * 2], func_points[i * 2 + 1]), func_colors[i],thickness)
        warped,M = fix_paper.fix(image, points)
        wraped_white,M=fix_paper.fix(white_pic_org, points)
        for i in range(int(len(draw_rec_cords) / 2)):
            cv2.rectangle(wraped_white, draw_rec_cords[2 * i], draw_rec_cords[2 * i + 1], rec_colors[i], 3)
        for j in range(int(len(draw_circle_cords) / 2)):
            cv2.circle(wraped_white, draw_circle_cords[2 * j], draw_circle_cords[2 * j + 1][0], circle_colors[j], 3)
        cv2.rectangle(wraped_white, (0, 0), (20, int(height/6)), (0, 255, 0), -1)
        cv2.rectangle(wraped_white, (0, int(height/6)), (20, int(2*height/6)), (255, 0, 0), -1)
        cv2.rectangle(wraped_white, (0, int(2*height/6)), (20, int(3*height/6)), (0, 0, 255), -1)
        cv2.rectangle(wraped_white, (0, int(3*height/6)), (20, int(4*height/6)), (180, 180, 0), -1)
        cv2.rectangle(wraped_white, (0, int(4*height/6)), (20, int(5*height/6)), (0, 0, 0), 2)
        ##########drawing the fucntion rectangle#####################################
        cv2.rectangle(wraped_white, (0, int(5 * height / 6)), (20, height), (0, 0, 0), 2)
        cv2.putText(wraped_white,"F",(0,int((5*height/6)+(height/12)+12)),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),1)
        #############################################################################
        y_coor=M[0][0]*topmost[0]+M[0][1]*topmost[1] +M[0][2]*1
        x_coor = M[1][0] * topmost[0] + M[1][1] * topmost[1] + M[1][2] * 1
        ti=M[2][0] * topmost[0] + M[2][1] * topmost[1] + M[2][2] * 1
        x_coor=x_coor/ti
        y_coor=y_coor/ti
        if x_coor > width-20 and x_coor < width:
            if y_coor > 0 and y_coor < int(height/6):
                color = green
            if y_coor > int(height/6) and y_coor < int(2*height/6):
                color = red
            if y_coor > int(2*height/6) and y_coor < int(3*height/6):
                color = blue
            if y_coor > int(3*height/6) and y_coor < int(4*height/6):
                color = cyan
            if y_coor > int(4*height/6) and y_coor < int(5*height/6):
                color = white
            if y_coor > int(5*height/6) and y_coor < height and func==0:
                func=1
            if y_coor > int(5*height/6) and y_coor < height and func==2:
                func=3
        else:
            if func==1:
                func=2
            if func == 3:
                xpoints = []
                ypoints = []
                starting_point = 0
                for i in range(2, len(dist_records_func)):
                    if func_colors[i] != trans:
                        if starting_point == 0:
                            xpoints.append(0)
                            ypoints.append(0)
                            startingx = func_points[i * 2 - 2]
                            startingy = func_points[i * 2 - 1]
                            endx = func_points[i * 2 - 2]
                            starting_point = 1
                        else:
                            xpoints.append(startingx - func_points[i * 2 - 2])
                            if endx > func_points[i * 2 - 2]:
                                endx = func_points[i * 2 - 2]
                            ypoints.append(startingy - func_points[i * 2 - 1])
                if xpoints and ypoints:
                    coefs = np.polyfit(xpoints, ypoints, 4)
                ########################################################
                    for i in range(startingx - endx):
                        y = int(coefs[0] * (i ** 4) + coefs[1] * (i ** 3) + coefs[2] * (i ** 2) + coefs[3] * i + coefs[4])
                        pol_x.append(startingx - i)
                        pol_y.append(startingy - y)
                    for i in range(len(pol_x)):
                        pt = (pol_x[i], pol_y[i])
                        if i == 0:
                            colors.append(trans)
                        else:
                            colors.append(red)
                        traj = np.append(traj, pt)
                        dist_records.append(dist_pts)
                    ########################################################
                    func_points = np.array([], np.uint16)
                    pol_x=[]
                    pol_y=[]
                    func_points = np.append(func_points, (0,0))
                    dist_records_func = [dist_pts]
                func = 0

        #######func==1 means that we entered the rectangle the first time
        #######func==2 means that we exited the rectangle for the first time
        #######func==3 means that we entered the rectangle for the second time (draw the func)
        gui.my_update(wraped_white)
        cv2.imshow('frame', image)
        if keyboard.is_pressed('q'):
            break
        if keyboard.is_pressed('l'):
            traj = np.array([], np.uint16)
            traj = np.append(traj, topmost)
            dist_pts = 0
            dist_records = [dist_pts]
            func_points = np.array([], np.uint16)
            func_points = np.append(func_points, topmost)
            dist_records_func = [dist_pts]
            color = cyan
            colors = [color]
            pol_x = []
            pol_y = []
            draw_rec_cords=[]
            draw_circle_cords=[]
            func_colors = [color]
            circle_colors=[]
            rec_colors=[]

        if keyboard.is_pressed('r') or keyboard.is_pressed('a'):
            if draw_rec == 0:
                draw_rec = 1
                corner1 = topmost
            elif draw_rec == 1:
                draw_rec = 0
                corner2 = topmost
                y_coor = M[0][0] * corner1[0] + M[0][1] * corner1[1] + M[0][2] * 1
                x_coor = M[1][0] * corner1[0] + M[1][1] * corner1[1] + M[1][2] * 1
                ti = M[2][0] * corner1[0] + M[2][1] * corner1[1] + M[2][2] * 1
                x_coor = x_coor / ti
                x_coor=width - x_coor
                y_coor = y_coor / ti
                x_center=x_coor
                y_center=y_coor
                if keyboard.is_pressed('r'):
                    draw_rec_cords.append((int(x_coor), int(y_coor)))
                    rec_colors.append(color)
                else:
                    draw_circle_cords.append((int(x_center), int(y_center)))
                    circle_colors.append(color)
                y_coor = M[0][0] * corner2[0] + M[0][1] * corner2[1] + M[0][2] * 1
                x_coor = M[1][0] * corner2[0] + M[1][1] * corner2[1] + M[1][2] * 1
                ti = M[2][0] * corner2[0] + M[2][1] * corner2[1] + M[2][2] * 1
                x_coor = x_coor / ti
                x_coor = width - x_coor
                y_coor = y_coor / ti
                if keyboard.is_pressed('r'):
                    draw_rec_cords.append((int(x_coor), int(y_coor)))
                    rec_colors.append(color)
                else:
                    dist = math.sqrt((x_center - x_coor)**2 + (y_center - y_coor)**2)
                    draw_circle_cords.append((int(dist), int(0)))
                    circle_colors.append(color)
            while keyboard.is_pressed('r') or keyboard.is_pressed('a'):
                continue
            print(draw_rec_cords)
            print(corner1)
    cv2.waitKey(1)
