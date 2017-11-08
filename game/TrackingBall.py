from Ball import Ball


class TrackingBall(Ball):
    def __init__(self, x, y):
        super(TrackingBall, self).__init__(x, y)
        self.restitution = 1

    def update(self, delta):
        if self.pos.x > 40:
            super(TrackingBall, self).update(delta)

    def render(self, game):
        return game.pixels
