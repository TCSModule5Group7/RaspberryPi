import sys

import pygame
from pygame.locals import *

from game.Game import Game


class GameController(object):
    FRAMES_PER_SECOND = 60
    RENDER = False

    def __init__(self, useMotion):
        self.game = Game(Game.WIDTH, Game.HEIGHT)
        self.useMotion = useMotion

        self.GameState = enum('STOPPED', 'RUNNING')
        self.state = self.GameState.STOPPED

        # PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.clock = pygame.time.Clock()

    def start(self):
        self.state = self.GameState.RUNNING

    def stop(self):
        self.state = self.GameState.STOPPED

    def reset(self):
        self.game = Game(Game.WIDTH, Game.HEIGHT)

    def loop(self, player_y=-1):
        self.clock.tick(GameController.FRAMES_PER_SECOND)

        # Keyboard Handling
        k_up = 0
        k_down = 0
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            down = event.type == KEYDOWN
            if event.key == K_UP:
                k_up = down * -1
            elif event.key == K_DOWN:
                k_down = down * 1
            elif event.key == K_ESCAPE:
                sys.exit(0)

        # Input Processing
        if not self.useMotion:
            self.game.input(0, k_down + k_up)

        if self.useMotion and not player_y == -1:
            self.game.paddletracking(player_y * Game.HEIGHT)

        # Update the field
        if self.state == self.GameState.RUNNING:
            self.game.update()

        # Render
        if GameController.RENDER:
            pixels = self.game.render()
            pygame.surfarray.blit_array(self.screen, pixels)
            pygame.display.flip()

        # Return gamestate
        return str(float(self.game.computer.pos.y) / Game.HEIGHT) + "/" + str(
            float(self.game.player.pos.y) / Game.HEIGHT) + "/" + str(
            float(self.game.ball.pos.x) / Game.WIDTH) + "/" + str(
            float(self.game.ball.pos.y) / Game.HEIGHT) + "/" + str(
            self.game.computer.score) + "/" + str(self.game.player.score) + "\n"

    def shutdown(self):
        pygame.quit()


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
