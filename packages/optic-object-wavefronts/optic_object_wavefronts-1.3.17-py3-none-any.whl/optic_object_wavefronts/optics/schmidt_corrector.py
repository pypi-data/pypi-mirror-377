import numpy as np


def surface_height(
    radius,
    config,
):
    sc = config

    relative_aperture_radius_rho = radius / sc["corrector_aperture_radius_d"]
    rho = relative_aperture_radius_rho

    Rc = sc["corrector_plate_radius_of_curvature_Rc"]
    d = sc["corrector_aperture_radius_d"]
    A1 = sc["aspheric_parameter_A1"]
    A2 = sc["aspheric_parameter_A2"]

    first = (rho * d) ** 2 / (2.0 * Rc)
    second = A1 * (rho * d) ** 4
    third = A2 * (rho * d) ** 6

    return first + second + third


def init_config(
    refractive_index_corrector_n=1.5185,
    refractive_index_sourrounding_n_tick=1.0,
    corrector_aperture_radius_d=100,
    mirror_radius_of_curvature_R=-800,
    relative_focus_delta=1.0,
):
    """
    cite: sacek2024telescope
    """
    assert mirror_radius_of_curvature_R < 0.0
    assert corrector_aperture_radius_d > 0.0
    assert 0.0 < relative_focus_delta <= 2.0
    assert refractive_index_sourrounding_n_tick > 0.0
    assert refractive_index_corrector_n > 0.0

    F = schmidt_focal_ratio_F(
        mirror_radius_of_curvature_R=mirror_radius_of_curvature_R,
        corrector_aperture_radius_d=corrector_aperture_radius_d,
    )

    b = thrird_order_aspheric_coefficient_b(
        relative_focus_delta=relative_focus_delta,
        schmidt_focal_ratio_F=F,
        mirror_radius_of_curvature_R=mirror_radius_of_curvature_R,
    )

    b_tick = fifth_order_aspheric_coefficient_b_tick(
        mirror_radius_of_curvature_R=mirror_radius_of_curvature_R,
    )

    A1 = aspheric_parameter_A1(
        thrird_order_aspheric_coefficient_b=b,
        refractive_index_corrector_n=refractive_index_corrector_n,
        refractive_index_sourrounding_n_tick=refractive_index_sourrounding_n_tick,
    )

    A2 = aspheric_parameter_A2(
        fifth_order_aspheric_coefficient_b_tick=b_tick,
        refractive_index_corrector_n=refractive_index_corrector_n,
        refractive_index_sourrounding_n_tick=refractive_index_sourrounding_n_tick,
    )

    Rc = corrector_plate_radius_of_curvature_Rc(
        relative_focus_delta=relative_focus_delta,
        aspheric_parameter_A1=A1,
        corrector_aperture_radius_d=corrector_aperture_radius_d,
    )

    return {
        "refractive_index_corrector_n": refractive_index_corrector_n,
        "refractive_index_sourrounding_n_tick": refractive_index_sourrounding_n_tick,
        "corrector_aperture_radius_d": corrector_aperture_radius_d,
        "mirror_radius_of_curvature_R": mirror_radius_of_curvature_R,
        "relative_focus_delta": relative_focus_delta,
        "schmidt_focal_ratio_F": schmidt_focal_ratio_F,
        "thrird_order_aspheric_coefficient_b": b,
        "fifth_order_aspheric_coefficient_b_tick": b_tick,
        "aspheric_parameter_A1": A1,
        "aspheric_parameter_A2": A2,
        "corrector_plate_radius_of_curvature_Rc": Rc,
    }


def schmidt_focal_ratio_F(
    mirror_radius_of_curvature_R,
    corrector_aperture_radius_d,
):
    return -1.0 * (mirror_radius_of_curvature_R / corrector_aperture_radius_d)


def thrird_order_aspheric_coefficient_b(
    relative_focus_delta,
    schmidt_focal_ratio_F,
    mirror_radius_of_curvature_R,
):
    R = mirror_radius_of_curvature_R
    F = schmidt_focal_ratio_F
    D = relative_focus_delta
    b = 2.0 * (1 - D / (16.0 * (F**2))) / (R**3)
    return b


def fifth_order_aspheric_coefficient_b_tick(mirror_radius_of_curvature_R):
    R = mirror_radius_of_curvature_R
    return 6.0 / (R**5)


def aspheric_parameter_A1(
    thrird_order_aspheric_coefficient_b,
    refractive_index_corrector_n,
    refractive_index_sourrounding_n_tick,
):
    n = refractive_index_corrector_n
    n_tick = refractive_index_sourrounding_n_tick
    b = thrird_order_aspheric_coefficient_b
    return b / (8 * (n_tick - n))


def aspheric_parameter_A2(
    fifth_order_aspheric_coefficient_b_tick,
    refractive_index_corrector_n,
    refractive_index_sourrounding_n_tick,
):
    n = refractive_index_corrector_n
    n_tick = refractive_index_sourrounding_n_tick
    b_tick = fifth_order_aspheric_coefficient_b_tick
    return b_tick / (16 * (n_tick - n))


def corrector_plate_radius_of_curvature_Rc(
    relative_focus_delta,
    aspheric_parameter_A1,
    corrector_aperture_radius_d,
):
    D = relative_focus_delta
    A1 = aspheric_parameter_A1
    d = corrector_aperture_radius_d

    return -1 / (2 * D * A1 * d**2)
