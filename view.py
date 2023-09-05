from helper import get_img, vicinity
from game import Item, GameState, Game

from tkinter import *
from tkinter import font
from PIL import ImageTk

class _GridView(Canvas):
    CELL_SIZE = 20
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
        self.__scrh = self.__h*self.CELL_SIZE + self.BD*2
        self.__scrw = self.__w*self.CELL_SIZE + self.BD*2

        self.config(highlightthickness=0,
            height=self.__scrh,
            width= self.__scrw
        )
        self.__load_imgs()
        self.__build()

    def __load_imgs(self):
        self.__tkimgs = {
            item: ImageTk.PhotoImage(self.IMGS[item])
            for item in self.IMGS
        }

    def __build(self):
        self.__img_ids = [
            [None for _ in range(self.__w)]
            for _ in range(self.__h)
        ] # use to change image later on

        for r in range(self.__h):
            for c in range(self.__w):
                self.__img_ids[r][c] = self.create_image(
                    c*self.CELL_SIZE + self.BD,
                    r*self.CELL_SIZE + self.BD,
                    image=self.__tkimgs[Item.UNOPEN], anchor=NW
                )

        # sunken effect
        for p in range(self.BD):
            self.create_line(0,p, self.__scrw-p,p,
                fill='#999999')
            self.create_line(p,0, p,self.__scrh-p,
                fill='#999999')

    def handle_click(self, event:Event):
        r = (event.y-self.BD)//self.CELL_SIZE
        c = (event.x-self.BD)//self.CELL_SIZE
        return r,c

    def adjust(self, row:int, col:int, item:Item):
        self.itemconfig(
            self.__img_ids[row][col],
            image=self.__tkimgs[item]
        )

class _SttBar(Label):
    def __init__(self, master):
        super().__init__(master)
        self.__stt = StringVar()
        self.config(
            textvariable=self.__stt,
            font=font.Font(size=13),
            anchor=W
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
        self.__stt.set(stt)

class Timer(Label):
    @staticmethod
    def sec2min(seconds:int):
        mins = seconds//60
        secs = seconds%60
        if mins > 99: mins, secs = 99, 59

        return f'{mins:0>2}:{secs:0>2}'

    def __init__(self, master):
        self.__elapsed_secs = 0
        self.__time_var = StringVar()
        super().__init__(master)
        self.config(
            textvariable=self.__time_var,
            font=font.Font(size=13),
        )
        self.reset()

    def start(self):
        self.__ended = False
        self.after(1000, self.__count)

    def __count(self):
        if self.__ended: return
        self.__elapsed_secs += 1
        self.__adjust()
        self.after(1000, self.__count)

    def stop(self):
        self.__ended = True

    def reset(self):
        self.stop()
        self.__elapsed_secs = 0
        self.__adjust()

    def __adjust(self):
        self.__time_var.set(f'[{Timer.sec2min(self.__elapsed_secs)}]')

class GameView(Frame):
    def __init__(self, master, game:Game):
        super().__init__(master)
        self.__game = game
        mode = self.__game.mode

        gridframe = Frame(self, bg='#d2d2d2') # for sunken effect
        gridframe.pack()
        self.__grid = _GridView(gridframe, mode.height, mode.width)
        self.__grid.pack(padx=30, pady=30)

        self.__grid.bind('<ButtonRelease-1>', self.lclick)
        self.__grid.bind('<3>', self.rclick)

        self.__grid.bind('<1>', self.__preview)
        self.__grid.bind('<B1-Motion>', self.__preview)
        self.__preview_coord = None

        self.__sttbar = _SttBar(self)
        self.__sttbar.config(bg='#c0c0c0',
            highlightthickness=1, highlightbackground='#a0a0a0'
        )
        self.__sttbar.pack(fill=X, side=RIGHT, expand=True)
        self.adjust_stt()

        self.__timer = Timer(self)
        self.__timer.config(bg='#c0c0c0',
            highlightthickness=1, highlightbackground='#a0a0a0'
        )
        self.__timer.pack(fill=X, side=LEFT)

    def lclick(self, event:Event):
        self.__free_preview()
        r,c = self.__grid.handle_click(event)

        first_click = not self.__game.has_data

        if self.__game.open(r,c):pass
        elif self.__game.auto(r,c):pass
        self.adjust_stt()
        
        if self.__game.state is not GameState.PLAY:
            self.__timer.stop()

        if first_click: self.__timer.start()

    def rclick(self, event:Event):
        r,c = self.__grid.handle_click(event)
        if self.__game.flag(r,c):pass
        elif self.__game.unflag(r,c):pass
        self.adjust_stt()

    def reset(self):
        self.__game.restart()
        self.adjust_stt()
        self.__timer.reset()

    def adjust_stt(self):
        self.__sttbar.adjust(
            self.__game.mines_left,
            self.__game.safes_left,
            self.__game.state
        )

    def adjust_grid(self, row:int, col:int, item:Item):
        self.__grid.adjust(row, col, item)

    def __preview(self, event:Event):
        r,c = self.__grid.handle_click(event)
        item = self.__game.item_at(r,c)
        if not item: return
        if (r,c) == self.__preview_coord: return

        self.__free_preview()
        self.__preview_coord = r,c

        if item is Item.UNOPEN:
            self.__grid.adjust(r,c, Item.ZERO)
        elif item.value > 0:
            for i,j in vicinity(r,c):
                item = self.__game.item_at(i,j)
                if item is Item.UNOPEN:
                    self.__grid.adjust(i,j, Item.ZERO)

    def __free_preview(self):
        if not self.__preview_coord: return
        r,c = self.__preview_coord

        assert self.__game.item_at(r,c)
        for i,j in vicinity(r,c):
            item = self.__game.item_at(i,j)
            if not item: continue
            self.__grid.adjust(i,j, item)

        self.__preview_coord = None