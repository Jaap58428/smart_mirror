import tkinter as tk
from time import sleep
from time import time
import random
import socket
from enum import Enum
import os

if os.name == 'nt':
    from sensor import MotionSenseMock as MotionSense
    from sensor import TempSenseMock as TempSense
    from sensor import BoardMock as Board
else:
    from sensor import Board
    from sensor import TempSense
    from sensor import MotionSense

settings = {
    "use_humidity_sensor": True,
    "display_host_ip": True,
    "display_sleep_timer": True,
    "display_debug_panel": True,
    "sleep_timeout_sec": 5,
    "screen_max_frame_time_sec": 0.033  # equals to around 30fps
}



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
        bg=Color.BACKGROUND.value
    )

    window.focus_set()
    window.attributes("-fullscreen", True)
    window.minsize(150, 100)

    return window


def get_heat_image_panel(parent):
    heat_image_panel = tk.Frame(parent)
    heat_image_panel.configure(
        bg=Color.HEAT_PANEL.value,
    )
    heat_image_panel.place(relwidth=0.2, relheight=0.2, anchor=tk.NW)

    # TODO add video stream

    return heat_image_panel


def generate_data_labels(parent, data_set):
    string_pointers = {}
    for attr, val in data_set.items():
        string_pointers[attr] = tk.StringVar()
        string_pointers[attr].set('{0}: {1}'.format(attr, str(val)))
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


def get_data(tmpsensor, motionsensor):

    (hum, temp) = tmpsensor.sense()
    hum = round(hum, 2)
    temp = round(temp, 2)
    motion = motionsensor.sense()
    return {"temp": temp, "hum": hum, "motion": motion }


def update_string_pointers(string_pointers, data_set):
    for attr, pointer in string_pointers.items():
        pointer.set('{0}: {1}'.format(attr, data_set[attr]))


def kill_gui(gui_elements):
    # heat image panel, requires place_remove()
    gui_elements[0].place_forget()

    # data & debug panel require pack_forget()
    gui_elements[1].pack_forget()
    if settings["display_debug_panel"]:
        gui_elements[2].pack_forget()


def show_gui(gui_elements):
    # heat image panel, requires place_remove()
    gui_elements[0].place(relwidth=0.2, relheight=0.2, anchor=tk.NW)

    # data & debug panel require pack_forget()
    gui_elements[1].pack(side=tk.TOP, anchor=tk.E)
    if settings["display_debug_panel"]:
        gui_elements[2].pack(side=tk.BOTTOM, anchor=tk.W)


def stream_video():
    # TODO: Implement updating video screen panel
    pass


def movement():
    # TODO: Implement movement detection
    pass


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
        ip = str(socket.gethostbyname(socket.gethostname()))
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


if __name__ == '__main__':
    with Board() as _, MotionSense(7) as m, TempSense(17) as t:
        data_set = get_data(t, m)

        window = get_main_window()

        heat_image_panel = get_heat_image_panel(window)
        data_panel, data_string_pointers = get_data_panel(window, data_set)

        panels = [
            heat_image_panel,
            data_panel
        ]

        if settings["display_debug_panel"]:
            debug_panel, debug_string_pointers = get_debug_panel(window)
            panels.append(debug_panel)

        is_gui_shown = True

        # At boot set start time
        start_time = time()
        while(True):
            # If timer hasn't passed into sleep: ACTIVE
            time_passed = time() - start_time
            if time_passed < settings["sleep_timeout_sec"]:
                stream_video()

                # Update data panel
                data_set = get_data(t, m)
                update_string_pointers(data_string_pointers, data_set)

                if settings["display_debug_panel"] and settings["display_sleep_timer"]:
                    time_str = round(time_passed, 1)
                    timer_str = "Timer: {0} ({1})".format(str(time_str), settings["sleep_timeout_sec"])
                    debug_string_pointers["display_sleep_timer"].set(timer_str)

                if movement():
                    start_time = time()

            # Else fall into PASSIVE, check for movement
            else:
                kill_gui(panels) if is_gui_shown else False
                # Once movement is detected, show GUI and reset timer
                if movement():
                    show_gui(panels)
                    start_time = time()

            window.update_idletasks()
            window.update()

            sleep(settings["screen_max_frame_time_sec"])
