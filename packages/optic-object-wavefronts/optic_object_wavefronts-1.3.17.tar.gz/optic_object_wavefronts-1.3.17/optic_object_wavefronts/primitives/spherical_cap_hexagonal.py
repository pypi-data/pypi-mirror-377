from .. import mesh
from .. import delaunay
from .. import geometry
import copy
import numpy as np
import posixpath
import collections


def init(outer_radius, curvature_radius, fn=10, ref="spherical_cap_hexagonal"):
    cap = mesh.init()

    cap["vertices"] = geometry.grid.hexagonal.init_from_outer_radius(
        outer_radius=outer_radius, fn=fn, ref=posixpath.join(ref, "inner")
    )

    # elevate z-axis
    # --------------
    for vkey in cap["vertices"]:
        cap["vertices"][vkey][2] = geometry.sphere.surface_height(
            x=cap["vertices"][vkey][0],
            y=cap["vertices"][vkey][1],
            curvature_radius=curvature_radius,
        )

    # vertex-normals
    # --------------
    for vkey in cap["vertices"]:
        vnkey = str(vkey)
        cap["vertex_normals"][vnkey] = geometry.sphere.surface_normal(
            x=cap["vertices"][vkey][0],
            y=cap["vertices"][vkey][1],
            curvature_radius=curvature_radius,
        )

    faces = delaunay.make_faces_xy(vertices=cap["vertices"], ref="")

    mtl_key = ref
    cap["materials"][mtl_key] = collections.OrderedDict()
    for fkey in faces:
        cap["materials"][mtl_key][fkey] = {
            "vertices": faces[fkey]["vertices"],
            "vertex_normals": faces[fkey]["vertices"],
        }

    return cap


def rotate_vertices_xy(vertices, phi):
    cosp = np.cos(phi)
    sinp = np.sin(phi)
    vertices_out = copy.deepcopy(vertices)
    for vkey in vertices_out:
        x = vertices_out[vkey][0]
        y = vertices_out[vkey][1]
        nx = cosp * x - sinp * y
        ny = sinp * x + cosp * y
        vertices_out[vkey][0] = nx
        vertices_out[vkey][1] = ny
    return vertices_out


def weave_hexagon_edges(mesh, outer_radius, margin_width_on_edge, ref):
    assert outer_radius >= 0
    assert margin_width_on_edge >= 0
    inner_radius_hexagon = (
        outer_radius * geometry.regular_polygon.inner_radius(fn=6)
    )
    inner_radius_threshold = inner_radius_hexagon - margin_width_on_edge
    rot_perp = np.pi / 2.0

    mtl_key = ref
    mesh["materials"][mtl_key] = collections.OrderedDict()

    for irotz, phi in enumerate(np.linspace(0, 2 * np.pi, 6, endpoint=False)):
        i_vertices = rotate_vertices_xy(vertices=mesh["vertices"], phi=phi)

        i_combi_vertices = {}
        for fkey in i_vertices:
            if i_vertices[fkey][1] > 0.99 * inner_radius_hexagon:
                i_combi_vertices[fkey] = np.array(
                    [
                        i_vertices[fkey][0],
                        i_vertices[fkey][2],
                        0.0,
                    ]
                )

        i_faces = delaunay.make_faces_xy(
            vertices=i_combi_vertices, ref=ref + "{:d}".format(irotz)
        )

        i_normal = np.array(
            [np.cos(-phi + rot_perp), np.sin(-phi + rot_perp), 0.0]
        )
        i_vnkey = posixpath.join(ref, "{:06d}".format(irotz))

        mesh["vertex_normals"][i_vnkey] = i_normal

        for fkey in i_faces:
            mesh["materials"][mtl_key][fkey] = {
                "vertices": i_faces[fkey]["vertices"],
                "vertex_normals": [i_vnkey, i_vnkey, i_vnkey],
            }

    return mesh
