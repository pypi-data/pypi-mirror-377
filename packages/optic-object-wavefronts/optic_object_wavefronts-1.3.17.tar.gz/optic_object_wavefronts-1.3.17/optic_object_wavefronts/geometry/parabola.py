import numpy as np


def surface_height(x, y, focal_length):
    r = np.hypot(x, y)
    return r**2 / (4.0 * focal_length)


def surface_normal(x, y, focal_length):
    """
    surface normal is given as  ( -dz/dx , -dz/dy , 1 )

    z(x,y) = (x**2 + y**2)/(4f)
    """
    dzdx = (2.0 * x) / (4.0 * focal_length)
    dzdy = (2.0 * y) / (4.0 * focal_length)
    normal = np.array([-dzdx, -dzdy, 1.0])
    return normal / np.linalg.norm(normal)
