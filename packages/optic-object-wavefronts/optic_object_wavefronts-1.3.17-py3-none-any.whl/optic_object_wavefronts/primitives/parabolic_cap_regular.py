from .. import geometry
from . import parabolic_cap
import posixpath
import collections


def init(
    outer_radius,
    focal_length,
    inner_radius=None,
    fn_polygon=17,
    fn_hex_grid=10,
    ref="spherical_cap_regular",
    rot=0.0,
):
    outer_polygon = geometry.regular_polygon.make_vertices_xy(
        outer_radius=outer_radius,
        fn=fn_polygon,
        ref="outer_bound",
        rot=rot,
    )

    if inner_radius is not None:
        inner_polygon = geometry.regular_polygon.make_vertices_xy(
            outer_radius=inner_radius,
            fn=fn_polygon,
            ref="inner_bound",
            rot=rot,
        )
    else:
        inner_polygon = None

    return parabolic_cap.init(
        outer_polygon=outer_polygon,
        inner_polygon=inner_polygon,
        fn_hex_grid=fn_hex_grid,
        focal_length=focal_length,
        ref=ref,
    )
