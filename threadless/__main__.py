from __future__ import print_function

import curses
from datetime import datetime
import time

class CursesScreen(object):
    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.nodelay()
        self.screen.keypad(1)

    def __del__(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

class Game(object):
    FRAME_RATE = 60

    def __init__(self):
        self.tickers = []
        self.screen = CursesScreen()

    def run(self):
        sec_per_frame = 1 / 60.0
        is_running   = True

        start = datetime.now()
        while is_running:
            self.screen.draw()
            for ticker in self.tickers:
                ticker()

            end       = datetime.now()
            delta     = end - start
            wait_time = sec_per_frame - (end - start).microseconds * 1000000
            if wait_time > 0:
                time.sleep(wait_time)
            start = end

def main():
    """ your app starts here
    """

    game = Game()
    game.run()
