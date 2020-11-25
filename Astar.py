import asyncio
import heapq
import math
from queue import PriorityQueue

from typing import List

from Octree import Octree
from Draw import Draw


class Pos:
    neighbourDistance = 0.125

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


class Node:
    def __init__(self, value: Pos, parent, goal: Pos):
        self.parent = parent
        self.value = value

        if parent:
            self.goal = parent.goal
            self.path = parent.path[:]
            self.path.append(value)
            self.g = parent.g + Pos.neighbourDistance / 10
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
        children = []
        for n in neighbours:
            if n.value == "Air":
                children.append(Node(Pos(n.pos.x, n.pos.y, n.pos.z), self, self.goal))
        return children

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value


def Astar(start: Pos, goal: Pos, root: Octree) -> List[Pos]:
    path = []
    visited = []
    priorityQueue = PriorityQueue()
    count = 0
    goalOctree = root.getLeavesInArea(goal, Pos(0.0, 0.0, 0.0))[0]

    priorityQueue.put((0, count, Node(start, 0, goal)))

    while not path and priorityQueue.qsize():
        current = priorityQueue.get()[2]
        visited.append(current.value)
        #draw.addPoint(current.value)
        children = current.getChildren(root, goalOctree)
        for child in children:
            a = child.value not in visited
            if child.value not in visited:
                count += 1
                if child.h == 0:
                    path = child.path
                    break
                priorityQueue.put((child.f, count, child))
        if count > 9000:
            print("Over9000")
            return current.path
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