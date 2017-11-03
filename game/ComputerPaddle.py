from game.Paddle import Paddle

SPEED_COMPUTER = 5


class ComputerPaddle(Paddle):
    def __init__(self, x, y):
        super(ComputerPaddle, self).__init__(x, y)

    def calculate_move(self, track_ball):
        # Margin to small, avoid stuttering
        if abs(self.pos.y - track_ball.pos.y) < self.shape.height / 2:
            self.velocity.y = 0
            return

        if track_ball.pos.y > self.pos.y:
            self.velocity.y = SPEED_COMPUTER
        else:
            self.velocity.y = -SPEED_COMPUTER
