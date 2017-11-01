from Vec2 import Vec2


class Entity:
    def __init__(self, x, y, inv_mass, restitution, shape):
        self.pos = Vec2(x, y)
        self.velocity = Vec2(0, 0)
        self.restitution = restitution  # Bounciness [0,1]
        self.inv_mass = inv_mass
        self.shape = shape

    def collision_callback(self):
        return

    def update(self):
        self.pos += self.velocity
        self.shape.set_pos(self.pos)

    def render(self, game):
        for x in range(self.shape.width):
            for y in range(self.shape.height):
                if 0 < x + self.pos.x - self.shape.width / 2 < game.WIDTH \
                        and 0 < y + self.pos.y - self.shape.height / 2 < game.HEIGHT:
                    # if y + self.y - self.height / 2 >= Field.HEIGHT: continue
                    # if x + self.x - self.width / 2 >= Field.WIDTH: continue
                    game.pixels[
                        int((x + self.pos.x - self.shape.width / 2) % game.WIDTH), int(
                            (y + self.pos.y - self.shape.height / 2) % game.HEIGHT)] = 255

        return game.pixels
