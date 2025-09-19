import numpy as np
import posixpath
import collections
from .. import mesh
from . import template_cylinder
from . import spherical_cap_regular


def init(
    outer_radius,
    curvature_radius_top,
    curvature_radius_bot,
    offset,
    fn_polygon,
    fn_hex_grid,
    rot,
    ref="spherical_lens",
    inner_radius=None,
):
    top = spherical_cap_regular.init(
        outer_radius=outer_radius,
        inner_radius=inner_radius,
        curvature_radius=-1.0 * curvature_radius_top,
        ref=posixpath.join(ref, "top"),
        fn_polygon=fn_polygon,
        fn_hex_grid=fn_hex_grid,
        rot=rot,
    )
    bot = spherical_cap_regular.init(
        outer_radius=outer_radius,
        inner_radius=inner_radius,
        curvature_radius=-1.0 * curvature_radius_bot,
        ref=posixpath.join(ref, "bot"),
        fn_polygon=fn_polygon,
        fn_hex_grid=fn_hex_grid,
        rot=(2 * np.pi) / (2 * fn_polygon) + rot,
    )

    lens = mesh.init()

    for vkey in top["vertices"]:
        tmp_v = np.array(top["vertices"][vkey])
        # tmp_v[2] = tmp_v[2] + 0.5 * float(offset)
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
        tmp_v[2] = tmp_v[2] - float(offset)
        lens["vertices"][vkey] = tmp_v

    bot_mtl_key = posixpath.join(ref, "bot")
    lens["materials"][bot_mtl_key] = collections.OrderedDict()
    for fkey in bot["materials"][bot_mtl_key]:
        lens["materials"][bot_mtl_key][fkey] = bot["materials"][bot_mtl_key][
            fkey
        ]

    for vnkey in bot["vertex_normals"]:
        lens["vertex_normals"][vnkey] = -1.0 * bot["vertex_normals"][vnkey]

    lens = template_cylinder.weave_cylinder_faces(
        mesh=lens,
        vkey_lower=posixpath.join(ref, "bot", "outer_bound"),
        vkey_upper=posixpath.join(ref, "top", "outer_bound"),
        ref=posixpath.join(ref, "outer"),
        norm_sign=+1.0,
    )

    if inner_radius is not None:
        lens = template_cylinder.weave_cylinder_faces(
            mesh=lens,
            vkey_lower=posixpath.join(ref, "bot", "inner_bound"),
            vkey_upper=posixpath.join(ref, "top", "inner_bound"),
            ref=posixpath.join(ref, "inner"),
            norm_sign=-1.0,
        )

    return lens
