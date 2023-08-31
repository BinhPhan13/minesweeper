from tkinter import *
from PIL import ImageTk
from helper import *

class GridView(Canvas):
    def __init__(self, master, height:int, width:int):
        super().__init__(master)

        self.__h, self.__w = height, width
        self.__cell_size = 20
        self.__bd = 4 # border width

        # in pixels
        self.__scrh = self.__h*self.__cell_size + self.__bd*2
        self.__scrw = self.__w*self.__cell_size + self.__bd*2

        self.config(highlightthickness=0,
            height=self.__scrh,
            width= self.__scrw
        )
        self.__load_imgs()
        self.__build()

        self.bind('<ButtonRelease-1>', self.lclick)

    def __load_imgs(self):
        self.__imgs = {
            item: ImageTk.PhotoImage(
                get_img(ITEM_IMG_FILES[item],
                (self.__cell_size, self.__cell_size)
            )) for item in Item
        }
    def __build(self):
        self.__img_ids = [
            [None for _ in range(self.__w)]
            for _ in range(self.__h)
        ] # use to change image later on

        for r in range(self.__h):
            for c in range(self.__w):
                self.__img_ids[r][c] = self.create_image(
                    c*self.__cell_size + self.__bd,
                    r*self.__cell_size + self.__bd,
                    image=self.__imgs[Item.UNOPEN], anchor=NW
                )

        # sunken effect
        for p in range(self.__bd):
            self.create_line(0,p, self.__scrw-p,p,
                fill='#999999')
            self.create_line(p,0, p,self.__scrh-p,
                fill='#999999')

    def lclick(self, event:Event):
        r = (event.y-self.__bd)//self.__cell_size
        c = (event.x-self.__bd)//self.__cell_size

        if in_range(r, -1, self.__h) \
        and in_range(c, -1, self.__w):
            self.itemconfig(
                self.__img_ids[r][c],
                image=self.__imgs[Item.ZERO]
            )