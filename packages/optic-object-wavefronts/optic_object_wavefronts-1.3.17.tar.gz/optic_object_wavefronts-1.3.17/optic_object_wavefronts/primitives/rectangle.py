from .. import mesh
from .. import geometry
import numpy as np
import posixpath
import collections


def init(
    x_width=4 / 3,
    y_width=1,
    ref="rectangle",
):
    """
    Returns a rectangle-object.

    2D surface
    1 Material

    Parameters
    ----------
    x_width : float
            Width in x.
    y_width : float
            Width in y.
    ref : str
            Key for the material.
    """
    join = posixpath.join
    rect = mesh.init()
    rect["vertices"][join(ref, "0")] = 0.5 * np.array([+x_width, +y_width, 0])
    rect["vertices"][join(ref, "1")] = 0.5 * np.array([-x_width, +y_width, 0])
    rect["vertices"][join(ref, "2")] = 0.5 * np.array([-x_width, -y_width, 0])
    rect["vertices"][join(ref, "3")] = 0.5 * np.array([+x_width, -y_width, 0])

    vnkey = join(ref, "0")
    rect["vertex_normals"][vnkey] = np.array([0.0, 0.0, 1.0])

    mtl_key = ref
    rect["materials"][mtl_key] = collections.OrderedDict()
    rect["materials"][mtl_key]["0"] = {
        "vertices": [join(ref, "0"), join(ref, "1"), join(ref, "2")],
        "vertex_normals": [vnkey, vnkey, vnkey],
    }
    rect["materials"][mtl_key]["1"] = {
        "vertices": [join(ref, "2"), join(ref, "3"), join(ref, "0")],
        "vertex_normals": [vnkey, vnkey, vnkey],
    }
    return rect
