import numbers


class Vec2(object):
    def __init__(self):
        self.x = 0
        self.y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __div__(self, other):
        return Vec2(self.x / other.x, self.y / other.y)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Vec2(self.x * other, self.y * other)
        else:
            raise Exception("Wrong type")

    def __abs__(self):
        self.x = abs(self.x)
        self.y = abs(self.y)

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y
