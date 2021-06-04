import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from concurrent import futures
import cv2
import numpy as np
import os
from PIL import Image, ImageOps
import keyboard

PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
<button onclick="fetch('capture')">Capture</button> 
</body>
</html>
"""

class FrameNum:
    num = 0
    @classmethod
    def next(cls):
        cls.num += 1
        return cls.num

folder = "/home/pi/scripts/im_seq/"
os.system("rm -rf {}".format(folder))
os.system("mkdir -p {}".format(folder))
stream = io.BytesIO()
# resolution = "1280x960"
# resolution = "1296x972"
resolution = "640x480"
# resolution = "2592x1944"
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/capture':
            camera.capture(stream, format='png')
            filename = folder + str(FrameNum.next()).zfill(6) + ".png"

            image = Image.open(stream)
            # image = ImageOps.grayscale(image)
            image = image.save(filename)
            stream.seek(0)

            content = "saved {}".format(filename)
            print(content)

            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution=resolution, framerate=8) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    camera.shutter_speed = 30000

    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        print("listening on {0[0]}:{0[1]}".format(server.server_address))
        server.serve_forever()
            
    finally:
        camera.stop_recording()