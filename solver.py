from game import Game, GameState, Item
from eqn import EQN
from store import Store
from helper import vicinity, bitcnt16

class Solver:
    def __init__(self, game:Game):
        self.__game = game
        self.__todo_sqs:list[tuple[int,int]] = []
        self.__store = Store()

    def __setup(self):
        self.__todo_sqs.clear()
        self.__store.clear()

    def solve(self):
        if not self.__game.start_coord: return
        self.__setup()
        self.__game.restart(False)
        self.__open(*self.__game.start_coord)
        
        self.__iter()

    def __iter(self):
        while self.__todo_sqs:
            self.__process_new()
            assert not self.__todo_sqs
            self.__deduct()

            if self.__game.state is not GameState.PLAY: return
        
    def __process_new(self):
        ''' Based on the new known squares:
            add/remove equations '''
        while self.__todo_sqs:
            r,c = self.__todo_sqs.pop()
            self.__replace_overlaps(r,c)
            self.__add_around(r,c)

    def __replace_overlaps(self, r:int, c:int):
        add, rm_index = [], []
        e0 = EQN(r,c,1,0)
        for i in self.__store.get_overlap(e0):
            rm_index.append(i)
            e1 = self.__store.get_eqn(i)

            new_mines = e1.mines-1 \
            if self.__game.item_at(r,c) is Item.FLAG else e1.mines

            new_mask = e1.munge(e0, True)
            if not new_mask: continue
            new_eqn = EQN(e1.sr, e1.sc, new_mask, new_mines)
            add.append(new_eqn)

        # possible because rm_index is sorted ascendingly
        while rm_index: self.__store.remove(rm_index.pop())
        while add: self.__store.add(add.pop())

    def __add_around(self, r:int, c:int):
        value = self.__game.item_at(r,c).value
        if value < 0: return

        bit, mask = 1, 0
        mines = value
        for i,j in vicinity(r,c):
            item = self.__game.item_at(i,j)
            if item is Item.FLAG: mines -= 1
            elif item is Item.UNOPEN: mask |= bit
            bit <<= 1

        assert not mask&2**4
        if not mask: return
        new_eqn = EQN(r-1,c-1, mask, mines)
        self.__store.add(new_eqn)

    def __deduct(self):
        ''' Consider equations from todo list:
            open/flag squares if successful '''
        while True:
            e0 = self.__store.fetch()
            if not e0: break
        # BASIC
            # if mines = 0 -> open all
            if e0.mines == 0:
                for r,c in e0.vars_pos: self.__open(r,c)
                return
            # if mines = number of variables -> flag all
            elif e0.mines == bitcnt16(e0.mask):
                for r,c in e0.vars_pos: self.__flag(r,c)
                return

    def __open(self, row:int, col:int):
        assert self.__game.open(row,col, False)
        self.__todo_sqs.append((row,col))

    def __flag(self, row:int, col:int):
        assert self.__game.flag(row,col)
        self.__todo_sqs.append((row,col))