import copy
import collections
import numpy as np
from . import version


def init():
    """
    Returns a mesh which describes meshes of triangular faces.
    A mesh can have multiple materials.
    This is the basic building.
    Finally it can be exported to an object-wavefront (.obj).
    """
    return {
        "vertices": collections.OrderedDict(),
        "vertex_normals": collections.OrderedDict(),
        "materials": collections.OrderedDict(),
    }


def translate(mesh, v):
    """
    Returns a translated copy of the mesh.

    Parameters
    ----------
    mesh : dict
            The mesh.
    v : numpy.array
            Three dimensional vector for translation.
    """
    v = np.array(v)
    out = copy.deepcopy(mesh)
    for vkey in out["vertices"]:
        out["vertices"][vkey] += v
    return out


def merge(a, b):
    """
    Returns a new mesh merged out of the objects a, and b.

    Parameters
    ----------
    a : dict
            The mesh a.
    b : dict
            The mesh b.
    """
    out = copy.deepcopy(a)
    for vkey in b["vertices"]:
        assert vkey not in out["vertices"]
        out["vertices"][vkey] = copy.deepcopy(b["vertices"][vkey])
    for vnkey in b["vertex_normals"]:
        assert vnkey not in out["vertex_normals"]
        out["vertex_normals"][vnkey] = copy.deepcopy(
            b["vertex_normals"][vnkey]
        )
    for mkey in b["materials"]:
        assert mkey not in out["materials"]
        out["materials"][mkey] = copy.deepcopy(b["materials"][mkey])
    return out


def remove_unused_vertices_and_vertex_normals(mesh):
    """
    Returns a new mesh with all unused vertices and vertex-normals removed.

    Parameters
    ----------
    mesh : dict
            The mesh.
    """
    out = init()
    out["materials"] = copy.deepcopy(mesh["materials"])

    valid_vkeys = set()
    for mkey in out["materials"]:
        for fkey in out["materials"][mkey]:
            for vkey in out["materials"][mkey][fkey]["vertices"]:
                valid_vkeys.add(vkey)

    for vkey in mesh["vertices"]:
        if vkey in valid_vkeys:
            out["vertices"][vkey] = mesh["vertices"][vkey]

    valid_vnkeys = set()
    for mkey in out["materials"]:
        for fkey in out["materials"][mkey]:
            for vnkey in out["materials"][mkey][fkey]["vertex_normals"]:
                valid_vnkeys.add(vnkey)

    for vnkey in mesh["vertex_normals"]:
        if vnkey in valid_vnkeys:
            out["vertex_normals"][vnkey] = mesh["vertex_normals"][vnkey]

    return out
