from __future__ import print_function

from datetime import datetime
import time

class Game(object):
    FRAME_RATE = 60

    def __init__(self):
        self.tickers = []

    def draw(self):
        pass

    def run(self):
        sec_per_frame = 1 / 60.0
        is_running   = True

        start = datetime.now()
        while is_running:
            self.draw()
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
