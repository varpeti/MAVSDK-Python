from Pos import Pos


class Octree:
    pos = Pos(0.0, 0.0, 0.0)
    size = Pos(0.0, 0.0, 0.0)
    value = 0
    leaf = True
    volume = 0

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
        self.volume = size.x * size.y * size.z * 8
        self.children: list[Octree] = [None] * Octree.NUMBER_OF_CHILDREN

    def setValue(self, pos, size, value):
        # print(self.pos, self.size, self.volume, Octree.minSize, self.volume <= Octree.minSize)
        if self.isFullyContained(pos, size):
            # print("FullyContained")
            if not self.leaf:
                self.merge()
            self.value = value
            self.leaf = True
        elif not self.isFullyOutside(pos, size):
            # print("PartiallyContained")
            if self.volume <= Octree.minSize:
                # self.value = value
                return
            if self.leaf:
                self.split()
            self.setChildValues(pos, size, value)
        # else:
        # print("FullyOutside")

    def getValue(self, pos):
        if self.isFullyOutside(pos, Pos(0.0, 0.0, 0.0)):
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
        childSize = Pos(self.size.x / 2.0, self.size.y / 2.0, self.size.z / 2.0)

        self.children[0] = Octree(Pos(self.pos.x - childSize.x, self.pos.y - childSize.y, self.pos.z - childSize.z),
                                  childSize, self.value)
        self.children[1] = Octree(Pos(self.pos.x + childSize.x, self.pos.y - childSize.y, self.pos.z - childSize.z),
                                  childSize, self.value)
        self.children[2] = Octree(Pos(self.pos.x - childSize.x, self.pos.y + childSize.y, self.pos.z - childSize.z),
                                  childSize, self.value)
        self.children[3] = Octree(Pos(self.pos.x + childSize.x, self.pos.y + childSize.y, self.pos.z - childSize.z),
                                  childSize, self.value)
        self.children[4] = Octree(Pos(self.pos.x - childSize.x, self.pos.y - childSize.y, self.pos.z + childSize.z),
                                  childSize, self.value)
        self.children[5] = Octree(Pos(self.pos.x + childSize.x, self.pos.y - childSize.y, self.pos.z + childSize.z),
                                  childSize, self.value)
        self.children[6] = Octree(Pos(self.pos.x - childSize.x, self.pos.y + childSize.y, self.pos.z + childSize.z),
                                  childSize, self.value)
        self.children[7] = Octree(Pos(self.pos.x + childSize.x, self.pos.y + childSize.y, self.pos.z + childSize.z),
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

    def getNeighbours(self, pos, cur=None):
        cur = cur or self.getLeavesInArea(pos, Pos(0.0, 0.0, 0.0))[0]
        minLength = (Octree.minSize ** (1.0 / 3.0)) / 2
        neighbours = []
        nx = self.getLeavesInArea(cur.pos, Pos(cur.size.x + minLength, cur.size.y - minLength, cur.size.z - minLength))
        for i in nx: neighbours.append(i)
        neighbours.remove(cur)
        ny = self.getLeavesInArea(cur.pos, Pos(cur.size.x - minLength, cur.size.y + minLength, cur.size.z - minLength))
        for i in ny: neighbours.append(i)
        neighbours.remove(cur)
        nz = self.getLeavesInArea(cur.pos, Pos(cur.size.x - minLength, cur.size.y - minLength, cur.size.z + minLength))
        for i in nz: neighbours.append(i)
        neighbours.remove(cur)
        return neighbours

    @staticmethod
    def cornerIt(neighbours: [int]):
        nodes = []
        minLength = (Octree.minSize ** (1.0 / 3.0))
        for n in neighbours:
            if n.value != "Air": continue
            thisLength = (n.volume ** (1.0 / 3.0))
            if thisLength <= minLength * 2: continue  # Too small to step in

            # Center
            nodes.append(n.pos)

            if thisLength <= minLength * 4: continue  # Too small to corner it

            cs = Pos(minLength * 2.0, minLength * 2.0, minLength * 2.0)
            nodes.append(Pos(n.pos.x + n.size.x - cs.x, n.pos.y + n.size.y - cs.y, n.pos.z + n.size.z - cs.z))
            nodes.append(Pos(n.pos.x - n.size.x + cs.x, n.pos.y + n.size.y - cs.y, n.pos.z + n.size.z - cs.z))
            nodes.append(Pos(n.pos.x + n.size.x - cs.x, n.pos.y - n.size.y + cs.y, n.pos.z + n.size.z - cs.z))
            nodes.append(Pos(n.pos.x - n.size.x + cs.x, n.pos.y - n.size.y + cs.y, n.pos.z + n.size.z - cs.z))
            nodes.append(Pos(n.pos.x + n.size.x - cs.x, n.pos.y + n.size.y - cs.y, n.pos.z - n.size.z + cs.z))
            nodes.append(Pos(n.pos.x - n.size.x + cs.x, n.pos.y + n.size.y - cs.y, n.pos.z - n.size.z + cs.z))
            nodes.append(Pos(n.pos.x + n.size.x - cs.x, n.pos.y - n.size.y + cs.y, n.pos.z - n.size.z + cs.z))
            nodes.append(Pos(n.pos.x - n.size.x + cs.x, n.pos.y - n.size.y + cs.y, n.pos.z - n.size.z + cs.z))
        return nodes


'''
if __name__ == '__main__':
    Octree.minSize = 0.25 * 0.25 * 0.25
    root = Octree(Pos(0.0, 0.0, -32.0), Pos(32.0, 32.0, 32.0), "Air")
    root.setValue(Pos(0.125, 0.125, -0.125), Pos(0.125, 0.125, 0.125), "Obstacle")
    nl = root.getNeighbours(Pos(0.125, 0.625, -0.125))
    print(len(nl))
    for n in nl:
        print(n.pos)
'''

if __name__ == '__main__':
    Octree.minSize = 0.25 * 0.25 * 0.25
    root = Octree(Pos(0.0, 0.0, -32.0), Pos(32.0, 32.0, 32.0), "Air")
    root.setValue(Pos(0.125, 0.125, -0.125), Pos(0.125, 0.125, 0.125), "Obstacle")
    nl = root.getNeighbours(Pos(0.125, 0.625, -0.125))
    nl = Octree.cornerIt(nl)
    for n in nl:
        print(n)
