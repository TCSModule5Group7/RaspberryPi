import sys

from pygame.locals import *

from game.Game import Game


class GameController(object):
    FRAMES_PER_SECOND = 60
    RENDER = True

    def __init__(self, useMotion):
        self.k_up = self.k_down = 0
        self.game = Game(Game.WIDTH, Game.HEIGHT)
        self.useMotion = useMotion

        self.GameState = enum('STOPPED', 'RUNNING')
        self.state = self.GameState.STOPPED

        # PyGame
        import pygame
        self.pygame = pygame
        self.pygame.init()
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

        if not self.useMotion:
            # Keyboard Handling
            for event in self.pygame.event.get():
                if not hasattr(event, 'key'): continue
                down = event.type == KEYDOWN
                if event.key == K_UP:
                    self.k_up = down * -1
                elif event.key == K_DOWN:
                    self.k_down = down * 1
                elif event.key == K_ESCAPE:
                    sys.exit(0)

            # Input Processing
                self.game.input(0, self.k_down + self.k_up)

        if self.useMotion and not player_y == -1:
            self.game.paddletracking(player_y * Game.HEIGHT)

        # Update the field
        if self.state == self.GameState.RUNNING:
            self.game.update()

        # Render
        if GameController.RENDER:
            pixels = self.game.render()
            self.pygame.surfarray.blit_array(self.screen, pixels)
            self.pygame.display.flip()

        # Return gamestate
        return str(float(self.game.computer.pos.y) / Game.HEIGHT) + "/" + str(
            float(self.game.player.pos.y) / Game.HEIGHT) + "/" + str(
            float(self.game.ball.pos.x) / Game.WIDTH) + "/" + str(
            float(self.game.ball.pos.y) / Game.HEIGHT) + "/" + str(
            self.game.computer.score) + "/" + str(self.game.player.score) + "\n"

    def shutdown(self):
        self.pygame.quit()


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
