from .. import mesh
from .. import geometry
from .. import primitives
from .. import polygon
import numpy as np
import posixpath


def make_geometry(
    housing_outer_radius,
    housing_wall_width,
    housing_height,
    lens_curvature_radius,
    lens_fn,
    photosensor_num_on_diagonal,
    photosensor_gap,
    photosensor_plane_distance,
):
    """
    Parameters
    ----------
    housing_outer_radius : float
        Outer radius of hexagonal housing.
    housing_wall_width : float
        Width of walls of housing.
    housing_height
        Height of housung.
    lens_curvature_radius : float
        Curvature radius of biconvex lens. Same curvature on both sides.
    lens_fn : int
        Resolution of lens.
    photosensor_num_on_diagonal : int
        Number of photo-sensors on the long diagonal insisde the hexagonal
        housing.
    photosensor_gap : float
        Gap between photo-sensors.
    photosensor_plane_distance : float
        Distance from lens'
    ref : str
        Name to reference multiple modules.
    """
    assert housing_outer_radius > 0.0
    assert housing_wall_width > 0.0
    assert housing_height > 0.0
    assert photosensor_plane_distance > 0.0
    assert housing_height <= photosensor_plane_distance

    assert lens_fn > 0
    assert lens_curvature_radius > 0.0
    assert photosensor_gap >= 0.0

    c = {}
    c["housing"] = {}
    c["housing"]["outer_radius_outside"] = housing_outer_radius
    c["housing"]["wall_width"] = housing_wall_width
    c["housing"]["height"] = housing_height
    c["housing"]["outer_radius_inside"] = (
        c["housing"]["outer_radius_outside"] - c["housing"]["wall_width"]
    )
    c["housing"]["position"] = np.array(
        [
            0.0,
            0.0,
            photosensor_plane_distance - c["housing"]["height"],
        ]
    )

    c["lens"] = {}
    c["lens"]["curvature_radius"] = lens_curvature_radius
    c["lens"]["outer_radius"] = c["housing"]["outer_radius_outside"]
    c["lens"]["fn"] = lens_fn
    c["lens"]["position"] = np.array([0, 0, 0])

    c["photosensor"] = {}
    c["photosensor"]["grid"] = {}
    c["photosensor"]["grid"]["gap"] = photosensor_gap
    c["photosensor"]["grid"]["num_on_diagonal"] = photosensor_num_on_diagonal
    c["photosensor"]["grid"]["distance_to_lens"] = photosensor_plane_distance

    c["photosensor"]["grid"]["spacing"] = (
        geometry.grid.hexagonal.estimate_spacing_for_small_hexagons_in_big_hexagon(
            big_hexagon_outer_radius=c["housing"]["outer_radius_inside"],
            num_small_hexagons_on_diagonal_of_big_hexagon=c["photosensor"][
                "grid"
            ]["num_on_diagonal"],
        )
    )

    grid_positions_xy = geometry.grid.hexagonal.init_from_spacing(
        spacing=c["photosensor"]["grid"]["spacing"],
        ref="_",
        fN=c["photosensor"]["grid"]["num_on_diagonal"],
    )
    grid_positions_xy = polygon.rotate_z(grid_positions_xy, 0)
    grid_positions_xy = polygon.get_vertices_inside(
        vertices=grid_positions_xy,
        polygon=geometry.regular_polygon.make_vertices_xy(
            outer_radius=c["housing"]["outer_radius_inside"],
            ref="_",
            fn=6,
            rot=0,
        ),
    )
    for gkey in grid_positions_xy:
        grid_positions_xy[gkey][2] = c["photosensor"]["grid"][
            "distance_to_lens"
        ]
    c["photosensor"]["grid"]["positions"] = grid_positions_xy

    c["photosensor"]["bound"] = {}
    c["photosensor"]["bound"]["inner_radius"] = (
        1 / 2 * c["photosensor"]["grid"]["spacing"]
    )
    c["photosensor"]["bound"]["outer_radius"] = (
        2 / np.sqrt(3) * c["photosensor"]["bound"]["inner_radius"]
    )

    c["photosensor"]["body"] = {}
    c["photosensor"]["body"]["inner_radius"] = (
        c["photosensor"]["bound"]["inner_radius"]
        - 0.5 * c["photosensor"]["grid"]["gap"]
    )
    c["photosensor"]["body"]["outer_radius"] = (
        2 / np.sqrt(3) * c["photosensor"]["body"]["inner_radius"]
    )
    return c


def init(
    geometry,
    ref="eye",
):
    join = posixpath.join
    cg = geometry
    camera = mesh.init()

    # grid for photo-sensors
    # ----------------------
    for gi, gkey in enumerate(cg["photosensor"]["grid"]["positions"]):
        photosensor = primitives.disc.init(
            outer_radius=cg["photosensor"]["body"]["outer_radius"],
            fn=6,
            rot=np.pi / 6,
            ref=join(ref, "photosensor_{:06d}".format(gi)),
            prevent_many_faces_share_same_vertex=False,
        )
        photosensor = mesh.translate(
            photosensor,
            cg["photosensor"]["grid"]["positions"][gkey],
        )
        camera = mesh.merge(camera, photosensor)

    # lens
    # ----
    lens = primitives.spherical_lens_hexagonal.init(
        outer_radius=cg["lens"]["outer_radius"],
        curvature_radius=cg["lens"]["curvature_radius"],
        fn=cg["lens"]["fn"],
        ref=join(ref, "lens"),
    )
    camera = mesh.merge(
        camera,
        mesh.translate(lens, cg["lens"]["position"]),
    )

    # housing
    # -------
    pipe = primitives.pipe_hexagonal.init(
        outer_radius=cg["housing"]["outer_radius_outside"],
        inner_radius=cg["housing"]["outer_radius_inside"],
        height=cg["housing"]["height"],
        ref=join(ref, "housing"),
    )

    camera = mesh.merge(
        camera,
        mesh.translate(pipe, cg["housing"]["position"]),
    )

    return camera
