from .. import mesh
from .. import delaunay
from .. import geometry
import numpy as np
import collections


def init(
    outer_radius,
    curvature_radius,
    fn_hex_grid=10,
    ref="spherical_pixel_cap",
):
    cap = mesh.init()
    cap["vertices"] = geometry.grid.hexagonal.init_from_outer_radius(
        outer_radius=2.0 * outer_radius, ref="hex", fn=fn_hex_grid
    )

    for k in cap["vertices"]:
        cap["vertices"][k][2] = geometry.sphere.surface_height(
            x=cap["vertices"][k][0],
            y=cap["vertices"][k][1],
            curvature_radius=curvature_radius,
        )

    for k in cap["vertices"]:
        cap["vertex_normals"][k] = geometry.sphere.surface_normal(
            x=cap["vertices"][k][0],
            y=cap["vertices"][k][1],
            curvature_radius=curvature_radius,
        )

    mtl_key = ref
    cap["materials"][mtl_key] = collections.OrderedDict()

    all_grid_faces = delaunay.make_faces_xy(vertices=cap["vertices"], ref=ref)

    for fkey in all_grid_faces:
        vkey_a = all_grid_faces[fkey]["vertices"][0]
        vkey_b = all_grid_faces[fkey]["vertices"][1]
        vkey_c = all_grid_faces[fkey]["vertices"][2]

        va = cap["vertices"][vkey_a]
        vb = cap["vertices"][vkey_b]
        vc = cap["vertices"][vkey_c]

        ra = np.hypot(va[0], va[1])
        rb = np.hypot(vb[0], vb[1])
        rc = np.hypot(vc[0], vc[1])

        if ra <= outer_radius and rb <= outer_radius and rc <= outer_radius:
            cap["materials"][mtl_key][fkey] = all_grid_faces[fkey]
            cap["materials"][mtl_key][fkey]["vertex_normals"] = [
                vkey_a,
                vkey_b,
                vkey_c,
            ]

    return mesh.remove_unused_vertices_and_vertex_normals(mesh=cap)
