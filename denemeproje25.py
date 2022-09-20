import cv2
import time
import os
import datetime
from threading import Thread
from queue import Queue
import numpy as np
import keyboard
renk_index = 0
renkler = { "kirmizi":(0, 0, 255),"sari":(0, 255, 255),"Mavi":(255, 0, 0),"Yesil":(0, 255, 0),"turuncu":(10,128,255),"beyaz":(255,255,255)}
gri = False
kenar=False
y=240
a=255
b=255
c=255
class Camera:
    def __init__(self, mirror=False):
        self.data = None
        self.data1=None
        self.cam = cv2.VideoCapture(0)
        self.WIDTH = 640
        self.HEIGHT = 480
        self.center_x = self.WIDTH / 2
        self.center_y = self.HEIGHT / 2
        self.touched_zoom = False
        self.image_queue = Queue()
        self.video_queue = Queue()
        self.scale = 1
        self.__setup()
        self.recording = False
        self.mirror = mirror
    def __setup(self):
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.WIDTH)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.HEIGHT)
        time.sleep(2)
    def get_location(self, x, y):
        self.center_x = x
        self.center_y = y
        self.touched_zoom = True
    def stream(self):
        def streaming():
            self.ret = True
            while self.ret:
                self.ret, np_image = self.cam.read()
                self.ret, np_image1 = self.cam.read()
                if np_image is None:
                    continue
                if self.mirror:
                    np_image = cv2.flip(np_image, 1)
                    np_image1 = cv2.flip(np_image1, 1)
                if self.touched_zoom:
                    np_image = self.__zoom(np_image, (self.center_x, self.center_y))
                    np_image1 = self.__zoom(np_image1, (self.center_x, self.center_y))
                else:
                    if not self.scale == 1:
                        np_image = self.__zoom(np_image)
                        np_image1 = self.__zoom(np_image1)
                self.data = np_image
                self.data1 = np_image1
                k = cv2.waitKey(1)
                if k == ord('q'):
                    self.release()
                    break
        Thread(target=streaming).start()
    def __zoom(self, img, center=None):
        height, width = img.shape[:2]
        if center is None:
            center_x = int(width / 2)
            center_y = int(height / 2)
            radius_x, radius_y = int(width / 2), int(height / 2)
        else:
            rate = height / width
            center_x, center_y = center
            if center_x < width * (1-rate):
                center_x = width * (1-rate)
            elif center_x > width * rate:
                center_x = width * rate
            if center_y < height * (1-rate):
                center_y = height * (1-rate)
            elif center_y > height * rate:
                center_y = height * rate
            center_x, center_y = int(center_x), int(center_y)
            left_x, right_x = center_x, int(width - center_x)
            up_y, down_y = int(height - center_y), center_y
            radius_x = min(left_x, right_x)
            radius_y = min(up_y, down_y)
        radius_x, radius_y = int(self.scale * radius_x), int(self.scale * radius_y)
        min_x, max_x = center_x - radius_x, center_x + radius_x
        min_y, max_y = center_y - radius_y, center_y + radius_y
        cropped = img[min_y:max_y, min_x:max_x]
        new_cropped = cv2.resize(cropped, (width, height))
        return new_cropped
    def zoom_out(self):
        if self.scale < 1:
            self.scale += 0.1
        if self.scale == 1:
            self.center_x = self.WIDTH
            self.center_y = self.HEIGHT
            self.touched_zoom = False
    def zoom_in(self):
        if self.scale > 0.2:
            self.scale -= 0.1
    def zoom(self, num):
        if num == 0:
            self.zoom_in()
        elif num == 1:
            self.zoom_out()
        elif num == 2:
            self.touch_init()
    def show(self, y=240,renk_index=0,gri=False,kenar=False):
        while True:
            kare_1 = self.data
            kare_2=self.data1
            if gri:
                kare_1 = cv2.cvtColor(kare_1, cv2.COLOR_RGB2GRAY)
                kare_2 = cv2.cvtColor(kare_2, cv2.COLOR_RGB2GRAY)
                kare_1 = cv2.cvtColor(kare_1, cv2.COLOR_GRAY2RGB)
                kare_2 = cv2.cvtColor(kare_2, cv2.COLOR_GRAY2RGB)
            if kenar:
                kare_1 = cv2.Canny(kare_1, 100, 200)
                kare_2 = cv2.Canny(kare_2, 100, 200)
                kare_1 = cv2.cvtColor(kare_1, cv2.COLOR_GRAY2RGB)
                kare_2 = cv2.cvtColor(kare_2, cv2.COLOR_GRAY2RGB)
            if kare_1 is not None or kare_2 is not None:
                a, b, c = list(renkler.items())[renk_index][1]
                cv2.line(kare_1, (0, 240), (680, 240), (a, b, c), 1)  # yatayqqq
                cv2.line(kare_1, (320, 0), (320, 480), (a, b, c), 1)  # dikey
                cv2.line(kare_2, (0, 240), (680, 240), (a, b, c), 1)  # yatay
                cv2.line(kare_2, (0, y), (680, y), (a, b, c), 1)  # yatay
                cv2.line(kare_2, (320, 0), (320, 480), (a, b, c), 1)  # dikey
                horizontalAppendedImg = np.hstack((kare_1, kare_2))
                out = cv2.resize(horizontalAppendedImg, (1600, 880), 2, 2, interpolation=cv2.INTER_CUBIC)
                cv2.namedWindow('image', cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow("image", out)
            key = cv2.waitKey(1)
            if key==ord('r'):
                if renk_index == 5:
                    renk_index = 0
                else:
                    renk_index += 1
            elif key == ord('w'):
                y-=13
            elif key == ord('g'):
                if gri:
                    time.sleep(0.25)
                    gri = False
                else:
                    time.sleep(0.25)
                    gri = True
            elif key == ord('s'):
                y += 13
            elif key == ord('q'):
                    self.release()
                    cv2.destroyAllWindows()
                    break
            elif key == ord('z'):
                    self.zoom_in()
            elif key == ord('x'):
                    self.zoom_out()
            elif key==ord('k'):
                if kenar:
                    kenar = False
                else:
                    kenar = True
                pass
    def release(self):
        self.cam.release()
        cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flag, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.get_location(x, y)
            self.zoom_in()
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.zoom_out()

if __name__ == '__main__':
    cam = Camera(mirror=True)
    cam.stream()
    cam.show()