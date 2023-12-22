class EQN:
    def __init__(self, sr:int, sc:int, mask:int, mines:int):
        # cannot have 0 or > 9 vars
        assert mask > 0 and mask < 2**9

        # adjust so that sr and sc are
        # min row and col of variables in equation
        while not mask & (1|2|4):
            sr += 1
            mask >>= 3
        while not mask & (1|8|64):
            sc += 1
            mask >>= 1

        self.__sr, self.__sc = sr, sc
        self.__mask = mask

        assert mines >= 0
        self.__mines = mines

    def munge(self, other:'EQN', diff:bool):
        '''Return intersection/difference mask of self vs other'''
        assert isinstance(other, EQN)
        sr, sc, mask = other.sr, other.sc, other.mask

        if abs(sr-self.sr) >= 3 or abs(sc-self.sc) >= 3:
            mask = 0
        else:
            while sc < self.sc:
                mask &= (1|8|64)^511
                mask >>= 1
                sc += 1
            while sc > self.sc:
                mask &= (4|32|256)^511
                mask <<= 1
                sc -= 1
            while sr < self.sr:
                mask &= (1|2|4)^511
                mask >>= 3
                sr += 1
            while sr > self.sr:
                mask &= (64|128|256)^511
                mask <<= 3
                sr -= 1

        if diff: mask ^= 511 # invert
        return self.mask & mask

    @property
    def vars_pos(self):
        bit = 1
        ret:list[tuple[int,int]] = []
        for dr in range(3):
            for dc in range(3):
                if self.mask & bit:
                    ret.append((self.sr+dr, self.sc+dc))
                bit <<= 1

        return ret

    def __eq__(self, other:'EQN'):
        if self.sr == other.sr \
        and self.sc == other.sc \
        and self.mask == other.mask:
            assert self.mines == other.mines
            return True
        return False

    def __str__(self) -> str:
        s = ''
        s += f'pos:{self.sr,self.sc}, '
        s += f'mask:{self.mask:0>9b}, '
        s += f'bombs:{self.mines}'
        return s

    @property
    def sr(self):
        return self.__sr

    @property
    def sc(self):
        return self.__sc

    @property
    def mask(self):
        return self.__mask

    @property
    def mines(self):
        return self.__mines