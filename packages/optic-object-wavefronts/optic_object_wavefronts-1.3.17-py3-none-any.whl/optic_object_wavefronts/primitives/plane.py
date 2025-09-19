from .. import geometry
from . import template_curved_surface
import numpy as np


def init(
    outer_polygon,
    inner_polygon=None,
    fn_hex_grid=10,
    ref="plane",
    fill_concave=False,
):
    return template_curved_surface.init(
        outer_polygon=outer_polygon,
        curvature_config={},
        curvature_height_function=geometry.plane.surface_height,
        curvature_surface_normal_function=geometry.plane.surface_normal,
        inner_polygon=inner_polygon,
        fn_hex_grid=fn_hex_grid,
        ref=ref,
        fill_concave=fill_concave,
    )
