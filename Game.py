import sys

import numpy as np
import pygame
from pygame.locals import *


class Field:
    WIDTH = 1080
    HEIGHT = 720
    ACCELERATION = 10

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = np.zeros((Field.WIDTH, Field.HEIGHT))

        self.paddle1 = Paddle(100, 360)
        self.paddle2 = Paddle(980, 360)
        self.bal = Bal(540, 360)
        self.entities = [self.paddle1, self.paddle2, self.bal]

        self.bal.start()

    def update(self, dx, dy):
        self.paddle1.move(Field.ACCELERATION * dx, Field.ACCELERATION * dy)

        for entity in self.entities:
            entity.update(self)

    def render(self):
        self.pixels = np.zeros((Field.WIDTH, Field.HEIGHT))

        for entity in self.entities:
            self.pixels = entity.render(self)

        return self.pixels


class Entity:
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0

    def update(self, field):
        self.x += self.dx
        self.y += self.dy
        self.dx = 0
        self.dy = 0

    def render(self, field):
        for x in range(self.width):
            for y in range(self.height):
                # if y + self.y - self.height / 2 >= Field.HEIGHT: continue
                # if x + self.x - self.width / 2 >= Field.WIDTH: continue
                field.pixels[
                    (x + self.x - self.width / 2) % Field.WIDTH, (y + self.y - self.height / 2) % Field.HEIGHT] = 255

        return field.pixels


class Paddle(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, 50, 200)

    def move(self, dx, dy):
        self.dy += dy

    def update(self, field):
        if (0 < self.y - self.height / 2 + self.dy) and (self.y + self.height / 2 + self.dy < Field.HEIGHT):
            Entity.update(self, field)
        else:
            self.dy = 0


class Bal(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, 40, 40)

    def start(self):
        self.dx = 5
        self.dy = 5

    def update(self, field):
        for entity in field.entities:
            if entity == self: continue
            if abs(entity.x - self.x) * 2 < (entity.width + self.width) and abs(entity.y - self.y) * 2 < (
                        entity.height + self.height):
                self.dx *= -1
                self.dy *= -1
            if self.x + self.width / 2 >= Field.WIDTH or self.x - self.width / 2 <= 0:
                self.dx *= -1
            if self.y + self.height / 2 >= Field.HEIGHT or self.y - self.height / 2 <= 0:
                self.dy *= -1

            self.x += self.dx
            self.y += self.dy


class Game:
    FRAMES_PER_SECOND = 30

    def __init__(self):
        self.k_up = self.k_down = 0
        self.field = Field(Field.WIDTH, Field.HEIGHT)

        # PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((1080, 720))
        self.clock = pygame.time.Clock()

        # Loop
        while 1:
            self.loop()

    def loop(self):
        self.clock.tick(30)

        # Input Handling
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            down = event.type == KEYDOWN
            if event.key == K_UP:
                self.k_up = down * -1
            elif event.key == K_DOWN:
                self.k_down = down * 1
            elif event.key == K_ESCAPE:
                sys.exit(0)

        # Update the field
        self.field.update(0, self.k_up + self.k_down)

        # Render
        pixels = self.field.render()
        pygame.surfarray.blit_array(self.screen, pixels)
        pygame.display.flip()


Game()
