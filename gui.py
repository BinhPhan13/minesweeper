from game import Game, Mode
from view import GameView
from tkinter import *
from tkinter import font
from collections import OrderedDict

MODES = OrderedDict([
    ('Easy', Mode(9,9, 10)),
    ('Medium', Mode(16,16, 40)),
    ('Hard', Mode(16,30, 99)),
    ('Expert', Mode(20,30, 150)),
])

class GUI:
    def __init__(self):
        self.__root = Tk()
        self.__root.resizable(False,False)
        self.__root.title('Mines')

        self.__mainframe = Frame(self.__root)
        self.__mainframe.pack()

        self.__build_menu()
        self.__build_config()

        self.__mode = MODES['Easy']
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

        blah = Button(menubar,
            text='Records',
            font=font.Font(size=10, weight=font.BOLD),
            relief=FLAT,
        )
        blah.grid(row=0, column=2)

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
            text='OK', bg='#c0c0c0',
            font=font.Font(size=10, weight=font.BOLD),
            activebackground='#c0c0c0',
            relief=FLAT,
            command=self.__set_mode
        ).grid(row=0, column=0, sticky=NSEW)

    def __build_game(self):
        self.__game = Game(self.__mode)
        self.__gameview = GameView(self.__mainframe, self.__game)
        self.__game.setview(self.__gameview)
        self.__gameview.pack()

    def __newgame(self):
        self.__game.restart()
        self.__gameview.adjust_stt()

    def __choose_mode(self):
        self.__mainframe.forget()
        self.__config_frame.pack()

    def __set_mode(self):
        self.__config_frame.forget()
        self.__mainframe.pack()

        mode = MODES[self.__choice.get()]
        if mode == self.__mode: self.__newgame()
        else:
            self.__mode = mode
            self.__gameview.destroy()
            self.__build_game()

    def start(self):
        self.__root.mainloop()