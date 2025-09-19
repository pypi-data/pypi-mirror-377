from .. import mesh
from . import disc
from . import template_cylinder
import numpy as np
import collections
import posixpath


def init(
    outer_radius=1.0,
    length=1.0,
    fn=6,
    rot=0.0,
    ref="cylinder",
):
    """
    Returns a cylinder-object.

    3D volume
    3 Materials: top / outer_side / bottom

    Parameters
    ----------
    outer_radius : float
            Outer radius of the regular polygon defining the Disc.
    length : float
            Length of Cylinder.
    fn : int
            Number of vertices in outer regular polygon.
    rot : float
            Rotation in z of regular polygon.
    ref : str
            Key for the material.
    """
    top = disc.init(
        outer_radius=outer_radius,
        ref=posixpath.join(ref, "top"),
        fn=fn,
        rot=rot,
    )
    bot = disc.init(
        outer_radius=outer_radius,
        ref=posixpath.join(ref, "bot"),
        fn=fn,
        rot=(2 * np.pi) / (2 * fn) + rot,
    )

    cyl = mesh.init()

    for vkey in top["vertices"]:
        tmp_v = np.array(top["vertices"][vkey])
        tmp_v[2] = float(length)
        cyl["vertices"][vkey] = tmp_v
    for vnkey in top["vertex_normals"]:
        cyl["vertex_normals"][vnkey] = np.array([0, 0, 1])

    mtl_top = posixpath.join(ref, "top")
    cyl["materials"][mtl_top] = collections.OrderedDict()
    for fkey in top["materials"][mtl_top]:
        cyl["materials"][mtl_top][fkey] = top["materials"][mtl_top][fkey]

    for vkey in bot["vertices"]:
        cyl["vertices"][vkey] = bot["vertices"][vkey]
    for vnkey in bot["vertex_normals"]:
        cyl["vertex_normals"][vnkey] = np.array([0, 0, -1])

    mtl_bot = posixpath.join(ref, "bot")
    cyl["materials"][mtl_bot] = collections.OrderedDict()
    for fkey in bot["materials"][mtl_bot]:
        cyl["materials"][mtl_bot][fkey] = bot["materials"][mtl_bot][fkey]

    cyl = template_cylinder.weave_cylinder_faces(
        mesh=cyl,
        vkey_lower=posixpath.join(ref, "bot", "outer_bound"),
        vkey_upper=posixpath.join(ref, "top", "outer_bound"),
        ref=posixpath.join(ref, "outer"),
    )

    return cyl
