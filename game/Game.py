import math
import random
import sys

import numpy as np
import pygame
from pygame.locals import *

import physics.Collision as collision
from Ball import Ball
from Paddle import Paddle
from Wall import Wall
from physics.Manifold import Manifold
from physics.Vec2 import Vec2

from Connector import Connector

import socket

ACCELERATION = 10
BALL_SPEED = 10


class Game:
    WIDTH = 1080
    HEIGHT = 720

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = np.zeros((Game.WIDTH, Game.HEIGHT))

        self.paddle1 = Paddle(100, 360)
        self.paddle2 = Paddle(980, 360)
        self.bal = Ball(920, 360)
        self.bal.velocity = Vec2(-1, -1)
        self.wall_north = Wall(540, 0, 1080, 20)
        self.wall_east = Wall(1080, 360, 20, 720)
        self.wall_south = Wall(540, 720, 1080, 20)
        self.wall_west = Wall(0, 360, 20, 720)

        self.entities = [self.paddle1, self.paddle2, self.bal, self.wall_north, self.wall_east, self.wall_south,
                         self.wall_west]

    def input(self, dx, dy):
        self.paddle2.velocity = Vec2(ACCELERATION * dx, ACCELERATION * dy)

        if not (0 < self.paddle2.pos.y - self.paddle2.shape.height / 2 + self.paddle2.velocity.y) or not (
                            self.paddle2.pos.y + self.paddle2.shape.height / 2 + self.paddle2.velocity.y < Game.HEIGHT):
            self.paddle2.velocity = Vec2(0, 0)

    def update(self):
        for entity in self.entities:
            if entity == self.bal:
                continue
            manifold = Manifold(self.bal, entity)
            if collision.aabb_vs_aabb(manifold):
                collision.resolve_collision(manifold)
                # Transfer momentum
                if isinstance(entity, Paddle):
                    vel_dir = self.bal.velocity / Vec2(BALL_SPEED, BALL_SPEED)
                    ratio = 1 / vel_dir.y
                    self.bal.velocity.y *= random.uniform(-ratio, ratio)

                # Check for point
                if entity == self.wall_east or entity == self.wall_west:
                    self.add_point()

                # Set paddle velocity to zero, preventing the ball from being pushed out
                entity.collision_callback()

        # Give ball minimum speed
        ratio = BALL_SPEED / math.sqrt(math.pow(self.bal.velocity.x, 2) + math.pow(self.bal.velocity.y, 2))
        if ratio > 1:
            self.bal.velocity.x *= ratio + 0.01
            self.bal.velocity.y *= ratio + 0.01

        for entity in self.entities:
            entity.update()

    def render(self):
        self.pixels = np.zeros((Game.WIDTH, Game.HEIGHT))

        for entity in self.entities:
            self.pixels = entity.render(self)

        return self.pixels

    def add_point(self):
        if self.bal.pos.x < Game.WIDTH / 2:
            self.paddle1.add_point()
            self.bal.pos = Vec2(540,360)
        else:
            self.paddle2.add_point()
            self.bal.pos = Vec2(540,360)
        print self.get_score()

    def get_score(self):
        return [self.paddle1.score, self.paddle2.score]


class Controller:
    FRAMES_PER_SECOND = 30

    def __init__(self):
        self.k_up = self.k_down = 0
        self.field = Game(Game.WIDTH, Game.HEIGHT)

        # Connector that sends data to the visualization
        self.useConnector = True
        try:
            self.connector = Connector("localhost",420)
            self.connector.connect()
        except socket.error:
            self.useConnector = False

        # PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.clock = pygame.time.Clock()

        # Loop
        while 1:
            self.loop()

    def loop(self):
        self.clock.tick(60)

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
        self.field.input(0, self.k_up + self.k_down)

        # Update the field
        self.field.update()

        # Send gamestate to visualization
        if self.useConnector:
            self.connector.update(float(self.field.paddle1.pos.y)/Game.HEIGHT,
                                  float(self.field.paddle2.pos.y)/Game.HEIGHT,
                                  float(self.field.bal.pos.x)/Game.WIDTH,
                                  float(self.field.bal.pos.y)/Game.HEIGHT,
                                  self.field.paddle1.score,
                                  self.field.paddle2.score)

        # Render
        pixels = self.field.render()
        pygame.surfarray.blit_array(self.screen, pixels)
        pygame.display.flip()


Controller()
