import numpy as np
import os
import posixpath
import collections
import scipy
from scipy import spatial as scipy_spatial
from . import polygon
from . import geometry


def make_faces_xy(vertices, ref):
    """
    Create triangular faces based on the vertices x, and y components.

    Parameters
    ----------
    vertices : dict
            The vertices to make triangular faces for.
    ref : str
            The key for the faces keys.

    Returns
    -------
    faces : dict
            The faces for the vertices, referencing the vertices by key.
    """
    vkeys, vertices = polygon.to_keys_and_numpy_array(polygon=vertices)
    vertices_xy = vertices[:, 0:2]

    del_tri = scipy.spatial.Delaunay(points=vertices_xy)
    del_faces = del_tri.simplices

    faces = {}
    for fidx, del_face in enumerate(del_faces):
        fkey = os.path.join(ref, "{:06d}".format(fidx))
        faces[fkey] = {
            "vertices": [
                vkeys[del_face[0]],
                vkeys[del_face[1]],
                vkeys[del_face[2]],
            ],
        }
    return faces


def fill_polygon_xy(
    poly, vertices, ref="poly", eps=1e-6, max_iterations=10 * 1000
):
    """
    Inserts additional vertives into the polygon 'poly' in order to make
    sure that the points along the polygon are closer to each other than to
    the outer vertices.
    This ensures that delauny triangles will a not cross the segments of the
    polygon.
    This is important e.g. for inner polygons which are not perfectly convex
    but have carvings.
    Only the xy-components are considered.

    Parameters
    ----------
    poly : OrderedDict (str, 3d array)
        A closed loop polygon
    vertices : dict (str, 3d array)
        Vertices of the mesh (excluding the vertices of the polygon)
    eps : float
        Do not fill point into segement of polygon when the new point is
        closer than 'eps' to either the start or the stop vertex of the
        segement.
    max_iterations : int
        Raise RuntimeError when more than 'max_iterations' are needed to
        insert new mid-points into the polygon.

    Returns
    -------
    poly : OrderedDict (str, 3d array)
        Same vertices as in the input poly but with additional vertices in
        between when needed.
    """
    num_iterations = 0
    while True:
        if num_iterations > max_iterations:
            raise RuntimeError("Did not expect this many iterations.")

        next_poly = _fill_middle_in_polygon_segment_xy(
            poly=poly,
            vertices=vertices,
            ref=ref,
            eps=eps,
        )

        if len(next_poly) == len(poly):
            break
        else:
            poly = next_poly
        num_iterations += 1

    return poly


def _fill_middle_in_polygon_segment_xy(poly, vertices, ref="poly", eps=1e-6):
    vxy = np.zeros(shape=(len(vertices), 2), dtype=float)
    vnames = []
    for i, vkey in enumerate(vertices):
        vxy[i] = vertices[vkey][0:2]
        vnames.append(vkey)

    tree = scipy_spatial.cKDTree(data=vxy)

    outpoly = collections.OrderedDict()

    vkeys = list(poly.keys())
    iii = 0
    for s in range(len(vkeys)):
        start_vkey, stop_key = cycle_segment_keys(vkeys, s)
        vstart = poly[start_vkey]
        vstop = poly[stop_key]

        segment = geometry.line.Line(start=vstart[0:2], stop=vstop[0:2])

        matches_start = set(
            tree.query_ball_point(x=vstart[0:2], r=segment.length)
        )
        matches_stop = set(
            tree.query_ball_point(x=vstop[0:2], r=segment.length)
        )
        matches = list(matches_start.union(matches_stop))

        # add segment's start point to output in any case
        iii, outkey = bumb_index(iii=iii, ref=ref)
        outpoly[outkey] = poly[start_vkey]

        inter_match = []
        inter_paras = []
        for vmatch in matches:
            para = segment.parameter_for_closest_distance_to_point(vxy[vmatch])
            if 0 <= para <= segment.length:
                inter_match.append(vmatch)
                inter_paras.append(para)
        inter_match = np.array(inter_match)
        inter_paras = np.array(inter_paras)

        if len(inter_match) > 0:
            imiddle = np.argmin(np.abs(inter_paras - 0.5 * segment.length))
            segment_parameter = inter_paras[imiddle]
            if eps < segment_parameter < segment.length - eps:
                ivert = segment.at(parameter=segment_parameter)
                iii, outkey = bumb_index(iii=iii, ref=ref)
                outpoly[outkey] = np.array([ivert[0], ivert[1], 0.0])

    return outpoly


def cycle_segment_keys(keys, i):
    start, stop = cycle_segment(num=len(keys), i=i)
    return keys[start], keys[stop]


def cycle_segment(num, i):
    assert num >= 0
    i = i % num
    j = i + 1
    j = j % num
    return i, j


def bumb_index(iii, ref):
    return iii + 1, posixpath.join(ref, "{:06d}".format(iii))
