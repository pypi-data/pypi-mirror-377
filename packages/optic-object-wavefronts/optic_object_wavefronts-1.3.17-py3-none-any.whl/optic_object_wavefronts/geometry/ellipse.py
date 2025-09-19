import numpy as np


class QuadraticEquation:
    def __init__(self, p, q):
        self.p_over_2 = 0.5 * float(p)
        self.q = float(q)
        self.inner_part_of_sqrt = self.p_over_2 * self.p_over_2 - self.q

        if self.has_real_solution():
            self.sqrt = np.sqrt(self.inner_part_of_sqrt)

    def has_real_solution(self):
        return self.inner_part_of_sqrt >= 0.0

    def minus_solution(self):
        return -self.p_over_2 - self.sqrt

    def plus_solution(self):
        return -self.p_over_2 + self.sqrt


def _elliptic_radii(focal_length_x, focal_length_y):
    radius_x = 2.0 * focal_length_x
    radius_y = 2.0 * focal_length_y
    radius_z = 0.5 * (radius_x + radius_y)
    return radius_x, radius_y, radius_z


def ray_intersection(support, direction, radius_x, radius_y, radius_z):
    """
    ellipsiod is given by f(x,y,z) = 0 with
    f(x,y,z) = x^2/A^2 + y^2/B^2 + (z-C)^2/C^2 - 1

    So this is a general tri-axial ellipsoid with its center
    in (0,0,c). Thus f(0,0,0) is exactly zero, as for all the
    other mirrors as well.

    The intersections of this ellipsoid with a general ray given by
    ray = base + dir * t      or short:  b + d * t
    can be expressed as:

    0=((bx+t*dx)^2)/(A^2) +((by+t*dy)^2)/(B^2) +((bz+t*dz-C)^2)/(C^2)

    solve for t:

    0=t^2*()
         p/m stands for plus/minus

    We only want to define a "long" and "short" focal length, so in
    our case we define:
     A = 2*short_focal_length
     B = 2*long_focal_length
     c = (A+B)/2   just the mean of the two ...
    since I don't have any better idea.
    """

    A = float(radius_x)
    B = float(radius_y)
    C = float(radius_z)

    iAA = 1.0 / (A * A)
    iBB = 1.0 / (B * B)
    iCC = 1.0 / (C * C)

    bx = float(support[0])
    by = float(support[1])
    bz = float(support[2])

    dx = float(direction[0])
    dy = float(direction[1])
    dz = float(direction[2])

    _a = (dx * dx) * iAA + (dy * dy) * iBB + (dz * dz) * iCC
    _b = 2.0 * ((bx * dx) * iAA + (by * dy) * iBB + dz * (bz - C) * iCC)
    _c = (bx * bx) * iAA + (by * by) * iBB + (bz * bz - 2.0 * bz * C) * iCC

    return QuadraticEquation(p=_b / _a, q=_c / _a)


def surface_height(x, y, focal_length_x, focal_length_y):
    radius_x, radius_y, radius_z = _elliptic_radii(
        focal_length_x, focal_length_y
    )
    eq = ray_intersection(
        support=np.array([x, y, 0.0]),
        direction=np.array([0.0, 0.0, 1.0]),
        radius_x=radius_x,
        radius_y=radius_y,
        radius_z=radius_z,
    )
    assert eq.has_real_solution()
    return eq.minus_solution()


def surface_normal(x, y, focal_length_x, focal_length_y):
    """
    surface normal is given as  ( -dz/dx , -dz/dy , 1 )

    z(x,y) = C*sqrt(1-x^2/A^2-y^2/B^2)+C
    dz/dx = C*1/2*(1-x^2/A^2-y^2/B^2)^(-1/2) * (-2*x/A^2)
    dz/dy = C*1/2*(1-x^2/A^2-y^2/B^2)^(-1/2) * (-2*y/A^2)
    normal = ( -dz/dx , -dz/dy , 1 )
    surface_normal_factor = C*1/2*(1-x^2/A^2-y^2/B^2)^(-1/2)
    """

    radius_x, radius_y, radius_z = _elliptic_radii(
        focal_length_x, focal_length_y
    )

    A = float(radius_x)
    B = float(radius_y)
    C = float(radius_z)

    iAA = 1.0 / (A * A)
    iBB = 1.0 / (B * B)
    iCC = 1.0 / (C * C)

    surface_normal_factor = (
        C * 0.5 * np.sqrt(1.0 - (x * x) * iAA - (y * y) * iBB)
    )

    normal = np.array(
        [
            surface_normal_factor * (-2.0 * x * iAA),
            surface_normal_factor * (-2.0 * y * iAA),
            1.0,
        ]
    )
    return normal / np.linalg.norm(normal)
