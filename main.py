#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import random
import socket
import signal
from enum import Enum
import os
import colorsys
import json
from PIL import Image
from PIL import ImageTk
from uvctypes import *
import time
import cv2
import numpy as np
from pathlib import Path  # python3 only
from dotenv import load_dotenv
import threading
import zmq
import base64



# SETUP SETTINGS
env_path = Path('/home/pi/rocket') / '.env'
load_dotenv(dotenv_path=env_path)
config_path = os.getenv("CONFIG_FILE")
with open('/home/ghost/smart_mirror/rocket/' + config_path, "r") as f:
    settings = json.load(f)

settings["run_ambient_sensor_thread"] = True
settings["admin_camera_feed"] = True

if os.name == 'nt':
    from sensor import MotionSenseMock as MotionSense
    from sensor import TempSenseMock as TempSense
    from sensor import BoardMock as Board
else:
    from sensor import Board
    from sensor import TempSense
    from sensor import MotionSense


LABEL_STRINGS = {
    "temp": "Ambient temperature",
    "hum": "Ambient humidity",
    "last_update": "LAST UPDATE"
}


ambient_sensor_data = {
    "temp": 0,
    "hum": 0,
    "last_update": time.time()
}


def ktoc(val):
    return (val - 27315) / 100.0


def display_temperature(img, val_k, loc, color):
    val = ktoc(val_k)
    cv2.putText(img, "{0:.1f} degC".format(val), loc, cv2.FONT_HERSHEY_DUPLEX, 0.75, color, 2)
    x, y = loc
    cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
    cv2.line(img, (x, y - 2), (x, y + 2), color, 1)


class Color(Enum):
    BACKGROUND = "#000"
    FONT_COLOR = "#FFF"


def get_main_window():
    window = tk.Tk()
    window.title("Smart Mirror GUI")
    window.configure(
        bg=Color.BACKGROUND.value,
        cursor="none"
    )

    window.focus_set()
    window.attributes("-fullscreen", True)
    window.minsize(150, 100)

    return window


def get_ip_address():
    ip_address = "UNKNOWN"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception as e:
        print(e)
    finally:
        s.close()
        return ip_address


def get_heat_image_panel(parent):
    heat_image_panel = tk.Label(
        parent,
        border=0,
        bg=Color.BACKGROUND.value,
        # bg = "#ffffff",
        width=640,
        height=480,
    )

    # heat_image_panel.pack(expand="yes", side=tk.TOP, anchor=tk.W, fill="both")
    heat_image_panel.pack(side=tk.TOP, anchor=tk.W)
    # heat_image_panel.pack()
    return heat_image_panel


def generate_data_labels(parent, data_set):
    string_pointers = {}
    for attr, val in data_set.items():
        string_pointers[attr] = tk.StringVar()
        attr_string = LABEL_STRINGS[attr]
        string_pointers[attr].set('{0}: {1}'.format(attr_string, str(val)))
        new_label = tk.Label(parent)
        new_label.configure(
            textvariable=string_pointers[attr],
            bg=Color.BACKGROUND.value,
            fg=Color.FONT_COLOR.value,
            width=10,
            anchor=tk.W,
            font=("default", 20)
        )
        if settings["run_ambient_sensor_thread"]:
            new_label.configure(
                font=("default", 0)
            )
        new_label.pack()
    return parent, string_pointers


def get_data_panel(parent, data_set):
    data_panel = tk.Frame(parent)
    data_panel.configure(
        bg=Color.BACKGROUND.value,
        height=10,
    )

    updated_data_panel, string_pointers = generate_data_labels(data_panel, data_set)

    updated_data_panel.pack(side=tk.TOP, anchor=tk.E)
    return updated_data_panel, string_pointers


def read_ambient_temp_sensor(tmpsensor):
    global ambient_sensor_data    
    current = time.time()

    delay = settings["ambient_temp_delay"]
    while(True):
        last_update = ambient_sensor_data["last_update"]
        
        if (time.time() - last_update) < delay:
            continue

   
        (hum, temp) = tmpsensor.sense()
        hum = round(hum, 2)
        temp = round(temp, 2)

        ambient_sensor_data["temp"] = temp
        
        if settings["use_humidity"]:
            ambient_sensor_data["hum"] = hum

        ambient_sensor_data["last_update"] = time.time()
        

def update_ambient_temp_data(tmpsensor):
    update_temp_thread = threading.Thread(
        target=read_ambient_temp_sensor,
        args=(tmpsensor,),
        daemon=True  # kills thread once main dies
    )
    update_temp_thread.start()


def update_string_pointers(string_pointers, data_set):
    for attr, pointer in string_pointers.items():
        attr_string = LABEL_STRINGS[attr]
        pointer.set('{0}: {1}'.format(
            attr_string,
            str(data_set[attr]))
        )


def kill_gui(gui_elements):
    # heat image panel, requires place_remove()
    gui_elements[0].pack_forget()

    # data & debug panel require pack_forget()
    gui_elements[1].pack_forget()
    if settings["display_debug_panel"]:
        gui_elements[2].pack_forget()


def show_gui(gui_elements):
    # heat image panel, requires place_remove()
    gui_elements[0].pack(side=tk.TOP, anchor=tk.W)

    # data & debug panel require pack_forget()
    gui_elements[1].pack(side=tk.TOP, anchor=tk.E)
    if settings["display_debug_panel"]:
        gui_elements[2].pack(side=tk.BOTTOM, anchor=tk.W)


def movement(motion_sensor):
    motion = motion_sensor.sense()
    return motion


def generate_debug_labels(parent):
    string_pointers = {}
    if settings["display_sleep_timer"]:
        string_pointers["display_sleep_timer"] = tk.StringVar()
        string_pointers["display_sleep_timer"].set("Timer: 0")
        timer_label = tk.Label(parent)
        timer_label.configure(
            textvariable=string_pointers["display_sleep_timer"],
            bg=Color.BACKGROUND.value,
            fg=Color.FONT_COLOR.value,
            anchor=tk.W,
            width=40,
            font=("default", 10)
        )
        timer_label.pack()
    if settings["display_host_ip"]:
        ip = get_ip_address()
        string_pointers["display_host_ip"] = tk.StringVar()
        string_pointers["display_host_ip"].set("Mirror network address: {0}".format(ip))
        ip_label = tk.Label(parent)
        ip_label.configure(
            textvariable=string_pointers["display_host_ip"],
            bg=Color.BACKGROUND.value,
            fg=Color.FONT_COLOR.value,
            anchor=tk.W,
            width=40,
            font=("default", 10)
        )
        ip_label.pack()

    return parent, string_pointers


def get_debug_panel(parent):
    debug_panel = tk.Frame(parent)
    debug_panel.configure(
        bg=Color.BACKGROUND.value,
    )
    updated_debug_panel, string_pointers = generate_debug_labels(debug_panel)
    updated_debug_panel.pack(side=tk.BOTTOM, anchor=tk.W)
    return updated_debug_panel, string_pointers


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


def editImageData(frame):
    frame = rotate_frame(frame)
    # Arguments are in the (x, y) form here
    # frame = cv2.resize(frame[:, :], (1100, 1800))


    # @NOTE: As of this moment (16-12-2019), we hit an assertion with the {min|max}.
    # This is a cv2 error.
    #minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frame)
   # cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
   # np.right_shift(frame, 8, frame)

    # frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)

    # https://docs.opencv.org/master/d3/d50/group__imgproc__colormap.html
    #frame = cv2.applyColorMap(frame, cv2.COLORMAP_RAINBOW)

    # display_temperature(img, minVal, minLoc, (255, 255, 255))
    # display_temperature(img, maxVal, maxLoc, (255, 255, 255))

    return frame


def convertNumpyToGuiElement(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return ImageTk.PhotoImage(Image.fromarray(frame))


def receive_frame():



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


# ONLY USE THIS AS A THREAD
def start_screen_grab_thread(cv2_stream):

    def write_screen_file(cv2_stream):
        delay = 1
        last_screen_grab_update = 0
        while True:
            current = time.time()
            if (current - last_screen_grab_update) < delay:
                continue

            frame = footage_socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)

            image = editImageData(source)

            if read_flag:
                path = '/home/ghost/smart_mirror/static/screen_grab.jpeg'
                cv2.imwrite(path, image)
                read_flag = False
                print("image written")

            last_screen_grab_update = current

    screen_grab_thread = threading.Thread(
        target=write_screen_file,
        args=(cv2_stream, ),
        daemon=True  # kills thread once main dies
    )
    screen_grab_thread.start()

    return screen_grab_thread




if __name__ == '__main__':
    with Board() as _, MotionSense(7) as motion_sensor, TempSense(17) as ambient_temp_sensor:
        # Open thermal camera stream
        context = zmq.Context()
        footage_socket = context.socket(zmq.SUB)
        footage_socket.bind('tcp://*:5555')
        footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

        # SETUP AMBIENT TEMP SENSOR
        last_ambient_temp_req_time = 0
        if settings["run_ambient_sensor_thread"]:
            update_ambient_temp_data(ambient_temp_sensor)

        # START SCREEN GRAB THREAD
        if settings["admin_camera_feed"]:
            start_screen_grab_thread(footage_socket)


        # GET ROOT WINDOW
        window = get_main_window()

        # SETUP VIDEO STREAM AND DATA PANELS
        heat_image_panel = get_heat_image_panel(window)
        data_panel, data_string_pointers = get_data_panel(window, ambient_sensor_data)

        panels = [
            heat_image_panel,
            data_panel
        ]

        # SETUP DEBUG PANEL
        if settings["display_debug_panel"]:
            debug_panel, debug_string_pointers = get_debug_panel(window)
            panels.append(debug_panel)

        is_gui_shown = True

        # At boot set start time
        start_time = time.time()

        while True:
            # If timer hasn't passed into sleep: ACTIVE
            time_passed = time.time() - start_time
            if time_passed < settings["sleep_timeout_sec"]:

                # GET IMAGE FROM STREAM
                frame = footage_socket.recv_string()
                img = base64.b64decode(frame)
                npimg = np.fromstring(img, dtype=np.uint8)
                source = cv2.imdecode(npimg, 1)

                # Update heat image panel
                img = editImageData(source)
                img = convertNumpyToGuiElement(img)
                heat_image_panel.configure(
                   image = img,
                )
                heat_image_panel.image = img

                update_string_pointers(data_string_pointers, ambient_sensor_data)
                # Update timer
                if settings["display_debug_panel"] and settings["display_sleep_timer"]:
                    time_str = round(time_passed, 1)
                    timer_str = "Timer: {0} ({1})".format(str(time_str), settings["sleep_timeout_sec"])
                    debug_string_pointers["display_sleep_timer"].set(timer_str)

                if movement(motion_sensor):
                    start_time = time.time()

            # Else fall into PASSIVE, check for movement
            else:
                kill_gui(panels) if is_gui_shown else False
                # Once movement is detected, show GUI and reset timer
                if movement(motion_sensor):
                    show_gui(panels)
                    start_time = time.time()
            window.update_idletasks()
            window.update()

            # FPS = how many frames fit in one seconds, so 1 sec / FPS to sleep
            time.sleep((1 / settings.get("screen_max_frame_rate", 1)))
    cv2_stream.release()
    cv2.destroyAllWindows()
