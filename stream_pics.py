import io
import time
import picamera
import zmq
from io import BytesIO
from picamera import PiCamera




port = "5560"
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.setsockopt(zmq.CONFLATE, 1)
socket.bind("tcp://0.0.0.0:%s" % port)

width = 1280
height = 960
# width = 640
# height = 480

# Create the in-memory stream
stream = BytesIO()
camera = PiCamera()
camera.resolution = (width, height)
# camera.shutter_speed = 20000
camera.start_preview()
time.sleep(2)



class FrameNum:
    num = 0

    @classmethod
    def next(cls):
        cls.num += 1
        return cls.num

while True:
    print("capturing...")
    camera.capture(stream, format='rgb', use_video_port=True)
    stream.seek(0)
    message = stream.read()
    socket.send(message)
    stream.seek(0)
    print("image sent {}".format(FrameNum.next()))
    print("exposure_speed", camera.exposure_speed)
    # time.sleep(1)

