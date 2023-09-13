from game import Game, Mode
from view import GameView
from __init__ import EXE_DIR

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
        self.__load_records()
        self.__root = Tk()
        self.__root.resizable(False,False)
        self.__root.title('Mines')

        self.__mainframe = Frame(self.__root)
        self.__mainframe.pack()

        self.__build_menu()
        self.__build_config()

        self.__build_game()

    def __build_menu(self):
        menubar = Frame(self.__mainframe)
        menubar.pack(fill=X, expand=True)

        self.__mode_button = Button(menubar,
            text='Mode',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
            command=self.__choose_mode
        )
        self.__mode_button.grid(row=0, column=0)
        self.__newgame_button = Button(menubar,
            text='New game',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
            command=self.__newgame
        )
        self.__newgame_button.grid(row=0, column=1)

        Button(menubar,
            text='Records',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
            command=self.__show_records
        ).grid(row=0, column=2)

        Button(menubar,
            text='Exit',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
            command=self.__exit
        ).grid(row=0, column=3)

    def __build_config(self):
        self.__config_frame = Frame(self.__root)
        
        titles = [s.capitalize() for s in Mode.ATTRS]
        for j, title in enumerate(titles):
            Label(self.__config_frame, bg='#d0d0d0',
                text=title, width=8,
            ).grid(row=0, column=j+1, sticky=NSEW)

        # modes
        self.__choice = StringVar(value='Easy')
        for i, description in enumerate(MODES):
            Radiobutton(self.__config_frame,
                anchor=W, width=8,
                text=description,
                value=description,
                variable=self.__choice,
            ).grid(row=i+1, column=0, sticky=NSEW)

            for j, attr in enumerate(Mode.ATTRS):
                v = getattr(MODES[description], attr)
                widget = Label(self.__config_frame, text=v)
                widget.configure(bg='white')
                widget.grid(row=i+1, column=j+1, sticky=NSEW)

        Button(self.__config_frame,
            text='OK', bg='#a0a0a0',
            font=font.Font(size=10, weight=font.BOLD),
            activebackground='#a0a0a0',
            relief=FLAT,
            command=self.__set_mode
        ).grid(row=0, column=0, sticky=NSEW)

        Label(self.__config_frame, bg='#d0d0d0',
        ).grid(
            row=len(MODES)+1, column=0,
            columnspan=len(Mode.ATTRS)+1,
            sticky=NSEW
        )

    def __build_game(self):
        mode = self.__choice.get()

        self.__game = Game(MODES[mode])
        self.__gameview = GameView(
            self.__mainframe, self.__game,
            self.__records[mode]
        )
        self.__game.setview(self.__gameview)
        self.__gameview.pack()

    def __newgame(self):
        self.__gameview.reset()

    def __choose_mode(self):
        self.__mainframe.forget()
        self.__config_frame.pack()

    def __set_mode(self):
        self.__config_frame.forget()
        self.__mainframe.pack()

        self.__gameview.destroy()
        self.__build_game()

    def __load_records(self):
        try:
            f = open(RECORDS_FILE, 'r')
            records:dict[str,list] = json.loads(f.readline())
            f.close()
        except FileNotFoundError: records = {mode:[] for mode in MODES}
        self.__records = records
    
    def __dump_records(self):
        # trim records to 20 each (suitable to show records)
        for k in self.__records:
            record = self.__records[k]
            record = record[:20]

        f = open(RECORDS_FILE, 'w')
        f.write(json.dumps(self.__records))
        f.close()

    def __show_records(self):
        mode = self.__choice.get()
        record = self.__records[mode]

        top = Toplevel(self.__root, bg='red')
        top.title(f'{mode} records')
        top.resizable(False, False)

        h, w = 10, 2
        for j in range(w):
            for i in range(h):
                label = Label(top, width=20,
                    highlightthickness=1,
                    highlightbackground='#a0a0a0',
                )
                label.grid(row=i, column=j)

                index = i+j*h
                text = f'{index+1:0>2}. '
                try:
                    date, playtime = record[index]
                    from view import Timer
                    display_time = Timer.sec2min(playtime)
                    text += f'{date:15}{display_time}'
                except: pass

                label.config(text=text, anchor=W,
                    font=font.Font(size=10)
                )

    def start(self):
        self.__root.mainloop()
    
    def __exit(self):
        self.__dump_records()
        self.__root.destroy()