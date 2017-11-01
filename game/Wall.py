from game.physics.AABB import AABB
from game.physics.Entity import Entity
from game.physics.Vec2 import Vec2


class Wall(Entity):
    def __init__(self, x, y, width, height):
        Entity.__init__(self, x, y, 0, 1, AABB(Vec2(x, y), width, height))

    def render(self, game):
        return game.pixels
