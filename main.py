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

# SETUP SETTINGS
env_path = Path('/home/pi/rocket') / '.env'
load_dotenv(dotenv_path=env_path)
config_path = os.getenv("CONFIG_FILE")
with open('/home/ghost/smart_mirror/rocket/' + config_path, "r") as f:
    settings = json.load(f)

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
}


def ktof(val):
    return (1.8 * ktoc(val) + 32.0)


def ktoc(val):
    return (val - 27315) / 100.0


def applyColorScheme(img, color_scheme):
    color_scheme = "BLUE_RED" if color_scheme is None else False
    COLOR_PALETS = {
        "BLUE_RED": (120, 180),  # blue to red
        "RAINBOW": (0, 180),  # full spectrum
        "TOXIC": (30, 60)  # yellow to green
    }

    for column in img:
        for (i, pixel) in enumerate(column):
            # gives between 0 and 255
            temp_ratio = pixel.split()[0] / 255.0  # or 0 or 1, equal values

            low_end, high_end = COLOR_PALETS[color_scheme]
            hue = low_end + (temp_ratio * (high_end - low_end))

            r, g, b = colorsys.hls_to_rgb(hue, 255, 255)
            column[i] = " ".join([r, g, b])

    return img


def display_temperature(img, val_k, loc, color):
    val = ktoc(val_k)
    cv2.putText(img, "{0:.1f} degC".format(val), loc, cv2.FONT_HERSHEY_DUPLEX, 0.75, color, 2)
    x, y = loc
    cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
    cv2.line(img, (x, y - 2), (x, y + 2), color, 1)


# class SignalHandler():
#     def __init__(self, ctx, uvc, device, stream):
#         self.uvc = uvc
#         self.device = device
#         self.stream = stream
#
#         signal.signal(signal.SIGINT, self.exitgracefully)
#         signal.signal(signal.SIGTERM, self.exitgracefully)
#
#     def exitgracefully(self, thing1, thing2):
#         print("[*] CALLED EXITGRACEFULLY [*]")
#         print("[*] THING1: {} [*]".format(thing1))
#         print("[*] THING2: {} [*]".format(thing2))
#         self.stream.__exit__()
#         self.device.__exit__()
#         self.uvc.__exit__()
#         raise(SystemExit)


class Color(Enum):
    BACKGROUND = "#000"
    FONT_COLOR = "#FFF"
    HEAT_PANEL = "#F00"
    DATA_PANEL = "#0F0"
    DEBUG_PANEL = "#00F"


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
        width=640,
        height=480,
    )
    heat_image_panel.pack(side=tk.TOP, anchor=tk.W)
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
            font=("default", 40)
        )
        new_label.pack()
    return parent, string_pointers


def get_data_panel(parent, data_set):
    data_panel = tk.Frame(parent)
    data_panel.configure(
        bg=Color.DATA_PANEL.value,
        height=10,
    )

    updated_data_panel, string_pointers = generate_data_labels(data_panel, data_set)

    updated_data_panel.pack(side=tk.TOP, anchor=tk.E)
    return updated_data_panel, string_pointers


def get_ambient_temp_data(tmpsensor, last_req_time, last_data_set):
    if time.time() - last_req_time > settings["ambient_temp_delay"]:
        (hum, temp) = tmpsensor.sense()
        hum = round(hum, 2)
        temp = round(temp, 2)

        last_data_set = {"temp": temp, "hum": hum}
        
        if not settings["use_humidity"]:
            del last_data_set["use_humidity"] 

        last_req_time = time.time()

    return last_data_set, last_req_time


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
        bg=Color.DEBUG_PANEL.value,
    )
    updated_debug_panel, string_pointers = generate_debug_labels(debug_panel)
    updated_debug_panel.pack(side=tk.BOTTOM, anchor=tk.W)
    return updated_debug_panel, string_pointers


def editImageData(frame):
    frame = cv2.resize(frame[:, :], (640, 480))

    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frame)
    cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(frame, 8, frame)
    img = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)

    # https://docs.opencv.org/master/d3/d50/group__imgproc__colormap.html
    img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)

    display_temperature(img, minVal, minLoc, (255, 255, 255))
    display_temperature(img, maxVal, maxLoc, (255, 255, 255))

    return Image.fromarray(ImageTk.PhotoImage(img))


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
    with Board() as _, MotionSense(7) as motion_sensor, TempSense(17) as ambient_temp_sensor:
        # Open thermal camera stream
        cv2_stream = get_stream()

        # SETUP AMBIENT TEMP SENSOR
        last_ambient_temp_req_time = 0
        data_set = 0
        data_set, last_ambient_temp_req_time = get_ambient_temp_data(
            ambient_temp_sensor,
            last_ambient_temp_req_time,
            data_set
        )  # return dict for display

        # GET ROOT WINDOW
        window = get_main_window()

        # SETUP VIDEO STREAM AND DATA PANELS
        heat_image_panel = get_heat_image_panel(window)
        data_panel, data_string_pointers = get_data_panel(window, data_set)

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

                # GET IMAGE FROM CAMERA
                cv2_stream.grab()
                read_flag, frame = cv2_stream.retrieve(0)

                # Update heat image panel
                img = editImageData(frame)
                heat_image_panel.configure(
                    image=img
                )
                heat_image_panel.image = img

                # Update data panel
                data_set, last_ambient_temp_req_time = get_ambient_temp_data(
                    ambient_temp_sensor,
                    last_ambient_temp_req_time,
                    data_set
                )
                update_string_pointers(data_string_pointers, data_set)

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

