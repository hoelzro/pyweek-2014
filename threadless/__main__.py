from __future__ import print_function

import curses
from datetime import datetime
import time

class Player(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getpos(self):
        return self.x, self.y

    # XXX screen boundaries
    def move_down(self):
        self.y += 1

class Screen(object):
    Q = 1
    J = 2

class CursesScreen(Screen):
    KEY_MAP = {
        Screen.Q: ord('q'),
        Screen.J: ord('j'),
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
        self.screen.on_key_down(Screen.Q, self.stop_running)
        self.screen.on_key_down(Screen.J, self.move_down)
        width, height = self.screen.get_size()
        x = int(width / 2)
        y = int(height / 2)
        self.player = Player(x, y)
        self.screen.add_object(self.player)

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

    def move_down(self):
        self.player.move_down()

def main():
    """ your app starts here
    """

    game = Game()
    game.run()
