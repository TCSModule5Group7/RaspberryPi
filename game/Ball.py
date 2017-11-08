from game.physics.AABB import AABB
from game.physics.Entity import Entity
from game.physics.Vec2 import Vec2


class Ball(Entity):
    def __init__(self, x, y):
        super(Ball, self).__init__(x, y, 5, 1, AABB(Vec2(540, 360), 15, 15))
