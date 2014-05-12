from __future__ import print_function

import curses
from datetime import datetime
import time

class Screen(object):
    Q = 1

class CursesScreen(Screen):
    KEY_MAP = {
        Screen.Q: ord('q'),
    }

    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.nodelay(1)
        self.screen.keypad(1)

        self.keybindings = {}

    def __del__(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def draw(self):
        height, width = self.screen.getmaxyx()
        y = int(height / 2)
        x = int(width / 2)

        self.screen.addch(y, x, 'P')
        self.screen.refresh()

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

class Game(object):
    FRAME_RATE = 60

    def __init__(self):
        self.is_running = True
        self.tickers = []
        self.screen = CursesScreen()
        self.screen.on_key_down(Screen.Q, self.stop_running)

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

    game = Game()
    game.run()
