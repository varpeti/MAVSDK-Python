import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt


class Draw:
    def addPoint(self, point):
        xdata, ydata, zdata = self.hl._verts3d
        self.hl.set_xdata(np.array(np.append(xdata, point.x)))
        self.hl.set_ydata(np.array(np.append(ydata, point.y)))
        self.hl.set_3d_properties(np.array(np.append(zdata, point.z)))
        plt.draw()
        plt.show(block=False)

    def showPath(self, path):
        xdata, ydata, zdata = self.hk._verts3d
        x, y, z = [], [], []
        for i in path: x.append(i.x);y.append(i.y);z.append(i.z)
        self.hk.set_xdata(np.array(np.append(xdata, x)))
        self.hk.set_ydata(np.array(np.append(ydata, y)))
        self.hk.set_3d_properties(np.array(np.append(zdata, z)))
        plt.draw()
        plt.show(block=True)

    def __init__(self, p1, p2):
        ax = Axes3D(plt.figure())
        self.hl, = ax.plot3D([0], [0], [0])
        self.hk, = ax.plot3D([0], [0], [0])

        ax.set_xlim3d([p1.x, p2.x])
        ax.set_ylim3d([p1.y, p2.y])
        ax.set_zlim3d([p1.z, p2.z])

    @staticmethod
    def wait():
        plt.show(block=True)


if __name__ == '__main__':
    class Point:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z


    draw = Draw(Point(-32.0, -32.0, 0.0), Point(32.0, 32.0, 64.0))
    draw.wait()
