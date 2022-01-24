import datetime
import os

from camera import Camera
import cv2


class SimulatorCamera(Camera):
    def __init__(self):
        super().__init__()
        self.images_directory = 'images/'
        self.connected = True

    def capture_image(self):
        frame = cv2.imread('galaxy.png')
        image_name = 'image_' + str(datetime.datetime.now().date()) + '_' + str(
            datetime.datetime.now().time()) + '.png'
        print(image_name)
        target = os.path.join(self.images_directory, image_name)
        cv2.imwrite(target, frame)
        return target
