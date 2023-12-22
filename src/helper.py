from __init__ import EXE_DIR
from PIL import Image
import datetime
import calendar
from math import floor

IMG_DIR = EXE_DIR + 'images/'
def get_img(file:str, size:tuple[int,int]):
    return Image.open(IMG_DIR+file).resize(
        size, Image.LANCZOS)

def in_range(v, lb, ub):
    '''Return whether lb < v < ub'''
    return lb < v and v < ub

def vicinity(r:int, c:int, pad:int=1):
    return ((r+dr,c+dc)
        for dr in range(-pad, pad+1)
        for dc in range(-pad, pad+1)
    )

def bitcnt16(word:int):
    assert isinstance(word, int)
    # Hamming weight
    word = ((word>>1)&0x5555) + (word&0x5555)
    word = ((word>>2)&0x3333) + (word&0x3333)
    word = ((word>>4)&0x0707) + (word&0x0707)
    word = ((word>>8)&0x000F) + (word&0x000F)
    return word

def repr_today():
    today = datetime.date.today()

    d = today.day
    m = calendar.month_abbr[today.month]
    y = today.year

    return f'{d:0>2} {m} {y}'

def sec2min(seconds:float):
    seconds = floor(seconds)
    mins = seconds//60
    secs = seconds%60
    if mins > 99: mins, secs = 99, 59

    return f'{mins:0>2}:{secs:0>2}'


WS = ' '
BR = '\n'
class Board:
    '''2D array wrapper'''
    def __init__(self, h:int, w:int, default=None):
        self.__h, self.__w = h, w
        self.__data = [
            [default for _ in range(self.__w)]
            for _ in range(self.__h)
        ]

    def __getitem__(self, coord:tuple[int,int]):
        r,c = coord
        if not self.valid_bound(r,c):
            raise IndexError(f'index out of range {r,c}')
        return self.__data[r][c]

    def __setitem__(self, coord:tuple[int,int], v):
        r,c = coord
        if not self.valid_bound(r,c):
            raise IndexError(f'index out of range {r,c}')
        self.__data[r][c] = v

    def valid_bound(self, row:int, col:int):
        return in_range(row, -1, self.__h) \
            and in_range(col, -1, self.__w)

    def show(self, size:int=2):
        s = f'{WS:<{size}}' + WS.join((
            f'{j%10:>{size}}' for j in range(self.__w)
        )) + BR

        s += BR.join((
            f'{i%10:<{size}}' + WS.join((
                f'{self.__data[i][j]:>{size}}'
                for j in range(self.__w)
            )) for i in range(self.__h)
        )) + BR

        print(s)

    @property
    def all_coords(self):
        return ((r,c)
            for r in range(self.__h)
            for c in range(self.__w)
        )

    @property
    def height(self):
        return self.__h

    @property
    def width(self):
        return self.__w