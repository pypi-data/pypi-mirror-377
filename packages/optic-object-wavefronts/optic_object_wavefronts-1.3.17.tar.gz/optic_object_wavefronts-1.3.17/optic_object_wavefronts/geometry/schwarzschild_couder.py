import numpy as np


def surface_height(x, y, k, c, a1, a2, a3, a4, a5, a6, a7, a8):
    r = np.hypot(x, y)
    z = 0.0
    z += (c * r**2) / (1 + np.sqrt((1 - (1 + k) * c**2 * r**2)))
    z += a1 * r**2
    z += a2 * r**4
    z += a3 * r**6
    z += a4 * r**8
    z += a5 * r**10
    z += a6 * r**12
    z += a7 * r**14
    z += a8 * r**16
    return z


def surface_normal(x, y, k, c, a1, a2, a3, a4, a5, a6, a7, a8, delta=1e-6):
    """
    surface-normal is: ( -dz/dx , -dz/dy , 1 )
    """
    xp = x + delta
    xm = x - delta
    yp = y + delta
    ym = y - delta
    z_xp = surface_height(xp, y, k, c, a1, a2, a3, a4, a5, a6, a7, a8)
    z_xm = surface_height(xm, y, k, c, a1, a2, a3, a4, a5, a6, a7, a8)
    z_yp = surface_height(x, yp, k, c, a1, a2, a3, a4, a5, a6, a7, a8)
    z_ym = surface_height(x, ym, k, c, a1, a2, a3, a4, a5, a6, a7, a8)
    dzdx = (z_xp - z_xm) / (2 * delta)
    dzdy = (z_yp - z_ym) / (2 * delta)
    normal = [-dzdx, -dzdy, 1.0]
    return normal / np.linalg.norm(normal)
