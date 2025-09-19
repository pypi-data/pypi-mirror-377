import numpy as np
from .. import optics


def init_schmidt_corrector_curvature_config(
    corrector_aperture_radius,
    mirror_radius_of_curvature,
    refractive_index_corrector,
    refractive_index_surrounding,
    relative_focus_delta=1.0,
):
    params = optics.schmidt_corrector.init_config(
        refractive_index_corrector_n=refractive_index_corrector,
        refractive_index_sourrounding_n_tick=refractive_index_surrounding,
        corrector_aperture_radius_d=corrector_aperture_radius,
        mirror_radius_of_curvature_R=mirror_radius_of_curvature,
        relative_focus_delta=relative_focus_delta,
    )

    return {
        "aspheric_parameter_A1": params["aspheric_parameter_A1"],
        "aspheric_parameter_A2": params["aspheric_parameter_A2"],
        "corrector_plate_radius_of_curvature_Rc": params[
            "corrector_plate_radius_of_curvature_Rc"
        ],
    }


def surface_height(
    x,
    y,
    aspheric_parameter_A1,
    aspheric_parameter_A2,
    corrector_plate_radius_of_curvature_Rc,
):
    A1 = aspheric_parameter_A1
    A2 = aspheric_parameter_A2
    Rc = corrector_plate_radius_of_curvature_Rc
    r = np.hypot(x, y)
    z = (r**2) / (2 * Rc) + A1 * (r**4) + A2 * (r**6)
    return z


def surface_normal(
    x,
    y,
    aspheric_parameter_A1,
    aspheric_parameter_A2,
    corrector_plate_radius_of_curvature_Rc,
    delta=1e-6,
):
    """
    surface-normal is: ( -dz/dx , -dz/dy , 1 )
    """
    A1 = aspheric_parameter_A1
    A2 = aspheric_parameter_A2
    Rc = corrector_plate_radius_of_curvature_Rc

    xp = x + delta
    xm = x - delta
    yp = y + delta
    ym = y - delta
    z_xp = surface_height(xp, y, A1, A2, Rc)
    z_xm = surface_height(xm, y, A1, A2, Rc)
    z_yp = surface_height(x, yp, A1, A2, Rc)
    z_ym = surface_height(x, ym, A1, A2, Rc)
    dzdx = (z_xp - z_xm) / (2 * delta)
    dzdy = (z_yp - z_ym) / (2 * delta)
    normal = [-dzdx, -dzdy, 1.0]
    return normal / np.linalg.norm(normal)
