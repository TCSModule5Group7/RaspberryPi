import itertools
import math
import socket
import random
import sys
import Queue
# import tracking
import LaptopTracking
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
from threading import Thread
import TriTracker

ACCELERATION = 10
SPEED_BALL = 7
SPEED_RATIO_TRACKING_BALL = 2


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
        self.track_ball = self.ball
        self.computer = ComputerPaddle(50, 360)
        self.player = PlayerPaddle(1030, 360)
        self.wall_north = Wall(540, 0, 1080, 20)
        self.wall_east = Wall(1080, 360, 20, 720)
        self.wall_south = Wall(540, 720, 1080, 20)
        self.wall_west = Wall(0, 360, 20, 720)

        self.entities = [self.computer, self.player, self.ball, self.track_ball]
        self.walls = [self.wall_north, self.wall_east, self.wall_south, self.wall_west]

        self.track_ball = self.spawn_trackball()

    def input(self, dx, dy):
        self.player.velocity = Vec2(ACCELERATION * dx, ACCELERATION * dy)

        if not (0 < self.player.pos.y - self.player.shape.height / 2 + self.player.velocity.y) or not (
                            self.player.pos.y + self.player.shape.height / 2 + self.player.velocity.y < Game.HEIGHT):
            self.player.velocity = Vec2(0, 0)

    def paddletracking(self, datagreen):
        if 1 > datagreen > 0:
            self.player.pos.y = datagreen * Game.HEIGHT

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
        self.pixels = np.zeros((Game.WIDTH, Game.HEIGHT))

        for entity in self.entities:
            self.pixels = entity.render(self)

        return self.pixels

    def add_point(self):
        if self.ball.pos.x < Game.WIDTH / 2:
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


class Controller(object):
    FRAMES_PER_SECOND = 30

    def __init__(self, useConnector, useMotion):
        # object tracking queues
        self.q_camera_read_green = Queue.Queue()
        self.q_camera_read_blue = Queue.Queue()
        self.q_camera_read_red = Queue.Queue()
        # object tracking thread
        self.tracker = TriTracker.LaptopTracker(self.q_camera_read_green, self.q_camera_read_blue, self.q_camera_read_red,
                                                    False)

        self.k_up = self.k_down = 0
        self.field = Game(Game.WIDTH, Game.HEIGHT)

        # Connector that sends data to the visualization
        self.useConnector = useConnector
        if self.useConnector:
            try:
                self.connector = Connector("localhost", 420)
                self.connector.connect()
            except socket.error:
                self.useConnector = False

        # PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.clock = pygame.time.Clock()

        self.useMotion = useMotion
        if self.useMotion:
            self.tracker.start()

        # Loop
        while 1:
            self.loop(self.q_camera_read_green, self.q_camera_read_blue, self.q_camera_read_red)

    def loop(self, QueueGreen, QueueBlue, QueueRed):
        self.clock.tick(30)
        self.running = True

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
        if not self.useMotion:
            self.field.input(0, self.k_down + self.k_up)

        if self.useMotion:
            datagreen = QueueGreen.get()
            datablue = QueueBlue.get()
            datared = QueueRed.get()

            if datablue is not None and datared is not None and datagreen is not None and (datablue - datared) is not 0:

                 if (datagreen < datablue):
                    datagreen = datablue


                 if (datagreen > datared):
                     datagreen = datared

                 datagreen -= datablue
                 datared -= datablue
                 calibratedY = (1 / datared) * datagreen
                 print("green"+ str(datagreen))
                 print("blue"+ str(datablue))
                 print("red" + str(datared))
                 print("Y"+ str(calibratedY))
                 self.field.paddletracking(calibratedY)

        # Update the field
        self.field.update()

        # Send gamestate to visualization
        if self.useConnector:
            s = self.connector.update(float(self.field.computer.pos.y) / Game.HEIGHT,
                                      float(self.field.player.pos.y) / Game.HEIGHT,
                                      float(self.field.ball.pos.x) / Game.WIDTH,
                                      float(self.field.ball.pos.y) / Game.HEIGHT,
                                      self.field.computer.score,
                                      self.field.player.score)
            # do something with the command

        # Render
        pixels = self.field.render()
        pygame.surfarray.blit_array(self.screen, pixels)
        pygame.display.flip()


Controller(False, True)
