import tkinter as tk
from time import sleep
import random

colors = {
    "BACKGROUND": "#000",
    "BANNER": "#0f0",
    "HEAT_IMAGE": "#f00"
}


def get_main_window():
    window = tk.Tk()
    window.title("Smart Mirror GUI")
    window.configure(bg=colors["BACKGROUND"])
    return window


def get_banner(parent):
    banner = tk.Frame(parent)
    banner.configure(
        bg=colors["BANNER"],
        bd=0,
        height=600,
        width=800,
    )
    banner.pack(side=tk.TOP)
    return banner


def get_heat_image_panel(parent):
    heat_image_panel = tk.Frame(parent, bg=colors["HEAT_IMAGE"])
    heat_image_panel.configure(height="300", width="500")
    banner.pack()
    return heat_image_panel


def generate_data_labels(banner, data_set):

    string_pointers = {}

    for attr, val in data_set.items():
        string_pointers[attr] = tk.StringVar()
        string_pointers[attr].set('{0}: {1}'.format(attr, str(val)))
        new_label = tk.Label(banner, textvariable=string_pointers[attr])
        new_label.pack()

    return banner, string_pointers


def get_data_panel(parent, data_set):
    data_panel = tk.Frame(parent, bg=colors["HEAT_IMAGE"])
    data_panel.configure(height="300", width="500")
    banner.pack()

    filled_banner, string_pointers = generate_data_labels(banner, data_set)

    return data_panel, string_pointers


def get_mock_data():
    return {
        "temp": random.randint(1, 101),
        "hum": random.randint(1, 101),
    }


def update_string_pointers(string_pointers, data_set):
    for attr, pointer in string_pointers.items():
        pointer.set(data_set[attr])


if __name__ == '__main__':
    data_set = get_mock_data()

    window = get_main_window()
    banner = get_banner(window)

    heat_image_panel = get_heat_image_panel(banner)
    data_panel, string_pointers = get_data_panel(banner, data_set)

    while(True):
        data_set = get_mock_data()

        update_string_pointers(string_pointers, data_set)

        # string_pointers['temp'].set(i)
        window.update_idletasks()
        window.update()

        sleep(1)
        # sleep(0.033)  # equals to around 30fps
