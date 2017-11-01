from game.physics.AABB import AABB
from game.physics.Entity import Entity
from game.physics.Vec2 import Vec2


class Bal(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, 5, 0.8, AABB(Vec2(540, 360), 20, 20))
