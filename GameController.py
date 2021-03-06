from game.Game import *
import time


class GameController(object):
    FRAMES_PER_SECOND = 15
    RENDER = False

    def __init__(self, useMotion, score_callback):
        self.k_up = self.k_down = 0
        self.game = Game(WIDTH, HEIGHT, score_callback)
        self.useMotion = useMotion

        self.GameState = enum('STOPPED', 'RUNNING')
        self.state = self.GameState.STOPPED
        self.resetting = False

        # PyGame
        # import pygame
        # self.pygame = pygame
        # self.pygame.init()
        # if GameController.RENDER:
        #     self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # self.clock = pygame.time.Clock()

    def start(self):
        self.state = self.GameState.RUNNING

    def stop(self):
        self.state = self.GameState.STOPPED

    def reset(self):
        self.resetting = True

    def loop(self, delta, player_y=-1):
        time.sleep(1 / GameController.FRAMES_PER_SECOND)
        if self.resetting:
            self.game = Game(WIDTH, HEIGHT)
            self.resetting = False

        # if not self.useMotion:
        #     # Keyboard Handling
        #     for event in self.pygame.event.get():
        #         if not hasattr(event, 'key'): continue
        #         down = event.type == KEYDOWN
        #         if event.key == K_UP:
        #             self.k_up = down * -1
        #         elif event.key == K_DOWN:
        #             self.k_down = down * 1
        #         elif event.key == K_ESCAPE:
        #             sys.exit(0)
        #
        #     # Input Processing
        #     self.game.input(0, self.k_down + self.k_up)

        if self.useMotion and not player_y == -1:
            self.game.paddletracking(player_y * HEIGHT)

        # Update the field
        if self.state == self.GameState.RUNNING:
            self.game.update(delta)

        # Render
        # if GameController.RENDER:
        #     pixels = self.game.render()
        #     self.pygame.surfarray.blit_array(self.screen, pixels)
        #     self.pygame.display.flip()

        # Return gamestate
        return str(float(self.game.computer.pos.y) / HEIGHT) + "/" + str(
            float(self.game.player.pos.y) / HEIGHT) + "/" + str(
            float(self.game.ball.pos.x) / WIDTH) + "/" + str(
            float(self.game.ball.pos.y) / HEIGHT) + "/" + str(
            self.game.computer.score) + "/" + str(self.game.player.score) + "\n"

        # def shutdown(self):
        #     self.pygame.quit()

    def get_gamestate(self):
        return str(float(self.game.computer.pos.y) / HEIGHT) + "/" + str(
            float(self.game.player.pos.y) / HEIGHT) + "/" + str(
            float(self.game.ball.pos.x) / WIDTH) + "/" + str(
            float(self.game.ball.pos.y) / HEIGHT) + "/" + str(
            self.game.computer.score) + "/" + str(self.game.player.score) + "\n"


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
