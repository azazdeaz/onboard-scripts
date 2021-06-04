from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
import time

# Create the in-memory stream
stream = BytesIO()
camera = PiCamera()
# width = 640
# height = 480
width = 1280
height = 920
camera.resolution = (width, height)
camera.shutter_speed = 20000
camera.start_preview()
sleep(2)



def pic(n=0):
    t = time.time()
    camera.capture(stream, format='jpeg', use_video_port=False)
    # "Rewind" the stream to the beginning so we can read its content
    stream.seek(0)
    print(time.time() - t)
    image = Image.open(stream)
    print(time.time() - t)
    image.save("im{}.jpeg".format(n))
pic()
pic()
time.sleep(1)
pic()
pic()
pic()
pic()
