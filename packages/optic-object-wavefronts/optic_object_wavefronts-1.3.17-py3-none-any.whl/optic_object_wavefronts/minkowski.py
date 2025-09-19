import numpy as np
import posixpath
import scipy
from scipy.spatial import ConvexHull


def minkowski_hull_xy(poly1, poly2, dim=2, ref=""):
    points1 = np.array([poly1[k][0:dim] for k in poly1])
    points2 = np.array([poly2[k][0:dim] for k in poly2])

    points = []
    for p1 in points1:
        points.append(p1 + points2)
    points = np.vstack(points)
    hull = scipy.spatial.ConvexHull(points=points)
    vertices = [points[v] for v in hull.vertices]

    out = {}
    for i in range(len(vertices)):
        out[posixpath.join(ref, "{:06d}".format(i))] = np.array(
            [vertices[i][0], vertices[i][1], 0.0]
        )
    return out
