import itertools
import math
import socket
import sys

import numpy as np
import pygame
from pygame.locals import *

import physics.Collision as collision
from Ball import Ball
from ComputerPaddle import ComputerPaddle
from Connector import Connector
from Paddle import Paddle
from PlayerPaddle import PlayerPaddle
from TrackingBall import TrackingBall
from Wall import Wall
from physics.Manifold import Manifold
from physics.Vec2 import Vec2

ACCELERATION = 10
SPEED_BALL = 10
SPEED_RATIO_TRACKING_BALL = 1.5


class Game(object):
    WIDTH = 1080
    HEIGHT = 720

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = np.zeros((Game.WIDTH, Game.HEIGHT))

        self.ball = Ball(920, 360)
        self.ball.velocity = Vec2(-0.707, -0.707)
        self.ball.velocity *= SPEED_BALL
        self.track_ball = TrackingBall(920, 360)
        self.track_ball.velocity = self.ball.velocity
        self.track_ball.velocity *= SPEED_RATIO_TRACKING_BALL
        self.computer = ComputerPaddle(100, 360)
        self.player = PlayerPaddle(980, 360)
        self.wall_north = Wall(540, 0, 1080, 20)
        self.wall_east = Wall(1080, 360, 20, 720)
        self.wall_south = Wall(540, 720, 1080, 20)
        self.wall_west = Wall(0, 360, 20, 720)

        self.entities = [self.computer, self.player, self.ball, self.track_ball]
        self.walls = [self.wall_north, self.wall_east, self.wall_south, self.wall_west]

    def input(self, dx, dy):
        self.player.velocity = Vec2(ACCELERATION * dx, ACCELERATION * dy)

        if not (0 < self.player.pos.y - self.player.shape.height / 2 + self.player.velocity.y) or not (
                            self.player.pos.y + self.player.shape.height / 2 + self.player.velocity.y < Game.HEIGHT):
            self.player.velocity = Vec2(0, 0)

    def update(self):
        # Collision of ball
        for entity in itertools.chain(self.entities, self.walls):
            if isinstance(entity, Ball):
                continue
            manifold = Manifold(self.ball, entity)
            if collision.aabb_vs_aabb(manifold):
                # Resolve collision
                collision.resolve_collision(manifold)
                # Transfer momentum
                if isinstance(entity, Paddle):
                    vel_dir = self.ball.velocity / Vec2(SPEED_BALL, SPEED_BALL)
                    ratio = 1 / vel_dir.y
                    # self.ball.velocity.y *= random.uniform(-ratio, ratio)

                # Recreate Tracking ball on player hit
                if entity == self.player:
                    self.entities.remove(self.track_ball)
                    self.track_ball = TrackingBall(self.ball.pos.x, self.ball.pos.y)
                    self.track_ball.velocity = self.ball.velocity
                    self.track_ball.velocity *= SPEED_RATIO_TRACKING_BALL
                    self.entities.append(self.track_ball)

                # Check for point
                if entity == self.wall_east or entity == self.wall_west:
                    self.add_point()

                # Paddle: Set velocity to zero, preventing the ball from being pushed out
                entity.collision_callback()

        # Collision of track ball
        for entity in self.walls:
            if entity == self.track_ball:
                continue
            manifold = Manifold(self.track_ball, entity)
            if collision.aabb_vs_aabb(manifold):
                # Resolve collision
                collision.resolve_collision(manifold)

                # If tracking ball hits west wall
                if entity == self.wall_west:
                    self.track_ball.velocity = Vec2(0, 0)

        # Give ball minimum speed
        ratio = SPEED_BALL / math.sqrt(math.pow(self.ball.velocity.x, 2) + math.pow(self.ball.velocity.y, 2))
        if ratio > 1:
            self.ball.velocity.x *= ratio + 0.01
            self.ball.velocity.y *= ratio + 0.01
        if self.track_ball.velocity == Vec2(0, 0):
            ratio = SPEED_BALL / math.sqrt(
                math.pow(self.track_ball.velocity.x, 2) + math.pow(self.track_ball.velocity.y, 2))
            if ratio > 1:
                self.track_ball.velocity.x *= ratio + 0.01
                self.track_ball.velocity.y *= ratio + 0.01

        # Calculate AI move
        self.computer.calculate_move(self.track_ball)

        # Update positions
        for entity in self.entities:
            entity.update()

    def render(self):
        self.pixels = np.zeros((Game.WIDTH, Game.HEIGHT))

        for entity in self.entities:
            self.pixels = entity.render(self)

        return self.pixels

    def add_point(self):
        if self.ball.pos.x < Game.WIDTH / 2:
            self.computer.add_point()
        else:
            self.player.add_point()
        print self.get_score()

    def get_score(self):
        return [self.computer.score, self.player.score]


class Controller(object):
    FRAMES_PER_SECOND = 30

    def __init__(self):
        self.k_up = self.k_down = 0
        self.field = Game(Game.WIDTH, Game.HEIGHT)

        # Connector that sends data to the visualization
        self.useConnector = True
        try:
            self.connector = Connector("localhost", 420)
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
            self.connector.update(float(self.field.paddle1.pos.y) / Game.HEIGHT,
                                  float(self.field.paddle2.pos.y) / Game.HEIGHT,
                                  float(self.field.bal.pos.x) / Game.WIDTH,
                                  float(self.field.bal.pos.y) / Game.HEIGHT,
                                  self.field.paddle1.score,
                                  self.field.paddle2.score)

        # Render
        pixels = self.field.render()
        pygame.surfarray.blit_array(self.screen, pixels)
        pygame.display.flip()


Controller()
