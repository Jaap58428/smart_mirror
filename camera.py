import numpy as np
import cv2
import zmq
import base64
import imutils


class Capture():
    """
    This class captures camera images. It is a resource,
    and should be constructed using the `with` statement.
    Furthermore, this class is is an iterator, and as such
    one can stream the images read from the camera.
    """

    def __init__(self, camera):
        """
        Creates a capture image from the camera
        """
        self.capture = cv2.VideoCapture(camera)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.capture.release()

    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self.capture.read()
        if ret:
            return frame
        else:
            raise StopIteration


class Socket():
    """
    A Socket is a class that holds a zmq socket.
    When created, no connection is yet established.
    In order to connect to a remote host, use the
    `connect` method.
    """

    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)

    def set_connection(self, addr):
        self.socket.connect(addr)

    def connect(self, addr):
        self.set_connection(addr)
        return Connection(self)

    def send(self, value):
        self.socket.send(value)


class Connection():
    """
    A Connection is a class that represents an
    open socket connection to a host. Values
    can be send trough the connection using the
    `send` method
    """

    def __init__(self, socket):
        self.socket = socket

    def send(self, value):
        self.socket.send(value)


def ktof(val):
    # return val
    # return 1.8 * val + 32
    return (1.8 * ktoc(val) + 32.0)


def ktoc(val):
    return (val - 27315) / 100.0


def display_temperature(img, val_k, loc, color):
    val = ktof(val_k)
    cv2.putText(img, "{0:.1f} degC".format(val), loc, cv2.FONT_HERSHEY_DUPLEX, 0.75, color, 2)
    x, y = loc
    cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
    cv2.line(img, (x, y - 2), (x, y + 2), color, 1)


def rotate_frame(img):
    # get image height, width
    (h, w) = img.shape[:2]
    # calculate the center of the image
    center = (w / 2, h / 2)

    angle90 = 90
    scale = 1.0

    # Perform the counter clockwise rotation holding at the center
    M = cv2.getRotationMatrix2D(center, angle90, scale)
    rotated90 = cv2.warpAffine(img, M, (h, w))
    return rotated90


def editImageData(frame, face_cascade):
    frame = cv2.resize(frame[:, :], (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)

    for (column, row, width, height) in detected_faces:
        cv2.rectangle(
            frame,
            (column, row),
            (column + width, row + height),
            (0, 255, 0),
            2
        )

    # img_norm = cv2.normalize(gray, dst = None, alpha = 0, beta = 65535, norm_type = cv2.NORM_MINMAX)
    gray = np.array(gray, dtype=np.uint24)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray)
    display_temperature(frame, minVal, minLoc, (255, 0, 0))
    display_temperature(frame, maxVal, maxLoc, (0, 0, 255))
    # cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
    # np.right_shift(frame, 8, frame)
    # img = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)

    # https://docs.opencv.org/master/d3/d50/group__imgproc__colormap.html
    # img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)

    #   tmp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #   _,alpha = cv2.threshold(tmp, 180, 255, cv2.THRESH_BINARY)
    #   b, g, r = cv2.split(img)
    #   rgba = [b,g,r, alpha]
    #   dst = cv2.merge(rgba, 4)

    #  img = dst

    return frame


socket = Socket()
connection = socket.connect('tcp://192.168.137.163:5555')
face_cascade = cv2.CascadeClassifier('/home/ghost/Documents/HSL/ISEN/smart_mirror/haarcascade_upperbody.xml')

with Capture(2) as c:
    for frame in c:
        frame = editImageData(frame, face_cascade)
        frame = imutils.rotate_bound(frame, 270)
        encoded, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        connection.send(jpg_as_text)
