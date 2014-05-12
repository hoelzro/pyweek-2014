from __future__ import print_function

import curses
from datetime import datetime
import sys
import time

class Positional(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getpos(self):
        return self.x, self.y

    # XXX screen boundaries
    def move_down(self):
        self.y += 1

    def move_up(self):
        self.y -= 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

class Player(Positional):
    pass

class Screen(object):
    Q = 1
    J = 2
    K = 3
    H = 4
    L = 5

class CursesScreen(Screen):
    KEY_MAP = {
        Screen.Q: ord('q'),
        Screen.J: ord('j'),
        Screen.K: ord('k'),
        Screen.H: ord('h'),
        Screen.L: ord('l'),
    }

    CHAR_FOR_TYPE = {
        Player: 'P'
    }

    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.nodelay(1)
        self.screen.keypad(1)

        self.keybindings = {}
        self.objects = []

    def __del__(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def draw(self):
        self.screen.erase()
        for obj in self.objects:
            x, y = obj.getpos()
            c    = self.CHAR_FOR_TYPE[type(obj)]
            self.screen.addch(y, x, c)
        self.screen.refresh()

    def get_size(self):
        height, width = self.screen.getmaxyx()
        return width, height

    def on_key_down(self, key, callback):
        key = self.KEY_MAP[key]
        if key not in self.keybindings:
            self.keybindings[key] = []
        self.keybindings[key].append(callback)

    def process_input(self):
        ch = self.screen.getch()

        if ch != -1:
            callbacks = self.keybindings.get(ch, [])
            for cb in callbacks:
                cb()

    def add_object(self, obj):
        self.objects.append(obj)

class Game(object):
    FRAME_RATE = 60

    def __init__(self):
        self.is_running = True
        self.tickers = []
        self.screen = CursesScreen()

        width, height = self.screen.get_size()
        x = int(width / 2)
        y = int(height / 2)
        self.player = Player(x, y)
        self.screen.add_object(self.player)

        self.screen.on_key_down(Screen.Q, self.stop_running)
        self.screen.on_key_down(Screen.J, self.player.move_down)
        self.screen.on_key_down(Screen.K, self.player.move_up)
        self.screen.on_key_down(Screen.H, self.player.move_left)
        self.screen.on_key_down(Screen.L, self.player.move_right)

        self.tickers.append(self.screen.process_input)

    def run(self):
        sec_per_frame = 1 / 60.0

        start = datetime.now()
        while self.is_running:
            self.screen.draw()
            for ticker in self.tickers:
                ticker()

            end       = datetime.now()
            delta     = end - start
            wait_time = sec_per_frame - (end - start).microseconds * 1000000
            if wait_time > 0:
                time.sleep(wait_time)
            start = end

    def stop_running(self):
        self.is_running = False

def main():
    """ your app starts here
    """

    try:
        game = Game()
        game.run()
    except Exception, e:
        print(sys.exc_info())
        print(str(e))
