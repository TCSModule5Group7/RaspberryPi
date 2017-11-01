from Vec2 import Vec2

class Manifold:
    def __init__(self, entity_a, entity_b):
        self.entity_a = entity_a
        self.entity_b = entity_b
        self.penetration = 0
        self.normal = Vec2(0, 0)
