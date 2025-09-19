from .. import geometry
from . import template_curved_surface
import numpy as np


def init(
    outer_polygon,
    curvature_radius,
    inner_polygon=None,
    fn_hex_grid=10,
    ref="spherical_cap",
):
    return template_curved_surface.init(
        outer_polygon=outer_polygon,
        curvature_config={"curvature_radius": curvature_radius},
        curvature_height_function=geometry.sphere.surface_height,
        curvature_surface_normal_function=geometry.sphere.surface_normal,
        inner_polygon=inner_polygon,
        fn_hex_grid=fn_hex_grid,
        ref=ref,
    )
