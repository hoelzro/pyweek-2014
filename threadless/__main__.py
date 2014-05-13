from __future__ import print_function

from abc import abstractmethod, ABCMeta
import atexit
import curses
import sys
import time


class Positional(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.MAX_X = width
        self.MAX_Y = height

    def getpos(self):
        return self.x, self.y

    def move_down(self):
        if self.y < self.MAX_Y - 1:
            self.y += 1

    def move_up(self):
        if self.y > 0:
            self.y -= 1

    def move_left(self):
        if self.x > 0:
            self.x -= 1

    def move_right(self):
        if self.x < self.MAX_X - 2:
            self.x += 1

    def move_rel(self, dx, dy):
        if 0 <= self.x + dx < self.MAX_X - 2:
            self.x += dx
        if 0 <= self.y + dy < self.MAX_Y - 1:
            self.y += dy


class Player(Positional):
    pass


class Enemy(Positional):
    pass


class Screen(object):
    Q = 1
    J = 2
    K = 3
    H = 4
    L = 5

    __metaclass__ = ABCMeta

    @abstractmethod
    def draw(self):
        '''
            Draws things on the screen.
        '''
        pass

    @abstractmethod
    def get_size(self):
        '''
            Returns the width and height of the screen.
        '''
        pass

    @abstractmethod
    def on_key_down(self, key, callback):
        '''
            Sets up a callback to be called when the given key is pressed.  Key constants
            from Screen should be used, and may be translated by this method implemention
            into native key codes.
        '''
        pass

    @abstractmethod
    def process_input(self):
        '''
            Processes any pending input events.
        '''
        pass

    @abstractmethod
    def add_object(self, obj):
        '''
            Adds a Positional object to the screen for drawing.  The object may lie outside
            of the screen boundaries.
        '''
        pass

    def teardown(self):
        pass


class CursesScreen(Screen):
    KEY_MAP = {
        Screen.Q: ord('q'),
        Screen.J: ord('j'),
        Screen.K: ord('k'),
        Screen.H: ord('h'),
        Screen.L: ord('l'),
    }

    CHAR_FOR_TYPE = {
        Player: 'P',
        Enemy:  'E',
    }

    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.nodelay(1)
        self.screen.keypad(1)

        self.keybindings = {}
        self.objects = []

    def teardown(self):
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
        self.tickers = [
            # (ticker, tick_delay)
        ]
        self.screen = CursesScreen()

        width, height = self.screen.get_size()
        x = int(width / 2)
        y = int(height / 2)
        self.player = Player(x, y, width, height)
        self.screen.add_object(self.player)

        self.enemies = [ Enemy(0, 0, width, height) ]
        for enemy in self.enemies:
            self.screen.add_object(enemy)

        self.screen.on_key_down(Screen.Q, self.stop_running)
        self.screen.on_key_down(Screen.J, self.player.move_down)
        self.screen.on_key_down(Screen.K, self.player.move_up)
        self.screen.on_key_down(Screen.H, self.player.move_left)
        self.screen.on_key_down(Screen.L, self.player.move_right)

        self.tickers.append((self.screen.process_input, 1))
        self.tickers.append((self.move_enemies, 20))

    def teardown(self):
        self.screen.teardown()

    def run(self):
        frames_per_second = 60.0
        seconds_per_frame = 1 / frames_per_second

        # ticks_per_second:
        # 1 -> 60
        # 2 -> 30
        # 3 -> 20
        # 4 -> 15
        # 5 -> 12
        # 6 -> 10
        # 60 -> 1

        start = time.time()
        tick = 0
        while self.is_running:
            tick = (tick + 1) % 60
            self.screen.draw()
            for ticker, tick_delay in self.tickers:
                if tick % tick_delay == 0:
                    ticker()

            end       = time.time()
            delta     = end - start
            wait_time = seconds_per_frame - (end - start)
            if wait_time > 0:
                time.sleep(wait_time)
            start = end

    def stop_running(self):
        self.is_running = False

    def move_enemies(self):
        player_x, player_y = self.player.getpos()
        for enemy in self.enemies:
            enemy_x, enemy_y = enemy.getpos()
            dx = player_x - enemy_x
            dy = player_y - enemy_y

            if dx < dy:
                enemy.move_rel(0, -1 if dy < 0 else 1)
            else:
                enemy.move_rel(-1 if dx < 0 else 1, 0)

def main():
    """ your app starts here
    """

    try:
        game = Game()
        game.run()
    except Exception, e:
        print(sys.exc_info())
        print(str(e))
    finally:
        game.teardown()
