from physics.AABB import AABB
from physics.Entity import Entity
from physics.Vec2 import Vec2


class Wall(Entity):
    def __init__(self, x, y, width, height):
        super(Wall, self).__init__(x, y, 0, 1, AABB(Vec2(x, y), width, height))

    def render(self, game):
        return game.pixels
