import tkinter as tk

window = tk.PanedWindow()
window.pack(expand=1)

banner = tk.PanedWindow(window)
banner.pack(text="Banner")

bannerText = tk.Label()
bannerText.pack(text="LABEL")

tk.mainloop()