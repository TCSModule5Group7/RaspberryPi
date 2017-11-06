from physics.AABB import AABB
from physics.Entity import Entity
from physics.Vec2 import Vec2
import Game


class Paddle(Entity):
    def __init__(self, x, y):
        super(Paddle, self).__init__(x, y, 0, 1, AABB(Vec2(Game.WIDTH * 0.1, Game.HEIGHT / 2), 20, 200))
        self.score = 0

    def collision_callback(self):
        self.velocity = Vec2(0, 0)

    def update(self):
        Entity.update(self)

    def add_point(self):
        self.score += 1
