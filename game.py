from helper import Board, vicinity
from enum import Enum
import random

class Mode:
    def __init__(self, height:int, width:int, mines:int):
        self.__height = height
        self.__width = width
        self.__mines = mines
        assert self.num_safes >= 9

    @property
    def height(self):
        return self.__height

    @property
    def width(self):
        return self.__width

    @property
    def mines(self):
        return self.__mines

    @property
    def num_safes(self):
        return self.height*self.width-self.mines

class Item(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

    FLAG = -1
    UNOPEN = -2
    BOMB = -3

    def __str__(self) -> str:
        map_spec = {
            Item.FLAG:'F',
            Item.UNOPEN:'-',
            Item.BOMB:'X',
        }
        try: return map_spec[self]
        except: return f'{self.value}'

class GameState(Enum):
    PLAY = 0
    WIN = 1
    LOSE = -1

class Game:
    def __init__(self, mode:Mode):
        self.__mode = mode
        self.__data = Board(mode.height, mode.width, 0)
        self.__field = Board(mode.height, mode.width, Item.UNOPEN)

        self.__mines_left = mode.mines
        self.__safes_left = mode.num_safes

        self.__has_data = False
        self.__state = GameState.PLAY

    def __gen_data(self, sr:int, sc:int):
        viable_coords = [
            (r,c) for r,c in self.__data.all_coords
            if abs(r-sr) > 1 or abs(c-sc) > 1
        ]
        mines_coords = random.sample(viable_coords, k=self.mode.mines)

        for r,c in mines_coords:
            self.__data[r,c] = -1
            for i,j in vicinity(r,c):
                if not self.__data.valid_bound(i,j): continue
                if self.__data[i,j] == -1: continue
                self.__data[i,j] += 1

        self.__has_data = True

    def __adjust(self, row:int, col:int, item:Item):
        self.__field[row,col] = item
        try: self.__view.adjust_grid(row, col, item)
        except: print('No view!')

    def __valid_action(self, row:int, col:int):
        return self.__state is GameState.PLAY \
        and self.__field.valid_bound(row,col)

    def open(self, row:int, col:int):
        if not self.__valid_action(row,col): return False
        if self.__field[row,col] is not Item.UNOPEN: return False
        if not self.__has_data: self.__gen_data(row,col)

        if self.__data[row,col] == -1: # lose
            self.__adjust(row, col, Item.BOMB)
            self.__state = GameState.LOSE
        else:
            self.__adjust(row, col, Item(self.__data[row,col]))
            self.__safes_left -= 1
            
            assert self.safes_left >= 0
            if self.safes_left == 0: # win
                for r,c in self.__field.all_coords:
                    self.flag(r,c)
                self.__state = GameState.WIN

            # auto open around ZERO
            if self.__field[row,col] is Item.ZERO:
                for r,c in vicinity(row,col):
                    self.open(r,c)
        return True

    def flag(self, row:int, col:int):
        if not self.__valid_action(row,col): return False
        if self.__field[row,col] is not Item.UNOPEN: return False
        if self.__mines_left <= 0: return False

        self.__adjust(row, col, Item.FLAG)
        self.__mines_left -= 1
        return True

    def unflag(self, row:int, col:int):
        if not self.__valid_action(row,col): return False
        if self.__field[row,col] is not Item.FLAG: return False 

        self.__adjust(row, col, Item.UNOPEN)
        self.__mines_left += 1
        return True

    def setview(self, view):
        from gui import GameView
        assert isinstance(view, GameView)
        self.__view = view

    @property
    def mines_left(self):
        return self.__mines_left

    @property
    def safes_left(self):
        return self.__safes_left

    @property
    def state(self):
        return self.__state

    @property
    def mode(self):
        return self.__mode