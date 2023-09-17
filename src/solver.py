from game import Game, GameState, Item
from eqn import EQN
from store import Store
from helper import vicinity, bitcnt16

class Solver:
    def __init__(self, game:Game):
        self.__game = game
        self.__store = Store()

    def solve(self):
        if not self.__game.start_coord: return
        self.__store.clear()
        self.__game.restart(False)
        self.__open(*self.__game.start_coord)

        self.__clear = True
        self.__iter()
        if not self.__clear: self.solve()

    def __iter(self):
        while True:
            if self.done: break
            if self.__lcl_deduct(): continue
            if self.__glb_deduct(): continue
            if self.__game.modify(self.__store): continue

            r,c = self.__game.dig()
            assert self.__game.unflag(r,c)
            self.__open(r,c)

            # digging got potential to make the map unsolvable
            # since it modify a known square --> not clear
            self.__clear = False
            break

    def __glb_deduct(self):
        '''Global deduction based on mines left'''
        mines_left = self.__game.mines_left
    # OPEN THE REST
        if mines_left == 0:
            for r,c in self.__game.field_coords:
                if self.__game.item_at(r,c) is Item.UNOPEN:
                    self.__game.open(r,c, False)
            return True

        DEPTH = 13
        eqns = self.__store.get_all()
        if len(eqns) > DEPTH: return False
        squares_left = self.__game.safes_left + mines_left

    # DISJOINT DEDUCTION
        # backtrack to find an disjoint union of equations
        # which leave the mines left = 0 or = remaining squares
        used = [False for _ in range(len(eqns))]
        cursor = 0 # backtrack pointer
        while True:
            if cursor < len(eqns):
                e0 = eqns[cursor]
                ok = True
                # not ok if overlap with an used equation
                for i in range(cursor):
                    if used[i] and e0.munge(eqns[i], False):
                        ok = False
                        break
                if ok:
                    # add to disjoint union
                    mines_left -= e0.mines
                    squares_left -= bitcnt16(e0.mask)
                
                used[cursor] = ok
                cursor += 1
                continue

            # reach the end -> found a disjoint union
            if squares_left > 0 and \
            (mines_left == 0 or mines_left == squares_left):
                # print('-> Union: ')
                # for i,e in enumerate(eqns):
                #     if used[i]: print(e)

                # can open/flag all squares outside the union
                f = self.__open if mines_left == 0 else self.__flag
                for r,c in self.__game.field_coords:
                    if self.__game.item_at(r,c) is Item.UNOPEN: 
                        outside = True
                        e = EQN(r,c,1,0)
                        for i in range(len(eqns)):
                            if used[i] and eqns[i].munge(e, False):
                                outside = False
                                break
                        if outside: f(r,c)
                return True

            cursor -= 1 # why?
            # find the nearest used eqn
            while cursor >= 0 and used[cursor] == 0: cursor-=1
            if cursor < 0: break
            
            # BACKTRACK
            used[cursor] = 0 # unuse the eqn

            # reset mines_left and squares_left
            e0 = eqns[cursor]
            mines_left += e0.mines
            squares_left += bitcnt16(e0.mask)

            cursor += 1
            continue

        return False

    def __lcl_deduct(self):
        '''Process equations from todo list'''
        while True:
            if self.done: return True
            e0 = self.__store.fetch()
            if not e0: return False

            if self.__try_basic(e0): continue
            if self.__try_subtract(e0): continue

    def __try_basic(self, e0:EQN):
        do_sth = True
        # if mines = 0 -> open all
        if e0.mines == 0:
            for r,c in e0.vars_pos: self.__open(r,c)
        # if mines = number of variables -> flag all
        elif e0.mines == bitcnt16(e0.mask):
            for r,c in e0.vars_pos: self.__flag(r,c)
        else: do_sth = False

        return do_sth

    def __try_subtract(self, e0:EQN):
        for i in self.__store.get_overlap(e0):
            e1 = self.__store.get_eqn(i)
            w0 = e0.munge(e1, True)
            w1 = e1.munge(e0, True)

            do_sth = True
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

                # why flag before open ..?
                if flag_eqn and open_eqn:
                    for r,c in flag_eqn.vars_pos: self.__flag(r,c)
                    for r,c in open_eqn.vars_pos: self.__open(r,c)
                else: do_sth = False
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
            else: do_sth = False

            if do_sth: return True

        return False

    def __open(self, row:int, col:int):
        assert self.__game.open(row,col, False)
        self.__process_new(row,col)

    def __flag(self, row:int, col:int):
        assert self.__game.flag(row,col)
        self.__process_new(row,col)

    def __process_new(self, row:int, col:int):
        '''Add/remove equations based on newly known square at row,col'''
        self.__replace_overlaps(row,col)
        self.__add_around(row,col)

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

    @property
    def done(self):
        return self.__game.state is not GameState.PLAY