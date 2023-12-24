from helper import get_img, vicinity, sec2min, repr_today
from game import Item, GameState, Game

from time import time

from tkinter import *
from tkinter import font
from PIL import ImageTk

class _GridView(Canvas):
    CELL_SIZE = 25
    BD = 5

    IMG_SIZE = CELL_SIZE, CELL_SIZE
    IMGS = {
        Item.ZERO: get_img('0.png', IMG_SIZE),
        Item.ONE: get_img('1.png', IMG_SIZE),
        Item.TWO: get_img('2.png', IMG_SIZE),
        Item.THREE: get_img('3.png', IMG_SIZE),
        Item.FOUR: get_img('4.png', IMG_SIZE),
        Item.FIVE: get_img('5.png', IMG_SIZE),
        Item.SIX: get_img('6.png', IMG_SIZE),
        Item.SEVEN: get_img('7.png', IMG_SIZE),
        Item.EIGHT: get_img('8.png', IMG_SIZE),

        Item.FLAG: get_img('flag.png', IMG_SIZE),
        Item.UNOPEN: get_img('unopen.png', IMG_SIZE),
        Item.BOMB: get_img('bomb.png', IMG_SIZE),
        Item.BADFLAG: get_img('badflag.png', IMG_SIZE)
    }

    def __init__(self, master, height:int, width:int):
        super().__init__(master)

        self.__h, self.__w = height, width
        # in pixels
        self._scrh = self.__h*self.CELL_SIZE + self.BD*2
        self._scrw = self.__w*self.CELL_SIZE + self.BD*2

        self.config(highlightthickness=0,
            height=self._scrh,
            width= self._scrw
        )
        self._load_imgs()
        self._build()

    def _load_imgs(self):
        self._tkimgs = {
            item: ImageTk.PhotoImage(self.IMGS[item])
            for item in self.IMGS
        }

    def _build(self):
        self._img_ids = [
            [None for _ in range(self.__w)]
            for _ in range(self.__h)
        ] # use to change image later on

        for r in range(self.__h):
            for c in range(self.__w):
                self._img_ids[r][c] = self.create_image(
                    c*self.CELL_SIZE + self.BD,
                    r*self.CELL_SIZE + self.BD,
                    image=self._tkimgs[Item.UNOPEN], anchor=NW
                )

        # sunken effect
        for p in range(self.BD):
            self.create_line(0,p, self._scrw-p,p,
                fill='#999999')
            self.create_line(p,0, p,self._scrh-p,
                fill='#999999')

    def handle_click(self, event:Event):
        r = (event.y-self.BD)//self.CELL_SIZE
        c = (event.x-self.BD)//self.CELL_SIZE
        return r,c

    def adjust(self, row:int, col:int, item:Item):
        self.itemconfig(
            self._img_ids[row][col],
            image=self._tkimgs[item]
        )

class _SttBar(Label):
    def __init__(self, master):
        super().__init__(master)
        self._stt = StringVar()
        self.config(
            textvariable=self._stt,
            font=font.Font(size=13),
            anchor=W, width=23
        )

    def adjust(self, mines_left:int, safes_left:int, state:GameState):
        if state is GameState.WIN:
            stt = 'COMPLETE !'
        elif state is GameState.LOSE:
            stt = 'DEAD !'
        else:
            stt = 'Mines left:' + f'{mines_left}'
            if safes_left < 10:
                stt += f' ({safes_left} safes left)'
        self._stt.set(stt)

class Timer(Label):
    def __init__(self, master):
        self._time_var = StringVar()
        super().__init__(master)
        self.config(
            textvariable=self._time_var,
            font=font.Font(size=13),
        )
        self._laps = 1000
        # stored seconds and started time
        self._time = 0.0
        self._stime = -0.1
        self._adjust()

    def start(self):
        self._stime = time()
        self.after(self._laps, self._count)

    def _count(self):
        self._adjust()
        if self._stime < 0: return
        self.after(self._laps, self._count)

    def stop(self):
        self._time = self.elapsed_time
        self._stime = -0.1
        self._adjust()

    def reset(self):
        self.stop()
        self._time = 0.0
        self._adjust()

    def _adjust(self):
        display_time = sec2min(self.elapsed_time)
        self._time_var.set(f'[{display_time}]')

    @property
    def elapsed_time(self):
        return self._time if self._stime < 0 \
        else self._time + time() - self._stime

class GameView(Frame):
    def __init__(self, master, game:Game, records:list):
        super().__init__(master)
        self._game = game
        mode = self._game.mode

        gridframe = Frame(self, bg='#d2d2d2') # for sunken effect
        gridframe.pack()
        self._grid = _GridView(gridframe, mode.height, mode.width)
        self._grid.pack(padx=30, pady=30)

        self._grid.bind('<ButtonRelease-1>', self.lclick)
        self._grid.bind('<3>', self.rclick)

        self._grid.bind('<1>', self._preview)
        self._grid.bind('<B1-Motion>', self._preview)
        self._preview_coord = None

        self._sttbar = _SttBar(self)
        self._sttbar.config(bg='#c0c0c0',
            highlightthickness=1, highlightbackground='#a0a0a0'
        )
        self._sttbar.pack(fill=X, side=RIGHT, expand=True)
        self.adjust_stt()

        self._timer = Timer(self)
        self._timer.config(bg='#c0c0c0',
            highlightthickness=1, highlightbackground='#a0a0a0'
        )
        self._timer.pack(fill=X, side=LEFT)

        self._records = records

    def lclick(self, event:Event):
        self._free_preview()
        first_click = not self._game.start_coord

        r,c = self._grid.handle_click(event)
        if not (self._game.open(r,c)
            or self._game.auto(r,c)): return

        self.adjust_stt()
        if first_click: self._timer.start()

        state = self._game.state
        if state is not GameState.PLAY:
            self._timer.stop()
            if state is GameState.WIN:
                self._add_record(self._timer.elapsed_time)

    def _add_record(self, playtime:float):
        rec = repr_today(), playtime
        self._records.append(rec)
        self._records.sort(key=lambda x:x[1])

    def rclick(self, event:Event):
        r,c = self._grid.handle_click(event)
        if not (self._game.flag(r,c)
            or self._game.unflag(r,c)): return

        self.adjust_stt()

    def reset(self):
        self._game.restart()
        self.adjust_stt()
        self._timer.reset()

    def adjust_stt(self):
        self._sttbar.adjust(
            self._game.mines_left,
            self._game.safes_left,
            self._game.state
        )

    def adjust_grid(self, row:int, col:int, item:Item):
        self._grid.adjust(row, col, item)

    def _preview(self, event:Event):
        r,c = self._grid.handle_click(event)
        item = self._game.item_at(r,c)
        if not item: return
        if (r,c) == self._preview_coord: return

        self._free_preview()
        self._preview_coord = r,c

        if item is Item.UNOPEN:
            self._grid.adjust(r,c, Item.ZERO)
        elif item.value > 0:
            for i,j in vicinity(r,c):
                item = self._game.item_at(i,j)
                if item is Item.UNOPEN:
                    self._grid.adjust(i,j, Item.ZERO)

    def _free_preview(self):
        if not self._preview_coord: return
        r,c = self._preview_coord

        assert self._game.item_at(r,c)
        for i,j in vicinity(r,c):
            item = self._game.item_at(i,j)
            if not item: continue
            self._grid.adjust(i,j, item)

        self._preview_coord = None
