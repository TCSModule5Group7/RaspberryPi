from Paddle import Paddle


class PlayerPaddle(Paddle):
    def __init__(self, x, y):
        super(PlayerPaddle, self).__init__(x, y)

    def collision_callback(self):
        return
