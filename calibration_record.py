import io
import time
import picamera
from concurrent import futures
import cv2
import numpy as np
import os
from PIL import Image, ImageOps


width = 1280
height = 960
# width = 640
# height = 480

folder = "/home/pi/scripts/im_seq/"
os.system("rm -rf {}".format(folder))
os.system("mkdir -p {}".format(folder))
im_num = 1


stream = io.BytesIO()
camera = picamera.PiCamera()
camera.shutter_speed = 30000
camera.resolution = (width, height)
camera.start_preview()

print("Warming up...")
time.sleep(2)

while True:
    input("Press Enter to continue...")

    camera.capture(stream, format='png')
    filename = folder + str(im_num).zfill(6) + ".png"
    im_num += 1

    image = Image.open(stream)
    # image = ImageOps.grayscale(image)
    image = image.save(filename)

    print("saved", filename)
    stream.seek(0)
