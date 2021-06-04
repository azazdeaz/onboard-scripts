import time
import zmq
import msgpack
from gpiozero import LED, Robot
import io
import picamera
import numpy as np

context = zmq.Context()

sock_cmd = context.socket(zmq.SUB)
sock_cmd.setsockopt(zmq.CONFLATE, 1)
sock_cmd.connect("tcp://192.168.50.111:5567")
sock_cmd.setsockopt_string(zmq.SUBSCRIBE, "")

port = "5560"
sock_img = context.socket(zmq.PUB)
sock_img.setsockopt(zmq.CONFLATE, 1)
sock_img.bind("tcp://0.0.0.0:%s" % port)


stream = io.BytesIO()
camera = picamera.PiCamera()
# width = 1280
# height = 960
width = 640
height = 480
camera.resolution = (width, height)
camera.start_preview()
print("warming up camera...")
time.sleep(2)
print("ready")

last_image_sent_at = 0
def is_time_to_send_a_new_image():
    return time.time() - last_image_sent_at > 60

def send_image(n=0):
    camera.capture(stream, format='jpeg', use_video_port=True)
    stream.seek(0)
    message = stream.read()
    sock_img.send(message)
    print("image sent")
    last_image_sent_at = time.time()

    # Reset the stream for the next capture
    stream.seek(0)

EEP = 26
IN1 = 5
IN2 = 6
IN3 = 13
IN4 = 19 

eep = LED(EEP)
eep.on()

robot = Robot(left=(IN2, IN1), right=(IN3, IN4))

send_image()


while True:
    message = sock_cmd.recv_string()
    # message = msgpack.unpackb(message)
    # left, right = message["left"], message["right"]
    values = list(map(float,message.split(",")))
    left, right = values[:2]
    # robot.left(message["left"])
    # robot.right(message["right"])
    robot.value = (left, right)
    if len(values) > 2:
        robot.value = (np.sign(left), np.sign(right))
        time.sleep(0.01)
        robot.value = (left, right)
        time.sleep(values[2])
        robot.stop()
        send_image()
    elif is_time_to_send_a_new_image():
        print("auto send image")
        send_image()
    print("Received request: %s" % message)