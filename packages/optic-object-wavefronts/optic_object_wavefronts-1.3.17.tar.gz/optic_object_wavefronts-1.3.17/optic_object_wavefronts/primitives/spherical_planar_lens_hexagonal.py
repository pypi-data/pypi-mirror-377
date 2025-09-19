from . import spherical_cap_hexagonal
from . import disc
from .. import mesh
import numpy as np
import posixpath
import collections


def init(
    outer_radius,
    curvature_radius,
    width,
    fn=10,
    ref="spherical_planar_lens_hexagonal",
):
    join = posixpath.join
    front = spherical_cap_hexagonal.init(
        outer_radius=outer_radius,
        curvature_radius=curvature_radius,
        fn=fn,
        ref=join(ref, "front"),
    )

    back = disc.init(
        outer_radius=outer_radius,
        fn=6,
        ref=join(ref, "back"),
        rot=0.0,
    )

    center_of_curvature = np.array([0.0, 0.0, curvature_radius])

    back = mesh.translate(back, [0.0, 0.0, -width])
    for vnkey in back["vertex_normals"]:
        back["vertex_normals"][vnkey] = np.array([0.0, 0.0, -1.0])

    facet = mesh.merge(front, back)

    hexagonal_grid_spacing = outer_radius / fn

    facet = spherical_cap_hexagonal.weave_hexagon_edges(
        mesh=facet,
        outer_radius=outer_radius,
        margin_width_on_edge=0.1 * hexagonal_grid_spacing,
        ref=join(ref, "side"),
    )

    mtl_side_key = posixpath.join(ref, "side")
    mtl_side = facet["materials"][mtl_side_key]
    new_mtl_side = collections.OrderedDict()
    for fkey in mtl_side:
        va_key = mtl_side[fkey]["vertices"][0]
        vb_key = mtl_side[fkey]["vertices"][1]
        vc_key = mtl_side[fkey]["vertices"][2]

        va = facet["vertices"][va_key]
        vb = facet["vertices"][vb_key]
        vc = facet["vertices"][vc_key]

        mid_ab = 0.5 * (va + vb)
        mid_bc = 0.5 * (vb + vc)
        mid_ca = 0.5 * (vc + va)

        r_mid_ab = np.linalg.norm(mid_ab - center_of_curvature)
        r_mid_bc = np.linalg.norm(mid_bc - center_of_curvature)
        r_mid_ca = np.linalg.norm(mid_ca - center_of_curvature)

        mid_ab_inside = r_mid_ab <= curvature_radius
        mid_bc_inside = r_mid_bc <= curvature_radius
        mid_ca_inside = r_mid_ca <= curvature_radius

        if np.sum([mid_ab_inside, mid_bc_inside, mid_ca_inside]) > 1:
            pass
        else:
            new_mtl_side[fkey] = mtl_side[fkey]

    facet["materials"][mtl_side_key] = new_mtl_side

    return facet
