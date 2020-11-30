import math


class Pos:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z)

    def __repr__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z) + "\n"

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2.0 +
                         (self.y - other.y) ** 2.0 +
                         (self.z - other.z) ** 2.0)

    def __eq__(self, other):
        return (self.x == other.x) and \
               (self.y == other.y) and \
               (self.z == other.z)

    def __hash__(self):
        return math.floor((self.x + self.y * 32 - self.z * 32 * 32)*100)
