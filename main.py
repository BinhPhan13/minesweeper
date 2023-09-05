from view import GameView
from game import Mode, Game
from tkinter import Tk

root = Tk()
root.resizable(False,False)

m = Mode(9,9, 10)
g = Game(m)
gv = GameView(root, g)

g.setview(gv)
gv.pack()

root.mainloop()