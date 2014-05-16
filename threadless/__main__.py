from __future__ import print_function

from abc import abstractmethod, ABCMeta
import curses
import logging
import math
import operator
import random
import time

logging.basicConfig(filename='threadless.log', level=logging.DEBUG)

class YoureDead(Exception):
    def __init__(self):
        super(Exception, self).__init__("You're dead! =(")

class Positional(object):
    def __init__(self, x, y, movement_checker):
        self.x                = x
        self.y                = y
        self.movement_checker = movement_checker

    def getpos(self):
        return self.x, self.y

    def move_down(self):
        self.move_rel(0, 1)

    def move_up(self):
        self.move_rel(0, -1)

    def move_left(self):
        self.move_rel(-1, 0)

    def move_right(self):
        self.move_rel(1, 0)

    def move_rel(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if self.movement_checker.permit_movement(self, new_x, new_y):
            self.x = new_x
            self.y = new_y


# XXX superclass isn't quite right, but whatever
class StoneBlock(Positional):
    pass

class Player(Positional):
    pass

class Enemy(Positional):
    MEMORY_LENGTH = 5
    BACKTRACK_PENALTY = 5
    MOMENTUM_BONUS = 1

    def __init__(self, *args, **kwargs):
        super(Enemy, self).__init__(*args, **kwargs)
        self.previous_positions = []

    def move_rel(self, dx, dy):
        current_position = self.getpos()
        self.previous_positions.append(current_position)
        if len(self.previous_positions) > self.MEMORY_LENGTH:
            self.previous_positions.pop(0)
        super(Enemy, self).move_rel(dx, dy)

    def calculate_next_move(self):
        x, y = self.getpos()
        player_x, player_y = self.movement_checker.player.getpos() # XXX not ideal
        possible_moves = [
            [x + dx, y + dy, 0] for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
        ]
        possible_moves = [ move for move in possible_moves if self.movement_checker.permit_movement(self, move[0], move[1]) ]

        if not possible_moves:
            return None

        for move in possible_moves:
            new_x, new_y, score = move
            score = math.sqrt(abs(new_x - player_x) ** 2 + abs(new_y - player_y) ** 2)

            if self.previous_positions:
                previous_position = self.previous_positions[-1]
                dx = abs(previous_position[0] - new_x)
                dy = abs(previous_position[1] - new_y)

                if dx == 2 or dy == 2:
                    score -= self.MOMENTUM_BONUS

            for prev_x, prev_y in self.previous_positions:
                if new_x == prev_x and new_y == prev_y:
                    score += self.BACKTRACK_PENALTY
                    break # we might weight positions further back differently
            move[2] = score
        best_move = min(possible_moves, key=operator.itemgetter(2))
        return best_move[0:2]

class Screen(object):
    Q = 1
    J = 2
    K = 3
    H = 4
    L = 5
    W = 6
    A = 7
    S = 8
    D = 9
    E = 10

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
        Screen.A: ord('a'),
        Screen.D: ord('d'),
        Screen.E: ord('e'),
        Screen.H: ord('h'),
        Screen.J: ord('j'),
        Screen.K: ord('k'),
        Screen.L: ord('l'),
        Screen.Q: ord('q'),
        Screen.S: ord('s'),
        Screen.W: ord('w'),
    }

    CHAR_FOR_TYPE = {
        Player:      'P',
        Enemy:       'E',
        StoneBlock:  'X',
    }

    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.nodelay(1)
        self.screen.keypad(1)
        self.cursor_state = curses.curs_set(0)

        self.keybindings = {}
        self.objects = []

    def teardown(self):
        curses.curs_set(self.cursor_state)
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


FRAME_RATE = 60.0

class Game(object):
    def __init__(self):
        self.is_running = True
        self.tickers = [
            # (ticker, tick_delay)
        ]
        self.screen = CursesScreen()

        width, height = self.screen.get_size()
        x = int(width / 2)
        y = int(height / 2)
        self.player = Player(x, y, self)
        self.screen.add_object(self.player)

        self.enemies = []
        self.blocks  = []

        self.screen.on_key_down(Screen.Q, self.stop_running)
        self.screen.on_key_down(Screen.S, self.player.move_down)
        self.screen.on_key_down(Screen.W, self.player.move_up)
        self.screen.on_key_down(Screen.A, self.player.move_left)
        self.screen.on_key_down(Screen.D, self.player.move_right)
        self.screen.on_key_down(Screen.E, self.place_block)

        self.add_ticker(self.screen.process_input)
        self.add_ticker(self.move_enemies, every=1/3.0)
        self.add_ticker(self.spawn_enemies, every=60)
        self.add_ticker(self.check_for_player_death)

    def teardown(self):
        self.screen.teardown()

    def run(self):
        seconds_per_frame = 1 / FRAME_RATE

        tick = 0
        while self.is_running:
            start = time.time()
            tick += 1
            self.screen.draw()
            for ticker, tick_delay in self.tickers:
                if tick % tick_delay == 0:
                    ticker()

            end       = time.time()
            wait_time = seconds_per_frame - (end - start)
            if wait_time > 0:
                time.sleep(wait_time)

    def stop_running(self):
        self.is_running = False

    def move_enemies(self):
        player_x, player_y = self.player.getpos()
        for enemy in self.enemies:
            enemy_x, enemy_y = enemy.getpos()
            next_move = enemy.calculate_next_move()
            if next_move:
                enemy.move_rel(next_move[0] - enemy_x, next_move[1] - enemy_y)

    def add_ticker(self, ticker, every=1/FRAME_RATE):
        assert every != 0
        self.tickers.append((ticker, every * FRAME_RATE))

    def spawn_enemies(self):
        width, height = self.screen.get_size()
        for i in range(0, 10):
            side = random.randint(0, 3)

            # for some reason, (width - 1, height - 1) as coordinates don't work, so
            # we use width - 2
            if side == 0:
                x = random.randint(0, width - 2)
                y = 0
            elif side == 1:
                x = width - 1
                y = random.randint(0, height - 1)
            elif side == 2:
                x = random.randint(0, width - 2)
                y = height - 1
            elif side == 3:
                x = 0
                y = random.randint(0, height - 1)

            enemy = Enemy(x, y, self)
            self.enemies.append(enemy)
            self.screen.add_object(enemy)

    def check_for_player_death(self):
        player_x, player_y = self.player.getpos()

        for enemy in self.enemies:
            enemy_x, enemy_y = enemy.getpos()

            if player_x == enemy_x and player_y == enemy_y:
                raise YoureDead()

    def place_block(self):
        x, y = self.player.getpos()
        width, height = self.screen.get_size()
        block = StoneBlock(x + 1, y, self)
        self.blocks.append(block)
        self.screen.add_object(block)

    def permit_movement(self, obj, x, y):
        width, height = self.screen.get_size()

        if x < 0 or x >= width - 1:
            return False

        if y < 0 or y >= height:
            return False

        for block in self.blocks:
            block_x, block_y = block.getpos()

            if x == block_x and y == block_y:
                return False

        return True

def main():
    """ your app starts here
    """

    try:
        game = Game()
        try:
            game.run()
        finally:
            game.teardown()
    except YoureDead, _:
        print("You're dead! =(")
