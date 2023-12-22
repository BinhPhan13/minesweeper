from helper import Board, vicinity
from enum import Enum
import random

class Mode:
    ATTRS = ('height', 'width', 'mines')
    def __init__(self, height:int, width:int, mines:int):
        self._height = height
        self._width = width
        self._mines = mines
        assert self.num_safes >= 9

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def mines(self):
        return self._mines

    @property
    def num_safes(self):
        return self.height*self.width-self.mines

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mode): return False
        return self.height == other.height \
        and self.width == other.width \
        and self.mines == other.mines \

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
    BADFLAG = -4

    def __str__(self) -> str:
        map_spec = {
            Item.FLAG:'F',
            Item.UNOPEN:'-',
            Item.BOMB:'X',
            Item.BADFLAG:'?'
        }
        try: return map_spec[self]
        except: return f'{self.value}'

class GameState(Enum):
    PLAY = 0
    WIN = 1
    LOSE = -1

class Game:
    def __init__(self, mode:Mode):
        self._mode = mode
        self._data = Board(mode.height, mode.width, 0)
        self._field = Board(mode.height, mode.width, Item.UNOPEN)

        self._mines_left = mode.mines
        self._safes_left = mode.num_safes

        self._start_coord = None
        self._state = GameState.PLAY

    def _gen_data(self, sr:int, sc:int):
        viable_coords = [
            (r,c) for r,c in self._data.all_coords
            if abs(r-sr) > 1 or abs(c-sc) > 1
        ]
        mines_coords = random.sample(viable_coords, self.mode.mines)

        for r,c in mines_coords:
            self._data[r,c] = -1
            for i,j in vicinity(r,c):
                if not self._data.valid_bound(i,j): continue
                if self._data[i,j] == -1: continue
                self._data[i,j] += 1

        self._start_coord = sr,sc

        # temporarily remove game view
        view = self.__view
        self.__view = None

        # using solver to ensure solvability
        from solver import Solver
        solver = Solver(self)
        solver.solve()

        # reset and regain view
        self.restart(False)
        self.__view = view

    def _adjust(self, row:int, col:int, item:Item):
        if self._field[row,col] is item: return
        self._field[row,col] = item
        try:
            self.__view.adjust_grid(row, col, item)
            self.__view.update()
        except: pass

    def _valid_action(self, row:int, col:int):
        return self._state is GameState.PLAY \
        and self._field.valid_bound(row,col)

    def open(self, row:int, col:int, auto:bool=True):
        if not self._valid_action(row,col): return False
        if self._field[row,col] is not Item.UNOPEN: return False
        if not self._start_coord: self._gen_data(row,col)

        if self._data[row,col] == -1: # lose
            self._adjust(row, col, Item.BOMB)
            for r,c in self._field.all_coords:
                if self._field[r,c] is Item.FLAG \
                and self._data[r,c] != -1:
                    self._adjust(r,c, Item.BADFLAG)
            self._state = GameState.LOSE
        else:
            self._adjust(row, col, Item(self._data[row,col]))
            self._safes_left -= 1

            assert self.safes_left >= 0
            if self.safes_left == 0: # win
                for r,c in self._field.all_coords:
                    self.flag(r,c)
                self._state = GameState.WIN

            # auto open around ZERO
            if auto and self._field[row,col] is Item.ZERO:
                for r,c in vicinity(row,col):
                    self.open(r,c)
        return True

    def flag(self, row:int, col:int):
        if not self._valid_action(row,col): return False
        if self._field[row,col] is not Item.UNOPEN: return False
        if self._mines_left <= 0: return False

        self._adjust(row, col, Item.FLAG)
        self._mines_left -= 1
        return True

    def unflag(self, row:int, col:int):
        if not self._valid_action(row,col): return False
        if self._field[row,col] is not Item.FLAG: return False

        self._adjust(row, col, Item.UNOPEN)
        self._mines_left += 1
        return True

    def auto(self, row:int, col:int):
        if not self._valid_action(row,col): return False
        mines_left = self._field[row,col].value
        if mines_left <= 0: return False

        unopens = []
        for r,c in vicinity(row,col):
            if not self._field.valid_bound(r,c): continue
            item = self._field[r,c]
            if item is Item.UNOPEN:
                unopens.append((r,c))
            elif item is Item.FLAG:
                mines_left -= 1

        if len(unopens) == 0: return False # nothing to do
        if mines_left == 0:
            for r,c in vicinity(row,col):
                self.open(r,c)
        elif mines_left == len(unopens):
            for r,c in vicinity(row,col):
                self.flag(r,c)
        else: return False # not a trivial case
        return True

    def restart(self, new:bool=True):
        for r,c in self._field.all_coords:
            self._adjust(r,c, Item.UNOPEN)

        self._mines_left = self.mode.mines
        self._safes_left = self.mode.num_safes
        self._state = GameState.PLAY

        if new:
            self._start_coord = None
            for r,c in self._data.all_coords:
                self._data[r,c] = 0

    def item_at(self, row:int, col:int) -> Item|None:
        return self._field[row,col] \
        if self._field.valid_bound(row,col) else None

    def setview(self, view):
        from view import GameView
        assert isinstance(view, GameView)
        self.__view = view

    @property
    def field_coords(self):
        return self._field.all_coords

    @property
    def mines_left(self):
        return self._mines_left

    @property
    def safes_left(self):
        return self._safes_left

    @property
    def state(self):
        return self._state

    @property
    def mode(self):
        return self._mode

    @property
    def start_coord(self):
        return self._start_coord

    # functions for modify data (requested by solver)
    def modify(self, store):
        '''Swap mines in unknown squares to make an eqn from store trivial'''
        from store import Store, EQN
        assert isinstance(store, Store)

        eqn = store.pick()
        if not eqn: return False

        # get full(mine)/clear(safe) from given equation's variables
        full, clear = [], []
        for r,c in eqn.vars_pos:
            assert self._field[r,c] is Item.UNOPEN
            if self._data[r,c] == -1:
                full.append((r,c))
            else: clear.append((r,c))

        # must contain both, else it is trivial
        assert full and clear

        # get candidates to swap with full/clear above, must be unopen
        # prioritize 'near' squares, which has contact with known squares
        near, far = [], []
        for r,c in self._field.all_coords:
            if eqn.munge(EQN(r,c,1,0), False): continue
            if self._field[r,c] is not Item.UNOPEN: continue

            isnear = False
            for i,j in vicinity(r,c):
                if not self._field.valid_bound(i,j): continue
                v = self._field[i,j].value
                if v >= 0:
                    assert v > 0
                    isnear = True
                    break

            if isnear: near.append((r,c))
            else: far.append((r,c))

        random.shuffle(near)
        if not near:
            # prioritize empty the set
            far.sort(key=lambda pos:-self._data[pos]) # why?
        else: random.shuffle(far)

        usable = near + far

        # get list of squares to be filled/emptied
        # full squares fill in filled squares
        # clear squares get mines from emptied squares
        fill, empty = [], []
        old, new = None, None # coordinates of old and new mines

        for r,c in usable:
            if self._data[r,c] == -1:
                empty.append((r,c))
            else: fill.append((r,c))

            if len(fill) == len(full):
                old, new = full, fill
                break
            elif len(empty) == len(clear):
                old, new = empty, clear
                break

        if not old: # cannot find enough to fill/empty
            assert not new
            return False

        changes:list[tuple[int,int,bool]] = []
        changes.extend((*pos, False) for pos in old)
        changes.extend((*pos, True) for pos in new)

        # update equations in store
        for r,c, ismine in changes:
            d = 1 if ismine else -1
            e0 = EQN(r,c,1,0)
            for i in store.get_overlap(e0):
                e1 = store.get_eqn(i)
                store.remove(i)

                new_mines = e1.mines + d
                new_eqn = EQN(e1.sr, e1.sc, e1.mask, new_mines)
                store.add(new_eqn)
            store.clean()

        self.__apply(changes)
        return True

    def __apply(self, changes:list[tuple[int,int,bool]]):
        '''Adjust data and field on changes'''
        for r,c, ismine in changes:
            self._data[r,c] = -1 if ismine else -2

            d = 1 if ismine else -1
            for i,j in vicinity(r,c):
                if not self._data.valid_bound(i,j) \
                    or self._data[i,j] < 0: continue
                self._data[i,j] += d
                assert self._data[i,j] >= 0

                if self._field[i,j] is not Item.UNOPEN:
                    self._adjust(i,j, Item(self._data[i,j]))

        # adjust old mines to new value
        for r,c, ismine in changes:
            if ismine: continue
            assert self._data[r,c] == -2
            v = 0
            for i,j in vicinity(r,c):
                if self._data.valid_bound(i,j) \
                and self._data[i,j] == -1:
                    v += 1
            self._data[r,c] = v

            # old mines can either be UNOPEN or FLAG
            # neither are important to adjust the field

    def dig(self):
        '''Replace a known flag by a unknown safe square'''
        flags, safes = [], []
        for r,c in self._field.all_coords:
            if self._field[r,c] is Item.FLAG:
                # make sure the flag connect between
                # a safe known square and an unopen square
                has_safe, has_unopen = False, False
                for i,j in vicinity(r,c):
                    if not self._field.valid_bound(i,j): continue
                    if self._field[i,j] is Item.UNOPEN:
                        has_unopen = True
                    elif self._field[i,j].value >= 0:
                        assert self._field[i,j].value > 0
                        has_safe = True

                    if has_safe and has_unopen:
                        flags.append((r,c))
                        break

            elif self._field[r,c] is Item.UNOPEN \
            and self._data[r,c] != -1:
                safes.append((r,c))

        old = random.choice(flags)
        new = random.choice(safes)

        changes:list[tuple[int,int,bool]] = [(*old, False), (*new, True)]
        self.__apply(changes)

        return old # only need to return place of digged flag to solver