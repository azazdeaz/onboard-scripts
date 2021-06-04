import time
import zmq
import msgpack
from gpiozero import LED, Robot
import numpy as np

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.CONFLATE, 1)
# socket.bind("tcp://*:5555")
socket.connect("tcp://192.168.50.111:5567")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

EEP = 26
IN1 = 5
IN2 = 6
IN3 = 13
IN4 = 19 

eep = LED(EEP)
eep.on()

robot = Robot(left=(IN2, IN1), right=(IN3, IN4))

prev_speed = (0,0)

# robot.value = (1,1)
# time.sleep(1)
# robot.stop()

while True:
    message = socket.recv_string()
    # message = msgpack.unpackb(message)
    # left, right = message["left"], message["right"]
    values = list(map(float,message.split(",")))
    left, right = values[:2]
    # robot.left(message["left"])
    # robot.right(message["right"])

    # starting motors
    # if (prev_speed[0] == 0 and prev_speed[1] == 0) and (left != 0 or right != 0):
    #     kick_scale = 0.8
    #     left_kick = 0 if left == 0 else np.sign(left) * kick_scale
    #     right_kick = 0 if right == 0 else np.sign(right) * kick_scale
    #     robot.value = (left_kick, right_kick)
    #     time.sleep(0.1)

    robot.value = (left, right)
    prev_speed = (left,right)
    if len(values) > 2 and values[2] > 0:
        time.sleep(values[2])
        robot.stop()
    print("Received request: %s" % message)