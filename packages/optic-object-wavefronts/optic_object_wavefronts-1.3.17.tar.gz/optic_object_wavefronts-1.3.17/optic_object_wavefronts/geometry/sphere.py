import numpy as np


def _assert_valid(distance_to_z_axis, curvature_radius):
    assert np.abs(curvature_radius) >= distance_to_z_axis
    assert distance_to_z_axis >= 0.0


def surface_height(x, y, curvature_radius):
    distance_to_z_axis = np.hypot(x, y)
    _assert_valid(distance_to_z_axis, curvature_radius)
    sig = np.sign(curvature_radius)
    h = np.abs(curvature_radius) - np.sqrt(
        curvature_radius**2 - distance_to_z_axis**2
    )
    return sig * h


def surface_normal(x, y, curvature_radius):
    distance_to_z_axis = np.hypot(x, y)
    _assert_valid(distance_to_z_axis, curvature_radius)
    center_or_sphere = np.array([0.0, 0.0, curvature_radius])
    point_on_sphere = np.array([x, y, surface_height(x, y, curvature_radius)])
    diff = center_or_sphere - point_on_sphere
    return np.sign(curvature_radius) * diff / np.linalg.norm(diff)
