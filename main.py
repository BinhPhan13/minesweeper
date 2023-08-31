from gui import GridView
from tkinter import Tk

root = Tk()
root.resizable(False,False)
root.config(bg='#d2d2d2') # better sunken effect

HEIGHT = 20
WIDTH = 30

gv = GridView(root, HEIGHT, WIDTH)
gv.pack(padx=30, pady=30)

root.mainloop()