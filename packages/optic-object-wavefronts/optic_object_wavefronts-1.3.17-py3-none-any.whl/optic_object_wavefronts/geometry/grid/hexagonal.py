import numpy as np
import posixpath
import collections
from . import template
from ... import polygon
import scipy
from scipy import spatial


HEXA = np.array([1.0, 0.0, 0.0])
HEXB = np.array([0.5, np.sqrt(3.0) / 2.0, 0.0])


def init_from_outer_radius(outer_radius=1.0, ref="hex", fn=10):
    spacing = float(outer_radius / fn)
    N = int(fn)
    vertices = collections.OrderedDict()
    for dA in np.arange(-N, N + 1, 1):
        for dB in np.arange(-N, N + 1, 1):
            bound_upper = -dA + N
            bound_lower = -dA - N
            if dB <= bound_upper and dB >= bound_lower:
                vkey = posixpath.join(ref, "{:d}_{:d}".format(dA, dB))
                vertices[vkey] = (dA * HEXA + dB * HEXB) * spacing
    return vertices


def init_from_spacing(spacing=1.0, ref="hex", fN=10):
    """
    Parameters
    ----------
    spacing : float
            The distance between to neighnoring vertices in the grid.
    fN : int
            The number of vertices along the radius of the grid.
    ref : str
            Key in the references for the vertices.

    The vertices are the centers of the hexagons.
    The central vertex is in the origin.

          Y
         _|_
     ___/ | \___
    /   \_|_/   \
    \___/ |_\___/____ x
    /   \___/   \
    \___/   \___/
        \___/
    """
    return template.init(
        fN, vector_A=HEXA, vector_B=HEXB, ref=ref, spacing=spacing
    )


def estimate_spacing_for_small_hexagons_in_big_hexagon(
    big_hexagon_outer_radius,
    num_small_hexagons_on_diagonal_of_big_hexagon,
):
    assert big_hexagon_outer_radius > 0.0

    n = num_small_hexagons_on_diagonal_of_big_hexagon
    assert n > 0
    assert np.mod(n, 2) == 1

    big_hexagon_inner_radius = big_hexagon_outer_radius * np.sqrt(3) / 2

    num_outer_diagonals = np.ceil(n / 2)
    num_radii = np.floor(n / 2)

    outer_diagonal_weight = 2.0 / np.sqrt(3)
    radii_weight = 1.0 / np.sqrt(3)

    spacing = (2 * big_hexagon_inner_radius) / (
        num_outer_diagonals * outer_diagonal_weight + num_radii * radii_weight
    )
    return spacing


def init_voronoi_cells_from_centers(
    centers, centers_spacing, rot=0.0, return_edges=False
):
    """
    Estimate the voronoi-cells of a hexagonal grid.

    Parameters
    ----------
    centers : dict of str -> 3D np.array
        The centers of the unit cells of a hexagonal grid.
    centers_spacing : float
        Distance between neighboring centers.

    Returns
    -------
    voronoi_cells : dict of str -> 3D np.array
        The unit cells of a hexagonal grid.
    """
    rot += 2.0 * np.pi * 1 / 12
    unit_cell_radius = 0.5 * centers_spacing * (2.0 / np.sqrt(3))
    voronoi_cells = {}
    edges = {}

    for key in centers:
        basename = posixpath.basename(key)
        v_str, w_str = str.split(basename, "_")
        v = int(v_str)
        w = int(w_str)

        """
               \
                \
                 \     A-------B
                  \   /         \                     ___
                   \ /           \                ___/
            A-------B    -1, 1    A-------B   ___/
           /         \           /         \ /
          /           \         /           \
         B    -1, 0    A-------B     0, 1    A
          \           /         \           /
           \         /           \         /
            A-------B     0, 0    A-------B
           /         \           /         \
          /           \         /           \
         B     0,-1    A-------B     1, 0    A
          \           /         \           /
           \         /           \         /
            A-------B     1,-1    A-------B
                     \           / \
                      \         /   \
                       A-------B     \
                                      \
                                       \
        """
        edges[key] = []
        for h in np.linspace(0, 5, 6):
            if h == 0:
                vkey = "{:d}_{:d}_{:s}".format(v, w, "A")
            elif h == 1:
                vkey = "{:d}_{:d}_{:s}".format(v, w, "B")
            elif h == 2:
                vkey = "{:d}_{:d}_{:s}".format(v - 1, w, "A")
            elif h == 3:
                vkey = "{:d}_{:d}_{:s}".format(v, w - 1, "B")
            elif h == 4:
                vkey = "{:d}_{:d}_{:s}".format(v, w - 1, "A")
            elif h == 5:
                vkey = "{:d}_{:d}_{:s}".format(v + 1, w - 1, "B")
            else:
                raise RuntimeError("Expected six corners.")

            edges[key].append(vkey)

            if vkey in voronoi_cells:
                continue
            else:
                phi = h / 6.0 * (2.0 * np.pi) + rot
                vertex = np.array(
                    [
                        unit_cell_radius * np.cos(phi) + centers[key][0],
                        unit_cell_radius * np.sin(phi) + centers[key][1],
                        0.0,
                    ]
                )
                voronoi_cells[vkey] = vertex

    if return_edges:
        return voronoi_cells, edges
    else:
        voronoi_cells


def find_hull_of_voronoi_cells(voronoi_cells, centers, centers_spacing):
    """
    Estimate the hull which encloses Voronoi cells.

    Parameters
    ----------
    voronoi_cells : dict of str -> 3D np.array
        The Voronoi cells of a hexagonal grid.
    centers : dict of str -> 3D np.array
        The centers of the Voronoi cells in a hexagonal grid.
    centers_spacing : float
        Distance between neighboring centers.

    Returns
    -------
    hull : dict of str -> 3D np.array
    """
    assert centers_spacing >= 0.0
    assert len(voronoi_cells) >= len(centers)

    spacing = centers_spacing * (2.0 / np.sqrt(3)) * 0.5

    U_keys, U_vertices_3d = polygon.to_keys_and_numpy_array(
        polygon=voronoi_cells
    )
    C_keys, C_vertices_3d = polygon.to_keys_and_numpy_array(polygon=centers)

    # project in xy-plane
    U_vertices = U_vertices_3d[:, 0:2]
    C_vertices = C_vertices_3d[:, 0:2]

    U_tree = scipy.spatial.cKDTree(data=U_vertices)
    C_tree = scipy.spatial.cKDTree(data=C_vertices)

    _ff = U_tree.query_ball_tree(other=C_tree, r=1.1 * spacing)
    U_num_neighbors_in_C = [len(neighbors) for neighbors in _ff]

    num_unit_cell_vertices = len(U_keys)

    # seed vertex
    current_U_vertex = -1
    for i in range(num_unit_cell_vertices):
        if U_num_neighbors_in_C[i] == 1:
            current_U_vertex = i
            break
    assert current_U_vertex >= 0, "Can not find seed-vertex in voronoi_cells."

    hull = collections.OrderedDict()
    hull[current_U_vertex] = U_vertices_3d[current_U_vertex]
    last_vertex = -1

    while True:
        current_U_vertex_neighbors = U_tree.query_ball_point(
            x=U_vertices[current_U_vertex],
            r=1.1 * spacing,
        )

        # remove current_U_vertex itself
        current_U_vertex_neighbors.remove(current_U_vertex)

        # remove last_vertex
        if last_vertex in current_U_vertex_neighbors:
            current_U_vertex_neighbors.remove(last_vertex)

        if len(current_U_vertex_neighbors) == 1:
            # choose the only option
            next_vertex = current_U_vertex_neighbors[0]
        elif len(current_U_vertex_neighbors) == 2:
            # choose the one with less neighbors
            a = current_U_vertex_neighbors[0]
            b = current_U_vertex_neighbors[1]
            if U_num_neighbors_in_C[a] <= U_num_neighbors_in_C[b]:
                next_vertex = a
            else:
                next_vertex = b
        else:
            raise RuntimeError

        if next_vertex in hull:
            # we closed the cycle
            break
        else:
            hull[next_vertex] = U_vertices_3d[next_vertex]
            last_vertex = int(current_U_vertex)
            current_U_vertex = int(next_vertex)

    # rename keys
    hull_with_original_unit_cell_vertex_keys = {}
    for i in hull:
        hull_with_original_unit_cell_vertex_keys[U_keys[i]] = hull[i]

    return hull_with_original_unit_cell_vertex_keys
