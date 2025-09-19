import numpy as np
import posixpath
import collections
from .. import mesh
from . import template_cylinder
from . import plane
from . import schmidt_corrector_surface


def init(
    outer_polygon,
    inner_polygon,
    schmidt_corrector_curvature_config,
    offset,
    fn_hex_grid,
    ref="schmidt_corrector_plate",
    fill_concave=False,
):
    top = schmidt_corrector_surface.init(
        outer_polygon=outer_polygon,
        inner_polygon=inner_polygon,
        schmidt_corrector_curvature_config=schmidt_corrector_curvature_config,
        fn_hex_grid=fn_hex_grid,
        ref=posixpath.join(ref, "top"),
        fill_concave=fill_concave,
    )
    bot = plane.init(
        outer_polygon=outer_polygon,
        inner_polygon=inner_polygon,
        ref=posixpath.join(ref, "bot"),
        fn_hex_grid=fn_hex_grid,
        fill_concave=fill_concave,
    )

    lens = mesh.init()

    for vkey in top["vertices"]:
        tmp_v = np.array(top["vertices"][vkey])
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

    if inner_polygon is not None:
        lens = template_cylinder.weave_cylinder_faces(
            mesh=lens,
            vkey_lower=posixpath.join(ref, "bot", "inner_bound"),
            vkey_upper=posixpath.join(ref, "top", "inner_bound"),
            ref=posixpath.join(ref, "inner"),
            norm_sign=-1.0,
        )

    return lens
