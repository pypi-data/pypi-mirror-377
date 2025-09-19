import triangle_mesh_io as tmi
from . import mesh
import copy


def reduce_mesh_to_obj(m):
    """
    The mesh has hashable keys to address vertices and normals.
    The object-wavefront replaces those with numeric indices.
    """
    v_dict = {}
    for vi, vkey in enumerate(m["vertices"]):
        v_dict[vkey] = vi
    vn_dict = {}
    for vni, vnkey in enumerate(m["vertex_normals"]):
        vn_dict[vnkey] = vni

    obj = tmi.obj.init()

    for vkey in m["vertices"]:
        obj["v"].append(m["vertices"][vkey])
    for vnkey in m["vertex_normals"]:
        obj["vn"].append(m["vertex_normals"][vnkey])

    for mkey in m["materials"]:
        mtl_faces = m["materials"][mkey]
        obj["mtl"][mkey] = []

        for fkey in mtl_faces:
            vs = []
            for dim in range(3):
                vs.append(v_dict[mtl_faces[fkey]["vertices"][dim]])
            vns = []
            for dim in range(3):
                vns.append(vn_dict[mtl_faces[fkey]["vertex_normals"][dim]])
            obj["mtl"][mkey].append({"v": vs, "vn": vns})

    return obj


def restore_mesh_from_obj(o):
    m = mesh.init()

    for i, v in enumerate(o["v"]):
        vkey = "{:d}".format(i)
        m["vertices"][vkey] = v

    for i, vn in enumerate(o["vn"]):
        vnkey = "{:d}".format(i)
        m["vertex_normals"][vnkey] = vn

    for mkey in o["mtl"]:
        m["materials"][mkey] = {}

        for i, f in enumerate(o["mtl"][mkey]):
            fkey = "{:d}".format(i)
            m["materials"][mkey][fkey] = {}

            m["materials"][mkey][fkey]["vertices"] = [None, None, None]
            for dim in [0, 1, 2]:
                refvkey = "{:d}".format(f["v"][dim])
                m["materials"][mkey][fkey]["vertices"][dim] = refvkey

            m["materials"][mkey][fkey]["vertex_normals"] = [None, None, None]
            for dim in [0, 1, 2]:
                refvnkey = "{:d}".format(f["vn"][dim])
                m["materials"][mkey][fkey]["vertex_normals"][dim] = refvnkey
    return m


def reduce_mesh_to_off(m, materials=None):
    """
    Reduces a mesh into an off.
    Offs do not have surface-normals.
    """
    obj = reduce_mesh_to_obj(m)
    off = tmi.off.init()

    off["v"] = copy.copy(obj["v"])

    if not materials:
        materials = list(obj["mtl"].keys())

    for mtl in materials:
        for obface in obj["mtl"][mtl]:
            off["f"].append(obface["v"])

    return off
