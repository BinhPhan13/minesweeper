from game import Game, Mode
from view import GameView
from __init__ import EXE_DIR
from helper import sec2min

import json
from tkinter import *
from tkinter import font
from collections import OrderedDict

MODES = OrderedDict([
    ('Easy', Mode(9,9, 10)),
    ('Medium', Mode(16,16, 40)),
    ('Hard', Mode(16,30, 99)),
    ('Expert', Mode(20,30, 180)),
])
RECORDS_FILE = EXE_DIR + 'src/records.json'

class GUI:
    def __init__(self):
        self._load_records()
        self._root = Tk()
        self._root.resizable(False,False)
        self._root.title('Mines')
        self._root.bind('s', lambda _: self._solve())

        self._mainframe = Frame(self._root)
        self._mainframe.pack()

        self._build_menu()
        self._build_config()
        self._build_game()

    def _build_menu(self):
        menubar = Frame(self._mainframe)
        menubar.pack(fill=X, expand=True)

        self._mode_button = Button(menubar,
            text='Mode',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
            command=self._choose_mode
        )
        self._mode_button.grid(row=0, column=0)

        self._newgame_button = Button(menubar,
            text='New game',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
            command=self._newgame
        )
        self._newgame_button.grid(row=0, column=1)

        Button(menubar,
            text='Records',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
            command=self._show_records
        ).grid(row=0, column=2)

        Button(menubar,
            text='Exit',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
            command=self._exit
        ).grid(row=0, column=3)

    def _build_config(self):
        self._config_frame = Frame(self._root)

        titles = [s.capitalize() for s in Mode.ATTRS]
        for j, title in enumerate(titles):
            Label(self._config_frame, bg='#d0d0d0',
                text=title, width=8,
            ).grid(row=0, column=j+1, sticky=NSEW)

        # modes
        self._choice = StringVar(value='Easy')
        for i, mode in enumerate(MODES):
            Radiobutton(self._config_frame,
                anchor=W, width=8,
                text=mode,
                value=mode,
                variable=self._choice,
            ).grid(row=i+1, column=0, sticky=NSEW)

            for j, attr in enumerate(Mode.ATTRS):
                v = getattr(MODES[mode], attr)
                widget = Label(self._config_frame, text=v)
                widget.configure(bg='white')
                widget.grid(row=i+1, column=j+1, sticky=NSEW)

        Button(self._config_frame,
            text='OK', bg='#a0a0a0',
            font=font.Font(size=10, weight=font.BOLD),
            activebackground='#a0a0a0',
            relief=FLAT,
            command=self._set_mode
        ).grid(row=0, column=0, sticky=NSEW)

        Label(self._config_frame, bg='#d0d0d0',
        ).grid(
            row=len(MODES)+1, column=0,
            columnspan=len(Mode.ATTRS)+1,
            sticky=NSEW
        )

    def _build_game(self):
        mode = self._choice.get()

        self._game = Game(MODES[mode])
        self._gameview = GameView(
            self._mainframe, self._game,
            self._records[mode]
        )
        self._game.setview(self._gameview)
        self._gameview.pack()

    def _newgame(self):
        self._gameview.reset()

    def _choose_mode(self):
        self._mainframe.forget()
        self._config_frame.pack()

    def _set_mode(self):
        self._config_frame.forget()
        self._mainframe.pack()

        self._gameview.destroy()
        self._build_game()

    def _load_records(self):
        try:
            f = open(RECORDS_FILE)
            self._records = json.load(f)
            f.close()
        except FileNotFoundError:
            self._records = {mode:[] for mode in MODES}

    def _dump_records(self):
        # trim to 20 records each mode
        for mode_records in self._records.values():
            mode_records = mode_records[:20]

        with open(RECORDS_FILE, 'w') as f:
            json.dump(self._records, f, indent=2)

    def _show_records(self):
        mode = self._choice.get()
        mode_records = self._records[mode]

        top = Toplevel(self._root, bg='red')
        top.title(f'{mode} records')
        top.resizable(False, False)

        h, w = 10, 2
        for j in range(w):
            for i in range(h):
                label = Label(top, width=30,
                    highlightthickness=1,
                    highlightbackground='#a0a0a0',
                )
                label.grid(row=i, column=j)

                index = i+j*h
                if index >= len(mode_records): continue

                text = f'{index+1:0>2}. '
                date, playtime = mode_records[index]
                display_time = sec2min(playtime)
                text += f'{date:15}{display_time}'

                label.config(text=text, anchor=W,
                    font=font.Font(size=10)
                )

    def _solve(self):
        from solver import Solver
        s = Solver(self._game, sleep_time=0.1)
        s.solve()

    def start(self):
        self._root.mainloop()

    def _exit(self):
        self._dump_records()
        self._root.destroy()