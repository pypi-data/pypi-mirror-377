import numpy as np
import collections
import os


def make_vertices_xy(outer_radius=1.0, ref="ring", fn=16, rot=0.0):
    vertices = collections.OrderedDict()
    for nphi, phi in enumerate(
        np.linspace(0.0, 2.0 * np.pi, fn, endpoint=False)
    ):
        vkey = os.path.join(ref, "{:06d}".format(nphi))
        vertices[vkey] = np.array(
            [
                outer_radius * np.cos(rot + phi),
                outer_radius * np.sin(rot + phi),
                0.0,
            ]
        )
    return vertices


def inner_radius(fn):
    return 1.0 * np.cos(np.pi / fn)
