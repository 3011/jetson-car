import math
import time


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def get_center(left, right):
    x = (left.x + right.x)/2
    y = (left.y + right.y)/2
    z = (left.z + right.z)/2
    return Point(x, y, z)


def get_distance(left, right):
    x = left.x - right.x
    y = left.y - right.y
    z = left.z - right.z
    return math.hypot(x, y, z)


def get_y_distance(left, right):
    y = right.y - left.y
    return y


class FPS():
    def __init__(self):
        self.last_frame_time = time.time()

    def __call__(self):
        now = time.time()
        fps = int(1/(now-self.last_frame_time))
        self.last_frame_time = now
        return fps
