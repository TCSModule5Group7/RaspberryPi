import itertools
import math
import random

# import tracking
import numpy as np

import physics.Collision as collision
from Ball import Ball
from ComputerPaddle import ComputerPaddle
from Paddle import Paddle
from PlayerPaddle import PlayerPaddle
from TrackingBall import TrackingBall
from Wall import Wall
from physics.Manifold import Manifold
from physics.Vec2 import Vec2

ACCELERATION = 10
SPEED_BALL = 7
SPEED_RATIO_TRACKING_BALL = 2
WIDTH = 1024
HEIGHT = 768


class Game(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = np.zeros((WIDTH, HEIGHT))

        self.ball = Ball(920, 360)
        self.ball.velocity = Vec2(-0.707, -0.707)
        self.ball.velocity *= SPEED_BALL
        self.track_ball = self.ball
        self.computer = ComputerPaddle(0.1 * WIDTH, HEIGHT / 2)
        self.player = PlayerPaddle(0.9 * WIDTH, HEIGHT / 2)
        self.wall_north = Wall(WIDTH / 2, 0, WIDTH, 20)
        self.wall_east = Wall(WIDTH, 360, 20, HEIGHT)
        self.wall_south = Wall(WIDTH / 2, HEIGHT, WIDTH, 20)
        self.wall_west = Wall(0, HEIGHT / 2, 20, HEIGHT)

        self.entities = [self.computer, self.player, self.ball, self.track_ball]
        self.walls = [self.wall_north, self.wall_east, self.wall_south, self.wall_west]

        self.track_ball = self.spawn_trackball()

    def input(self, dx, dy):
        self.player.velocity = Vec2(ACCELERATION * dx, ACCELERATION * dy)

        if not (0 < self.player.pos.y - self.player.shape.height / 2 + self.player.velocity.y) or not (
                            self.player.pos.y + self.player.shape.height / 2 + self.player.velocity.y < HEIGHT):
            self.player.velocity = Vec2(0, 0)

    def paddletracking(self, y):
        self.player.pos.y = y

    def update(self):
        # Collision of ball
        for entity in itertools.chain(self.entities, self.walls):
            if isinstance(entity, Ball):
                continue
            manifold = Manifold(self.ball, entity)
            if collision.aabb_vs_aabb(manifold):
                # Resolve collision
                collision.resolve_collision(manifold)

                if isinstance(entity, Paddle):
                    print "collision"
                    self.track_ball = self.spawn_trackball()

                    # Transfer momentum
                    vel_dir = self.ball.velocity / Vec2(SPEED_BALL, SPEED_BALL)
                    ratio = 1 / vel_dir.y
                    # self.ball.velocity.y *= random.uniform(-ratio, ratio)

                # Check for point
                if entity == self.wall_east or entity == self.wall_west:
                    self.add_point()

                # Paddle: Set velocity to zero, preventing the ball from being pushed out
                entity.collision_callback()

        # Collision of track ball
        for entity in self.walls:
            manifold = Manifold(self.track_ball, entity)
            if collision.aabb_vs_aabb(manifold):
                # Resolve collision
                collision.resolve_collision(manifold)

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
        self.pixels = np.zeros((WIDTH, HEIGHT))

        for entity in self.entities:
            self.pixels = entity.render(self)

        return self.pixels

    def add_point(self):
        if self.ball.pos.x < WIDTH / 2:
            self.computer.add_point()
            self.ball.pos = Vec2(540, 360)
            self.ball.velocity.y = random.uniform(-0.5 * SPEED_BALL, 0.5 * SPEED_BALL)
            self.track_ball = self.spawn_trackball()
        else:
            self.player.add_point()
            self.ball.pos = Vec2(540, 360)
            self.ball.velocity.y = random.uniform(-0.7 * SPEED_BALL, 0.7 * SPEED_BALL)
            self.track_ball = self.spawn_trackball()
        print self.get_score()

    def get_score(self):
        return [self.computer.score, self.player.score]

    def spawn_trackball(self):
        if self.entities.__contains__(self.track_ball):
            self.entities.remove(self.track_ball)
        self.track_ball = TrackingBall(self.ball.pos.x, self.ball.pos.y)
        self.track_ball.velocity = self.ball.velocity
        self.track_ball.velocity *= SPEED_RATIO_TRACKING_BALL
        self.entities.append(self.track_ball)
        return self.track_ball
