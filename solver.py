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
        e0 = EQN(r,c,1,0)
        for i in self.__store.get_overlap(e0):
            e1 = self.__store.get_eqn(i)
            self.__store.remove(i)

            new_mines = e1.mines-1 \
            if self.__game.item_at(r,c) is Item.FLAG else e1.mines

            new_mask = e1.munge(e0, True)
            if not new_mask: continue
            new_eqn = EQN(e1.sr, e1.sc, new_mask, new_mines)
            self.__store.add(new_eqn)

        self.__store.clean()

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

        # SUBTRACT
            for i in self.__store.get_overlap(e0):
                e1 = self.__store.get_eqn(i)
                w0 = e0.munge(e1, True)
                w1 = e1.munge(e0, True)

                if w0 and w1:
                    w0cnt = bitcnt16(w0)
                    w1cnt = bitcnt16(w1)

                    w0_eqn = EQN(e0.sr, e0.sc, w0, 0)
                    w1_eqn = EQN(e1.sr, e1.sc, w1, 0)

                    flag_eqn, open_eqn = None, None
                    if w0cnt == e0.mines-e1.mines:
                        flag_eqn, open_eqn = w0_eqn, w1_eqn
                    elif w1cnt == e1.mines-e0.mines:
                        flag_eqn, open_eqn = w1_eqn, w0_eqn

                    if not (flag_eqn or open_eqn): continue
                    for r,c in flag_eqn.vars_pos: self.__flag(r,c)
                    for r,c in open_eqn.vars_pos: self.__open(r,c)
                    return
                # e1 is subset of e0
                elif w0:
                    sub_mines = e0.mines-e1.mines
                    assert sub_mines >= 0
                    new_eqn = EQN(e0.sr, e0.sc, w0, sub_mines)
                    self.__store.add(new_eqn)
                # e0 is subset of e1
                elif w1:
                    sub_mines = e1.mines-e0.mines
                    assert sub_mines >= 0
                    new_eqn = EQN(e1.sr, e1.sc, w1, sub_mines)
                    self.__store.add(new_eqn)

    def __open(self, row:int, col:int):
        assert self.__game.open(row,col, False)
        self.__todo_sqs.append((row,col))

    def __flag(self, row:int, col:int):
        assert self.__game.flag(row,col)
        self.__todo_sqs.append((row,col))