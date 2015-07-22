#!/usr/bin/env python3
from math import sqrt, atan2, cos, sin, acos, asin, pi

class Vector(tuple):
    def __new__(cls, x, y):
        return tuple.__new__(cls, (float(x), float(y)))

    def __add__(self, v):
        x1, y1 = self
        x2, y2 = v
        return Vector(x1 + x2, y1 + y2)

    def __sub__(self, v):
        x1, y1 = self
        x2, y2 = v
        return Vector(x1 - x2, y1 - y2)

    def __mul__(self, a):
        x, y = self
        return Vector(a * x, a * y)

    def __truediv__(self, a):
        x, y = self
        a = 1/a
        return Vector(a * x, a * y)

    def __rmul__(self, a):
        x, y = self
        return Vector(a * x, a * y)

    def __neg__(self):
        x, y = self
        return Vector(-x, -y)

    def __pos__(self):
        return self

    def __abs__(self):
        x, y = self
        return sqrt(x*x + y*y)

    def cartesian(self):
        x, y = self
        return (x, y)

    def x(self):
        x, _ = self
        return x

    def y(self):
        _, y = self
        return y

    def polar(self):
        x, y = self
        r = sqrt(x*x + y*y)
        θ = atan2(y, x)
        return (r, θ)

    def r(self):
        x, y = self
        return sqrt(x*x + y*y)

    def θ(self):
        x, y = self
        return atan2(y, x)

    def from_polar(r, θ):
        return Vector(r * cos(θ), r * sin(θ))

    def normalise(self):
        _, θ = self.polar()
        return Vector.from_polar(1, θ)

# generalise concept of bisection to a weighted sum of two vectors
# finds the point a fraction p along the line a->b
def dissect(a, b, p):
    return (1-p)*a + p*b

def bisect(a, b):
    return (a+b)*0.5

# bisect an angle and return a point d on the new line bd
def abisect(a, b, c):
    ab = abs(a - b)
    bc = abs(b - c)
    ca = abs(c - a)
    abc = acos((ab*ab + bc*bc - ca*ca) / (2*ab*bc))
    cab = acos((ca*ca + ab*ab - bc*bc) / (2*ca*ab))
    adb = pi - cab - abc/2
    ad = ab * sin(abc/2) / sin(adb)
    return dissect(a, c, ad/ca)

# find the point of intersection between two lines a and b
def intersect(a1, a2, b1, b2):
    ax, ay = a1
    bx, by = a2 - a1
    cx, cy = b1
    dx, dy = b2 - b1

    if dx == 0:
        l = (cx - ax) / bx
    elif dy == 0:
        l = (cy - ay) / by
    else:
        l = ((ay - cy)/dy - (ax-cx)/dx) / (bx/dx - by/dy)
    return a1 + l * (a2 - a1)

# centroid of a triangle abc
def centroid(a, b, c):
    ab = bisect(a, b)
    bc = bisect(b, c)
    return intersect(a, bc, ab, c)

# are two vectors parallel?
def parallel(a, b):
    ax, ay = a
    bx, by = b
    try:
        return bx / ax == by / ay
    except ZeroDivisionError:
        try:
            return ax / bx == ay / by
        except ZeroDivisionError:
            return (ax == 0 and ay == 0) or (bx == 0 and by == 0)

# rotate a vector counterclockwise
def rotate(v, φ):
    (r, θ) = v.polar()
    return Vector.from_polar(r, θ + φ)

