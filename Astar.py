import math
from queue import PriorityQueue
from typing import List

from Octree import Octree
from Pos import Pos


class Node:
    def __init__(self, value: Pos, parent, goal: Pos):
        self.parent = parent
        self.value = value

        if parent:
            self.goal = parent.goal
            self.path = parent.path[:]
            self.path.append(value)
            self.g = parent.g + value.distance(parent.value)
        else:
            self.path = [value]
            self.goal = goal
            self.g = 0.0

        self.h = self.getDistance()
        self.f = self.g + self.h

    def getDistance(self):
        return self.value.distance(self.goal)

    def getChildren(self, root: Octree, goalOctree: Octree):
        cur = root.getLeavesInArea(self.value, Pos(0.0, 0.0, 0.0))[0]
        if cur == goalOctree:
            return [Node(self.goal, self, self.goal)]
        neighbours = root.getNeighbours(self.value, cur)
        np = Octree.cornerIt(neighbours)
        children = []
        for p in np:
            children.append(Node(p, self, self.goal))
        return children

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value


def Astar(start: Pos, goal: Pos, root: Octree, draw) -> List[Pos]:
    path = []
    visited = {}
    priorityQueue = PriorityQueue()
    count = 0
    goalOctree = root.getLeavesInArea(goal, Pos(0.0, 0.0, 0.0))[0]

    priorityQueue.put((0, count, Node(start, 0, goal)))

    while not path and priorityQueue.qsize():
        current = priorityQueue.get()[2]
        if current.value in visited: continue
        draw.addPoint(current.value)
        visited[current.value] = True
        children = current.getChildren(root, goalOctree)
        for child in children:
            if child.value not in visited:
                count += 1
                if child.h == 0:
                    path = child.path
                    break
                priorityQueue.put((child.f, count, child))
    return path


'''
draw = Draw(Pos(-32.0, -32.0, 0.0), Pos(32.0, 32.0, -64.0))

if __name__ == '__main__':
    Octree.minSize = 0.25 * 0.25 * 0.25
    root = Octree(Pos(0.0, 0.0, -32.0), Pos(32.0, 32.0, 32.0), "Air")
    root.setValue(Pos(2.75, 0.0, 0.0), Pos(0.5, 5.125, 5.500), "Obstacle")

    path = Astar(Pos(0.0, 0.0, 0.0), Pos(6.0, 0.0, -1.0), root)
    print(path)
    draw.showPath(path)
    draw.wait()
'''

'''
if __name__ == '__main__':
    a = {}
    b = Pos(10, 32, -10)
    c = Pos(320, 1, -10)
    d = Pos(10, 32, -10)
    a[b] = True
    print(b in a, c in a, d in a) # True False True
'''