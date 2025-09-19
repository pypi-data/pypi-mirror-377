from .. import mesh
from .. import delaunay
from .. import geometry
from .. import polygon
import posixpath
import numpy as np
import collections
import copy


def init(
    outer_polygon,
    curvature_config,
    curvature_height_function,
    curvature_surface_normal_function,
    inner_polygon=None,
    fn_hex_grid=10,
    ref="curved_surface",
    eps=1e-6,
    vs_hex_grid=None,
    fill_concave=False,
):
    """
    Returns an object that describes a curved 2d surface. The user provides
    f unctions which control the curvature's height and surface-normal.

    outer_polygon : 2D-polygon-dict
            The outer bound of the surface.
    curvature_config : dict
            The config of the curvature. This is fed to the height-, and
            surface-normal-function.
    curvature_height_function : function
            Takes arguments x, y, and **curvature_config.
            Is expected to return the height z.
    curvature_surface_normal_function : function
            Takes arguments x, y, and **curvature_config.
            Is expected to return the surface-normal.
    inner_polygon : 2D-polygon-dict
            The inner bound of the surface.
    fn_hex_grid : int
            Number of vertices along the radius in grid. Must be None when
            vs_hex_grid is used instead.
    vs_hex_grid : float (mutual excludes fn_hex_grid)
            Spacing of vertices in the grid.
    ref : string
            The name of the surface.
    """
    outer_limits = polygon.limits(outer_polygon)
    safe_outer_radius_xy = 1.5 * np.max(
        [np.max(np.abs(outer_limits[0])), np.max(np.abs(outer_limits[1]))]
    )

    if vs_hex_grid is None:
        assert fn_hex_grid is not None
        _outer_radius = safe_outer_radius_xy
        _fn_hex_grid = fn_hex_grid
    else:
        assert vs_hex_grid > 0.0
        assert fn_hex_grid is None
        _fn_hex_grid = np.ceil(safe_outer_radius_xy / vs_hex_grid)
        _outer_radius = vs_hex_grid * _fn_hex_grid

    hex_vertices = geometry.grid.hexagonal.init_from_outer_radius(
        outer_radius=_outer_radius,
        fn=_fn_hex_grid,
        ref=posixpath.join(ref, "grid"),
    )

    hex_vertices_valid = polygon.get_vertices_inside(
        vertices=hex_vertices, polygon=outer_polygon
    )

    if inner_polygon is not None:
        hex_vertices_valid = polygon.get_vertices_outside(
            vertices=hex_vertices_valid, polygon=inner_polygon
        )

    mes = mesh.init()

    for k in hex_vertices_valid:
        mes["vertices"][k] = hex_vertices_valid[k]

    # outer_polygon
    # -------------
    if fill_concave:
        mes["vertices"] = polygon.remove_first_from_second_when_too_close(
            first=outer_polygon,
            second=mes["vertices"],
            eps=eps,
        )
        outer_polygon = delaunay.fill_polygon_xy(
            poly=outer_polygon,
            vertices=mes["vertices"],
            ref=determine_polygons_ref(outer_polygon),
        )
    for k in outer_polygon:
        vkey = posixpath.join(ref, k)
        mes["vertices"][vkey] = copy.deepcopy(outer_polygon[k])

    if inner_polygon is not None:
        # inner_polygon
        # -------------
        if fill_concave:
            mes["vertices"] = polygon.remove_first_from_second_when_too_close(
                first=inner_polygon,
                second=mes["vertices"],
                eps=eps,
            )
            inner_polygon = delaunay.fill_polygon_xy(
                poly=inner_polygon,
                vertices=mes["vertices"],
                ref=determine_polygons_ref(inner_polygon),
            )
        for k in inner_polygon:
            vkey = posixpath.join(ref, k)
            mes["vertices"][vkey] = copy.deepcopy(inner_polygon[k])

    for k in mes["vertices"]:
        mes["vertices"][k][2] = curvature_height_function(
            x=mes["vertices"][k][0],
            y=mes["vertices"][k][1],
            **curvature_config,
        )

    for k in mes["vertices"]:
        mes["vertex_normals"][k] = curvature_surface_normal_function(
            x=mes["vertices"][k][0],
            y=mes["vertices"][k][1],
            **curvature_config,
        )

    faces = delaunay.make_faces_xy(vertices=mes["vertices"], ref=ref)

    mes["materials"][ref] = collections.OrderedDict()

    mtl_key = ref
    for fkey in faces:
        mes["materials"][mtl_key][fkey] = {
            "vertices": faces[fkey]["vertices"],
            "vertex_normals": faces[fkey]["vertices"],
        }

    if inner_polygon is not None:
        mask_faces_in_inner = polygon.mask_face_inside(
            vertices=mes["vertices"],
            faces=mes["materials"][mtl_key],
            polygon=inner_polygon,
        )
        fkeys_to_be_removed = []
        for idx, fkey in enumerate(mes["materials"][mtl_key]):
            if mask_faces_in_inner[idx]:
                fkeys_to_be_removed.append(fkey)
        for fkey in fkeys_to_be_removed:
            mes["materials"][mtl_key].pop(fkey)

    return mesh.remove_unused_vertices_and_vertex_normals(mesh=mes)


def determine_polygons_ref(poly):
    dirnames = [posixpath.dirname(p) for p in poly]
    dirnames = list(set(dirnames))
    assert len(dirnames) == 1
    return dirnames[0]
