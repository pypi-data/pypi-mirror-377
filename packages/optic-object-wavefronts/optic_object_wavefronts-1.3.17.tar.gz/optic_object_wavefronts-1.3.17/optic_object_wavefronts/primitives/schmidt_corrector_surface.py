from .. import geometry
from . import template_curved_surface
import numpy as np


def init(
    outer_polygon,
    schmidt_corrector_curvature_config,
    inner_polygon=None,
    fn_hex_grid=10,
    ref="schmidt_corrector_surface",
    fill_concave=False,
):
    return template_curved_surface.init(
        outer_polygon=outer_polygon,
        curvature_config=schmidt_corrector_curvature_config,
        curvature_height_function=geometry.schmidt_corrector.surface_height,
        curvature_surface_normal_function=geometry.schmidt_corrector.surface_normal,
        inner_polygon=inner_polygon,
        fn_hex_grid=fn_hex_grid,
        ref=ref,
        fill_concave=fill_concave,
    )
