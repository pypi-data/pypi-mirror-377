import numpy as np
import posixpath
import collections
from .. import mesh


def _find_keys(dic, key):
    out = []
    for k in dic:
        if key in k:
            out.append(k)
    return out


def weave_cylinder_faces(mesh, ref, vkey_lower, vkey_upper, norm_sign=1.0):
    assert np.abs(norm_sign) == 1.0

    num_v_lower = len(_find_keys(dic=mesh["vertices"], key=vkey_lower))
    num_v_upper = len(_find_keys(dic=mesh["vertices"], key=vkey_upper))
    assert num_v_lower == num_v_upper
    n = num_v_upper

    side_mtl = ref
    mesh["materials"][side_mtl] = collections.OrderedDict()

    for ni in range(n):
        n_a = int(ni)
        n_b = int(n_a + 1)
        if n_b == n:
            n_b = 0
        n_c = int(ni)
        va_key = posixpath.join(vkey_upper, "{:06d}".format(n_a))
        va = np.array(mesh["vertices"][va_key])
        vb_key = posixpath.join(vkey_upper, "{:06d}".format(n_b))
        vb = np.array(mesh["vertices"][vb_key])
        vc_key = posixpath.join(vkey_lower, "{:06d}".format(n_c))
        vc = np.array(mesh["vertices"][vc_key])
        va[2] = 0.0
        vb[2] = 0.0
        vc[2] = 0.0

        rst_vna_key = posixpath.join(ref, "top", "{:06d}".format(n_a))
        if rst_vna_key not in mesh["vertex_normals"]:
            mesh["vertex_normals"][rst_vna_key] = (
                norm_sign * va / np.linalg.norm(va)
            )

        rst_vnb_key = posixpath.join(ref, "top", "{:06d}".format(n_b))
        if rst_vnb_key not in mesh["vertex_normals"]:
            mesh["vertex_normals"][rst_vnb_key] = (
                norm_sign * vb / np.linalg.norm(vb)
            )

        rsb_vnc_key = posixpath.join(ref, "bot", "{:06d}".format(n_c))
        if rsb_vnc_key not in mesh["vertex_normals"]:
            mesh["vertex_normals"][rsb_vnc_key] = (
                norm_sign * vc / np.linalg.norm(vc)
            )

        mesh["materials"][side_mtl]["ttb_{:06d}".format(ni)] = {
            "vertices": [
                va_key,
                vb_key,
                vc_key,
            ],
            "vertex_normals": [
                rst_vna_key,
                rst_vnb_key,
                rsb_vnc_key,
            ],
        }

    for ni in range(n):
        n_a = int(ni)
        n_b = int(n_a + 1)
        if n_b == n:
            n_b = 0
        n_c = int(ni + 1)
        if n_c == n:
            n_c = 0
        va_key = posixpath.join(vkey_lower, "{:06d}".format(n_a))
        va = np.array(mesh["vertices"][va_key])
        vb_key = posixpath.join(vkey_lower, "{:06d}".format(n_b))
        vb = np.array(mesh["vertices"][vb_key])
        vc_key = posixpath.join(vkey_upper, "{:06d}".format(n_c))
        vc = np.array(mesh["vertices"][vc_key])
        va[2] = 0.0
        vb[2] = 0.0
        vc[2] = 0.0

        rsb_vna_key = posixpath.join(ref, "bot", "{:06d}".format(n_a))
        if rsb_vna_key not in mesh["vertex_normals"]:
            mesh["vertex_normals"][rsb_vna_key] = (
                norm_sign * va / np.linalg.norm(va)
            )

        rsb_vnb_key = posixpath.join(ref, "bot", "{:06d}".format(n_b))
        if rsb_vnb_key not in mesh["vertex_normals"]:
            mesh["vertex_normals"][rsb_vnb_key] = (
                norm_sign * vb / np.linalg.norm(vb)
            )

        rst_vnc_key = posixpath.join(ref, "top", "{:06d}".format(n_c))
        if rst_vnc_key not in mesh["vertex_normals"]:
            mesh["vertex_normals"][rst_vnc_key] = (
                norm_sign * vc / np.linalg.norm(vc)
            )

        mesh["materials"][side_mtl]["bbt_{:06d}".format(ni)] = {
            "vertices": [
                va_key,
                vb_key,
                vc_key,
            ],
            "vertex_normals": [
                rsb_vna_key,
                rsb_vnb_key,
                rst_vnc_key,
            ],
        }

    return mesh


def init(
    top_surface_object,
    bot_surface_object,
    offset,
    fn_polygon,
    fn_hex_grid,
    ref,
    weave_inner_polygon,
):
    top = top_surface_object
    bot = bot_surface_object

    cyl = mesh.init()

    for vkey in top["vertices"]:
        tmp_v = np.array(top["vertices"][vkey])
        # tmp_v[2] = tmp_v[2] + 0.5 * float(offset)
        cyl["vertices"][vkey] = tmp_v
    for fkey in top["faces"]:
        cyl["faces"][fkey] = top["faces"][fkey]
    for vnkey in top["vertex_normals"]:
        cyl["vertex_normals"][vnkey] = +1.0 * top["vertex_normals"][vnkey]

    for vkey in bot["vertices"]:
        tmp_v = np.array(bot["vertices"][vkey])
        tmp_v[2] = tmp_v[2] - float(offset)
        cyl["vertices"][vkey] = tmp_v
    for fkey in bot["faces"]:
        cyl["faces"][fkey] = bot["faces"][fkey]
    for vnkey in bot["vertex_normals"]:
        cyl["vertex_normals"][vnkey] = -1.0 * bot["vertex_normals"][vnkey]

    cyl = weave_cylinder_faces(
        mesh=cyl,
        vkey_lower=posixpath.join(ref, "bot", "outer_bound"),
        vkey_upper=posixpath.join(ref, "top", "outer_bound"),
        ref=posixpath.join(ref, "outer"),
        norm_sign=+1.0,
    )

    if weave_inner_polygon:
        cyl = weave_cylinder_faces(
            mesh=cyl,
            vkey_lower=posixpath.join(ref, "bot", "inner_bound"),
            vkey_upper=posixpath.join(ref, "top", "inner_bound"),
            ref=posixpath.join(ref, "inner"),
            norm_sign=-1.0,
        )

    return cyl
