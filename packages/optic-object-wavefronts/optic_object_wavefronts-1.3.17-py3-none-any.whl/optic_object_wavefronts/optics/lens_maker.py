"""
The lens-maker-equation for a bi-convex, lens with equal
curvature-radii on both caps.
"""

import numpy as np


def estimate_curvature_radius(
    focal_length,
    aperture_radius,
    refractive_index,
    max_deviation_for_focal_length=1e-6,
    max_num_iterations=1000,
):
    """
    Returns the curvature-radius of a bi-convex lens according
    to the lens-maker-equation.

    Parameters
    ----------
    focal_length : float
            The desired focal-length of the bi-convex lens.
    aperture_radius : float
            The radius of the lens' aperture where the light passes through.
    refractive_index : float
            The refractive index by which the speed of light is
            reduced inside the lens' material.
    max_deviation_for_focal_length : float
            The max deviation between the desired and estimated focal-length.
    max_num_iterations : int
            Assert the max num. of iterations.
    """
    assert focal_length > 0.0
    assert aperture_radius > 0.0
    assert refractive_index > 1.0
    assert max_deviation_for_focal_length < focal_length
    assert max_deviation_for_focal_length > 0.0
    assert max_num_iterations > 0

    curvature_radius = float(focal_length)  # start point
    deviation = float(focal_length)  # start point
    num_iterations = 0

    while np.abs(deviation) > max_deviation_for_focal_length:
        assert num_iterations < max_num_iterations

        curvature_radius = curvature_radius - deviation * 0.1

        thickness = estimate_thickness(
            curvature_radius=curvature_radius, aperture_radius=aperture_radius
        )

        expected_focal_length = estimate_focal_length(
            curvature_radius=curvature_radius,
            thickness=thickness,
            refractive_index=refractive_index,
        )

        deviation = expected_focal_length - focal_length
        num_iterations += 1

    return curvature_radius


def estimate_thickness(
    curvature_radius,
    aperture_radius,
):
    """
    Returns the thickness of a bi-convex lens

    Parameters
    ----------
    curvature_radius : float
            The curving radius of the two caps of the lens.
    aperture_radius : float
            The radius of the lens' aperture where the light passes through.
    """
    R = curvature_radius
    r = aperture_radius
    return 2.0 * R - 2.0 * np.sqrt(R * R - r * r)


def estimate_focal_length(
    curvature_radius,
    thickness,
    refractive_index,
):
    """
    Returns the expected focal-length of a bi-convex lens according to the
    lens-maker-equation.

    Parameters
    ----------
    curvature_radius : float
            The curving radius of the two caps of the lens.
    thickness : float
            The thickness along the optical axis from cap to cap.
    refractive_index : float
            The refractive index by which the speed of light is
            reduced inside the lens' material.
    """
    R = curvature_radius
    n = refractive_index
    t = thickness
    f_inv = (n - 1.0) * (2.0 / R - ((n - 1.0) * t) / (n * R * R))
    return 1.0 / f_inv
