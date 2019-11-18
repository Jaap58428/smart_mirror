import tkinter as tk
from time import sleep
import random

colors = {
    "BACKGROUND": "#000",
    "FONT_COLOR": "#fff",
    "HEAT_IMAGE": "#f00",
    "DATA_PANEL": "#00f"
}


def get_main_window():
    window = tk.Tk()
    window.title("Smart Mirror GUI")
    window.configure(
        bg=colors["BACKGROUND"],
    )
    window.geometry('600x1000')
    window.minsize(150, 100)
    return window


def get_heat_image_panel(parent):
    heat_image_panel = tk.Frame(parent)
    heat_image_panel.configure(
        bg=colors["HEAT_IMAGE"],
    )
    heat_image_panel.place(relwidth=0.2, relheight=0.2, anchor=tk.NW)

    return heat_image_panel


def generate_data_labels(parent, data_set):
    string_pointers = {}
    for attr, val in data_set.items():
        string_pointers[attr] = tk.StringVar()
        string_pointers[attr].set('{0}: {1}'.format(attr, str(val)))
        new_label = tk.Label(parent)
        new_label.configure(
            textvariable=string_pointers[attr],
            bg=colors["BACKGROUND"],
            fg=colors["FONT_COLOR"],
            anchor=tk.E
        )
        new_label.pack()
    return parent, string_pointers


def get_data_panel(parent, data_set):
    data_panel = tk.Frame(parent)
    data_panel.configure(
        bg=colors["DATA_PANEL"],
    )
    data_panel.place(relwidth=0.3, relheight=0.2, anchor=tk.NE)

    updated_data_panel, string_pointers = generate_data_labels(parent, data_set)

    return updated_data_panel, string_pointers


def get_mock_data():
    return {
        "temp": random.randint(1, 101),
        "hum": random.randint(1, 101),
    }


def update_string_pointers(string_pointers, data_set):
    for attr, pointer in string_pointers.items():
        pointer.set('{0}: {1}'.format(attr, data_set[attr]))


if __name__ == '__main__':
    data_set = get_mock_data()

    window = get_main_window()

    heat_image_panel = get_heat_image_panel(window)
    data_panel, string_pointers = get_data_panel(window, data_set)

    while(True):
        data_set = get_mock_data()

        update_string_pointers(string_pointers, data_set)

        window.update_idletasks()
        window.update()

        sleep(0.1)
        sleep(0.033)  # equals to around 30fps
