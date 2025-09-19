import numpy as np
import posixpath
import collections
from .. import mesh
from . import cylinder
from . import spherical_cap_hexagonal


def estimate_height_of_cap(curvature_radius, outer_radius):
    return curvature_radius - np.sqrt(curvature_radius**2 - outer_radius**2)


def init(
    outer_radius,
    curvature_radius,
    fn,
    ref="spherical_lens_hexagonal",
):
    assert curvature_radius > 0.0
    assert outer_radius > 0.0

    top = spherical_cap_hexagonal.init(
        outer_radius=outer_radius,
        curvature_radius=-1.0 * curvature_radius,
        ref=posixpath.join(ref, "top"),
        fn=fn,
    )
    bot = spherical_cap_hexagonal.init(
        outer_radius=outer_radius,
        curvature_radius=1.0 * curvature_radius,
        ref=posixpath.join(ref, "bot"),
        fn=fn,
    )

    cap_height = estimate_height_of_cap(curvature_radius, outer_radius)

    lens = mesh.init()

    for vkey in top["vertices"]:
        tmp_v = np.array(top["vertices"][vkey])
        tmp_v[2] = tmp_v[2] + float(cap_height)
        lens["vertices"][vkey] = tmp_v
    top_mtl_key = posixpath.join(ref, "top")
    lens["materials"][top_mtl_key] = collections.OrderedDict()
    for fkey in top["materials"][top_mtl_key]:
        lens["materials"][top_mtl_key][fkey] = top["materials"][top_mtl_key][
            fkey
        ]
    for vnkey in top["vertex_normals"]:
        lens["vertex_normals"][vnkey] = +1.0 * top["vertex_normals"][vnkey]

    for vkey in bot["vertices"]:
        tmp_v = np.array(bot["vertices"][vkey])
        tmp_v[2] = tmp_v[2] - float(cap_height)
        lens["vertices"][vkey] = tmp_v
    bot_mtl_key = posixpath.join(ref, "bot")
    lens["materials"][bot_mtl_key] = collections.OrderedDict()
    for fkey in bot["materials"][bot_mtl_key]:
        lens["materials"][bot_mtl_key][fkey] = bot["materials"][bot_mtl_key][
            fkey
        ]
    for vnkey in bot["vertex_normals"]:
        lens["vertex_normals"][vnkey] = -1.0 * bot["vertex_normals"][vnkey]

    hexagonal_grid_spacing = outer_radius / fn

    lens = spherical_cap_hexagonal.weave_hexagon_edges(
        mesh=lens,
        outer_radius=outer_radius,
        margin_width_on_edge=0.1 * hexagonal_grid_spacing,
        ref=posixpath.join(ref, "side"),
    )

    return lens
