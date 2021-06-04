import io
import time
import picamera
import picamera.array
from concurrent import futures
import cv2
import numpy as np
import os
from PIL import Image, ImageOps


# width = 1280
# height = 960
width = 640
height = 480

folder = "/home/pi/scripts/im_seq/"
os.system("rm -rf {}".format(folder))
os.system("mkdir -p {}".format(folder))
im_num = 1

try:
    with picamera.PiCamera(resolution=(width, height), framerate=1) as camera:
        camera.resolution = (width, height)
        camera.framerate = 4
        print("camera", camera)
        # Start a preview and let the camera warm up for 2 seconds
        camera.start_preview()
        time.sleep(8)

        # Note the start time and construct a stream to hold image data
        # temporarily (we could write it directly to connection but in this
        # case we want to find out the size of each capture first to keep
        # our protocol simple)
        start = time.time()
        with picamera.array.PiRGBArray(camera) as stream:
            for foo in camera.capture_continuous(stream, 'bgr', use_video_port=True):
                # Write the length of the capture to the stream and flush to
                # ensure it actually gets sent
                # connection.write(struct.pack('<L', stream.tell()))
                # connection.flush()
                # Rewind the stream and send the image data over the wire
                
                # message = things_pb2.Image(width=width, height=height, image_data=message)

                filename = folder + str(im_num).zfill(6) + ".png"
                im_num += 1

                stream.seek(0)
                gray = cv2.cvtColor(stream.array, cv2.COLOR_BGR2GRAY)
                cv2.imwrite(filename, gray)

                # stream.seek(0)
                # message = stream.read()
                # f = open(filename, 'wb')
                # f.write(message)
                # f.close()

                # image = Image.open(stream)
                # image = ImageOps.grayscale(image)
                # image = image.save(filename)

                # data = np.fromstring(stream.read(), dtype=np.uint8)
                # # "Decode" the image from the array, preserving colour
                # image = cv2.imdecode(data, 1)
                # # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # cv2.imwrite(filename, image)
                print("saved", filename)


                # Reset the stream for the next capture
                stream.seek(0)
    # Write a length of zero to the stream to signal we're done
    # connection.write(struct.pack('<L', 0))
except KeyboardInterrupt:
    print('interrupted!')
finally:
    print('ended')