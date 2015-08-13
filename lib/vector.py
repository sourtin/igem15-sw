#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import sqrt, atan2, cos, sin, acos, asin, pi

class Vector(tuple):
    """2D vector implementation supporting many
       mathematical operators via overloading:
          + - * / abs round"""

    def __new__(cls, x, y):
        """return the paramaters to pass to new so
           that we can be pickled"""
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

    def __round__(self, n):
        x, y = self
        return Vector(round(x, n), round(y, n))

    def cartesian(self):
        """return cartesian coordinates"""
        x, y = self
        return (x, y)

    def x(self):
        """return the x cartesian coordinate"""
        x, _ = self
        return x

    def y(self):
        """return the y cartesian coordinate"""
        _, y = self
        return y

    def polar(self):
        """return polar coordinates r,θ"""
        x, y = self
        r = sqrt(x*x + y*y)
        θ = atan2(y, x)
        return (r, θ)

    def r(self):
        """return the r polar coordinate"""
        x, y = self
        return sqrt(x*x + y*y)

    def θ(self):
        """return the θ polar coordinate"""
        x, y = self
        return atan2(y, x)

    def from_polar(r, θ):
        """static; construct from polar coordinates"""
        return Vector(r * cos(θ), r * sin(θ))

    def normalise(self):
        """return a normalised unit vector"""
        _, θ = self.polar()
        return Vector.from_polar(1, θ)

    def rotate(self, φ):
        """rotate anticlockwise by φ"""
        r, θ = self.polar()
        return Vector.from_polar(r, θ + φ)

def dissect(a, b, p):
    """find the point the fraction p along the line ab"""
    return (1-p)*a + p*b

def bisect(a, b):
    """find the midpoint of ab"""
    return (a+b)*0.5

def abisect(a, b, c):
    """returns an arbitrary point along the bisection of the angle abc"""

    ab = abs(a - b)
    bc = abs(b - c)
    ca = abs(c - a)
    abc = acos((ab*ab + bc*bc - ca*ca) / (2*ab*bc))
    cab = acos((ca*ca + ab*ab - bc*bc) / (2*ca*ab))
    adb = pi - cab - abc/2
    ad = ab * sin(abc/2) / sin(adb)
    return dissect(a, c, ad/ca)

def intersect(a1, a2, b1, b2):
    """find the point of intersection between two lines a and b,
       a1, a2 - two points along line a
       b1, b2 - two points along line b"""

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

def centroid(a, b, c):
    """centroid of the triangle abc"""
    ab = bisect(a, b)
    bc = bisect(b, c)
    return intersect(a, bc, ab, c)

def parallel(a, b):
    """return whether two vectors a and b are parallel"""

    ax, ay = a
    bx, by = b
    try:
        return bx / ax == by / ay
    except ZeroDivisionError:
        try:
            return ax / bx == ay / by
        except ZeroDivisionError:
            return (ax == 0 and ay == 0) or (bx == 0 and by == 0)

