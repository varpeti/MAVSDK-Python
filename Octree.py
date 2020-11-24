class Vector3:
    x = 0.0
    y = 0.0
    z = 0.0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z)

    def __repr__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z)


class Octree:
    pos = Vector3(0.0, 0.0, 0.0)
    size = Vector3(0.0, 0.0, 0.0)
    value = 0
    leaf = True
    area = 0

    minSize = 1.0
    NUMBER_OF_CHILDREN = 8

    '''   4------5
         /|     /|
        0------1 |
        | |    | |
        | 6----|-7
        |/     |/
        2------3
    '''
    children = []

    def __init__(self, pos, size, value):
        self.pos = pos
        self.size = size
        self.value = value
        self.leaf = True
        self.area = size.x * size.y * size.z * 8
        self.children = [None] * Octree.NUMBER_OF_CHILDREN

    def setValue(self, pos, size, value):
        # print(self.pos, self.size, self.area, Octree.minSize, self.area <= Octree.minSize)
        if self.isFullyContained(pos, size):
            # print("FullyContained")
            if not self.leaf:
                self.merge()
            self.value = value
            self.leaf = True
        elif not self.isFullyOutside(pos, size):
            # print("PartiallyContained")
            if self.area <= Octree.minSize:
                # self.value = value
                return
            if self.leaf:
                self.split()
            self.setChildValues(pos, size, value)
        # else:
        # print("FullyOutside")

    def getValue(self, pos):
        if self.isFullyOutside(pos, Vector3(0.0, 0.0, 0.0)):
            return None

        if self.leaf:
            return self.value

        for i in range(Octree.NUMBER_OF_CHILDREN):
            value = self.children[i].getValue(pos)
            if value is not None:
                return value
        return None

    def drawSelf(self):
        print(self.pos, self.size, self.value)

    def draw(self):
        if self.leaf:
            self.drawSelf()
        else:
            for i in range(Octree.NUMBER_OF_CHILDREN):
                self.children[i].draw()

    def isFullyContained(self, pos, size):
        return pos.x - size.x <= self.pos.x - self.size.x and \
               pos.x + size.x >= self.pos.x + self.size.x and \
               pos.y - size.y <= self.pos.y - self.size.y and \
               pos.y + size.y >= self.pos.y + self.size.y and \
               pos.z - size.z <= self.pos.z - self.size.z and \
               pos.z + size.z >= self.pos.z + self.size.z

    def isFullyOutside(self, pos, size):
        return self.pos.x + self.size.x < pos.x - size.x or \
               self.pos.y + self.size.y < pos.y - size.y or \
               self.pos.z + self.size.z < pos.z - size.z or \
               self.pos.x - self.size.x > pos.x + size.x or \
               self.pos.y - self.size.y > pos.y + size.y or \
               self.pos.z - self.size.z > pos.z + size.z

    def setChildValues(self, pos, size, value):
        for i in range(Octree.NUMBER_OF_CHILDREN):
            self.children[i].setValue(pos, size, value)

        for i in range(Octree.NUMBER_OF_CHILDREN):
            if not self.children[i].leaf:
                return
            if self.children[0].value != self.children[i].value:
                return

        self.merge()

    def split(self):
        self.leaf = False
        childSize = Vector3(self.size.x / 2.0, self.size.y / 2.0, self.size.z / 2.0)

        self.children[0] = Octree(Vector3(self.pos.x - childSize.x, self.pos.y - childSize.y, self.pos.z - childSize.z),
                                  childSize, self.value)
        self.children[1] = Octree(Vector3(self.pos.x + childSize.x, self.pos.y - childSize.y, self.pos.z - childSize.z),
                                  childSize, self.value)
        self.children[2] = Octree(Vector3(self.pos.x - childSize.x, self.pos.y + childSize.y, self.pos.z - childSize.z),
                                  childSize, self.value)
        self.children[3] = Octree(Vector3(self.pos.x + childSize.x, self.pos.y + childSize.y, self.pos.z - childSize.z),
                                  childSize, self.value)
        self.children[4] = Octree(Vector3(self.pos.x - childSize.x, self.pos.y - childSize.y, self.pos.z + childSize.z),
                                  childSize, self.value)
        self.children[5] = Octree(Vector3(self.pos.x + childSize.x, self.pos.y - childSize.y, self.pos.z + childSize.z),
                                  childSize, self.value)
        self.children[6] = Octree(Vector3(self.pos.x - childSize.x, self.pos.y + childSize.y, self.pos.z + childSize.z),
                                  childSize, self.value)
        self.children[7] = Octree(Vector3(self.pos.x + childSize.x, self.pos.y + childSize.y, self.pos.z + childSize.z),
                                  childSize, self.value)

    def merge(self):
        self.leaf = True
        self.value = self.children[0].value
        for i in range(Octree.NUMBER_OF_CHILDREN):
            self.children[i] = None

    def getLeavesByValue(self, value):
        ret = []
        if self.leaf:
            ret.append(self)
        else:
            for i in range(Octree.NUMBER_OF_CHILDREN):
                leaves = self.children[i].getLeavesByValue(value)
                for leaf in leaves:
                    ret.append(leaf)
        return ret

    def getLeavesInArea(self, pos, size):
        leaves = []
        if self.isFullyOutside(pos, size):
            return leaves

        if self.leaf:
            leaves.append(self)
            return leaves

        for i in range(Octree.NUMBER_OF_CHILDREN):
            new_leaves = self.children[i].getLeavesInArea(pos, size)
            for leaf in new_leaves:
                leaves.append(leaf)
        return leaves

    '''     nz nx
             |/
         ny-cur-ny
            /|
          nx nz
    '''

    def getNeighbours(self, pos):
        cur = self.getLeavesInArea(pos, Vector3(0.0, 0.0, 0.0))[0]
        minLength = (Octree.minSize ** (1.0 / 3.0)) / 2
        neighbours = []
        nx = self.getLeavesInArea(cur.pos, Vector3(cur.size.x + minLength, 0.0, 0.0))
        for i in nx: neighbours.append(i)
        neighbours.remove(cur)
        ny = self.getLeavesInArea(cur.pos, Vector3(0.0, cur.size.y + minLength, 0.0))
        for i in ny: neighbours.append(i)
        neighbours.remove(cur)
        nz = self.getLeavesInArea(cur.pos, Vector3(0.0, 0.0, cur.size.z + minLength))
        for i in nz: neighbours.append(i)
        neighbours.remove(cur)
        return neighbours


if __name__ == '__main__':
    Octree.minSize = 0.25 * 0.25 * 0.25
    root = Octree(Vector3(0.0, 0.0, -32.0), Vector3(32.0, 32.0, 32.0), "Air")
    root.setValue(Vector3(0.125, 0.125, -0.125), Vector3(0.125, 0.125, 0.125), "Obstacle")
    nl = root.getNeighbours(Vector3(0.125, 0.625, -0.125))
    print(len(nl))
    for n in nl:
        print(n.pos)
