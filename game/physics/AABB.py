from Vec2 import Vec2


class AABB:
    def __init__(self, pos, width, height):
        self.width = width
        self.height = height
        self.min = Vec2(pos.x - width / 2, pos.y - height / 2)
        self.max = Vec2(pos.x + width / 2, pos.y + height / 2)

    def set_pos(self, pos):
        self.min = Vec2(pos.x - self.width / 2, pos.y - self.height / 2)
        self.max = Vec2(pos.x + self.width / 2, pos.y + self.height / 2)
