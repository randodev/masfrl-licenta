import logging
import numpy as np
from copy import copy, deepcopy
from masfrl.engine.display import Display

# Use module logger
logger = logging.getLogger(__name__)


class Environment:
    def __init__(self, x, y, player, actions, specials, walls, walk_reward, initial_score):

        self.x = x
        self.y = y
        self.specials = specials
        self.walls = walls
        self.walk_reward = walk_reward
        self.score = initial_score
        self.max_score = initial_score
        self.reset_score = initial_score
        self.restart = False
        self.actions = actions
        self.show_display = False
        self.hit_wall = 0
        self.log = True

        # Remember previous results
        self.successful = False
        self.previous_result = False

        if not player:
            self.reposition_player()
        else:
            self.orig_player = player
            self.player = deepcopy(self.orig_player)

        # Display
        self.display = Display(
            self.actions,
            self.get_player(),
            self.x,
            self.y,
            self.specials,
            self.walls
        )

    def reposition_player(self, new_player=None):
        if not new_player:
            # Reposition player in a random way
            player = (np.random.randint(self.x), np.random.randint(self.y))
            while player in self.walls:
                player = (np.random.randint(self.x), np.random.randint(self.y))

            self.orig_player = player
            self.player = deepcopy(self.orig_player)
        else:
            self.orig_player = deepcopy(new_player)
            self.player = deepcopy(self.orig_player)

    def get_player(self):
        return self.player

    def get_orig_player(self):
        return deepcopy(self.orig_player)

    def set_cell_score(self, state, action, val):
        if self.show_display:
            self.display.set_cell_score(state, action, val)

    def restart_game(self):
        # Reposition player on the grid
        self.player = (np.random.randint(self.x), np.random.randint(self.y))
        while self.player in self.walls:
            self.player = (np.random.randint(self.x), np.random.randint(self.y))

        # Save maximum score obtained
        if self.score > self.max_score:
            self.max_score = self.score

        # Reset score
        self.score = self.reset_score
        self.restart = False

        # Restart Tkinter display
        if self.show_display:
            self.display.restart_game(self.player)

    def has_restarted(self):
        return self.restart

    def get_max_score(self):
        return self.max_score

    def try_move(self, dx, dy):
        if self.restart:
            self.restart_game()
        new_x = self.player[0] + dx
        new_y = self.player[1] + dy
        self.score += self.walk_reward
        # If the new position fits the requirements
        if (new_x >= 0) and (new_x < self.x) and (new_y >= 0) and (new_y < self.y) and not (
                    (new_x, new_y) in self.walls):
            if self.show_display:
                self.display.update_player(new_x, new_y)
            self.player = (new_x, new_y)
            self.hit_wall = 0
        else:
            self.hit_wall += 1
            if self.hit_wall == 10:
                self.restart = True
                self.hit_wall = 0

        for (i, j, c, w) in self.specials:
            if new_x == i and new_y == j:
                self.score -= self.walk_reward
                self.score += w
                if self.score > 0:
                    if self.log:
                        logger.info("Obtained a positive score : %s" % str(self.score))
                    if self.previous_result:
                        self.successful = True
                    self.previous_result = True
                else:
                    if self.log:
                        logger.error("Obtained a negative score : %s" % str(self.score))
                    self.previous_result = False
                    self.successful = False
                self.restart = True
                self.hit_wall = 0
                return
                # print "score: ", score

    def run_display(self):
        if self.show_display:
            self.display.start_game()

    def stop_display(self):
        if self.show_display:
            self.display.stop_game()


def stringify(environment):
    return {
        "x": environment.x,
        "y": environment.y,
        "player": deepcopy(environment.orig_player),
        "actions": environment.actions,
        "specials": environment.specials,
        "walls": environment.walls,
        "walk_reward": environment.walk_reward,
        "initial_score": environment.reset_score
    }


def stringify_properties(x, y, player, actions, specials, walls, walk_reward, initial_score):
    return {
        "x": x,
        "y": y,
        "player": player,
        "actions": actions,
        "specials": specials,
        "walls": walls,
        "walk_reward": walk_reward,
        "initial_score": initial_score
    }


def unstringify(stringified):
    return Environment(
        stringified['x'],
        stringified['y'],
        stringified['player'],
        stringified['actions'],
        stringified['specials'],
        stringified['walls'],
        stringified['walk_reward'],
        stringified['initial_score']
    )
