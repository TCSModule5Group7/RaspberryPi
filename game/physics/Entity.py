from Vec2 import Vec2


class Entity(object):
    def __init__(self, x, y, inv_mass, restitution, shape):
        self.pos = Vec2(x, y)
        self.velocity = Vec2(0, 0)
        self.abs_vel = Vec2(0, 0)
        self.restitution = restitution  # Bounciness [0,1]
        self.inv_mass = inv_mass
        self.shape = shape

    def collision_callback(self):
        return

    def update(self, dt):
        self.pos += self.velocity * dt
        self.shape.set_pos(self.pos)

    def render(self, game):
        for x in range(self.shape.width):
            for y in range(self.shape.height):
                if 0 < x + self.pos.x - self.shape.width / 2 < game.width \
                        and 0 < y + self.pos.y - self.shape.height / 2 < game.height:
                    # if y + self.y - self.height / 2 >= Field.HEIGHT: continue
                    # if x + self.x - self.width / 2 >= Field.WIDTH: continue
                    game.pixels[
                        int((x + self.pos.x - self.shape.width / 2) % game.width), int(
                            (y + self.pos.y - self.shape.height / 2) % game.height)] = 255

        return game.pixels
