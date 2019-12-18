import socket
import numpy as np
import cv2


def get_stream():
    # capture from the LAST camera in the system
    # presumably, if the system has a built-in webcam it will be the first
    for i in reversed(range(10)):
        cv2_cap = cv2.VideoCapture(i)
        if cv2_cap.isOpened():
            break

    if not cv2_cap.isOpened():
        print("Camera not found!")
        exit(1)

    return cv2_cap


if __name__ == '__main__':
    width = 160
    height = 120
    channels = 1
    packets = 20
    byte_size = width * height * channels / packets

    UDP_IP = '127.0.0.1'
    UDP_PORT = 999
    cap = get_stream()

    while True:
        cap.grab()
        read_flag, frame = cap.retrieve(0)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        d = frame.flatten()
        s = d.tostring()
        for i in range(20):
            sock.sendto(s[i * byte_size:(i + 1) * byte_size], (UDP_IP, UDP_PORT))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
