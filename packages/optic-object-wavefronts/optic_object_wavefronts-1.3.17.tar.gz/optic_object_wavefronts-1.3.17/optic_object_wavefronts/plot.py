import optic_object_wavefronts as oow
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as plt_Polygon
from mpl_toolkits.mplot3d.art3d import (
    Poly3DCollection,
    Line3DCollection,
    Line3D,
)
import numpy as np


def ax_add_polygon(ax, polygon, closed=True, **kwargs):
    keys = list(polygon.keys())
    for ii in range(len(polygon) - 1):
        s = polygon[keys[ii]]
        e = polygon[keys[ii + 1]]
        ax.plot([s[0], e[0]], [s[1], e[1]], **kwargs)
    if closed:
        s = polygon[keys[-1]]
        e = polygon[keys[0]]
        ax.plot([s[0], e[0]], [s[1], e[1]], **kwargs)


def ax_add_face(
    ax,
    vertices,
    face_color="green",
    face_alpha=0.5,
    face_edge_color="black",
    face_edge_width=0.2,
):
    p = plt_Polygon(
        vertices,
        closed=False,
        facecolor=face_color,
        alpha=face_alpha,
        edgecolor=face_edge_color,
        linewidth=face_edge_width,
    )
    ax.add_patch(p)


def ax_add_mesh_xy(
    ax,
    mesh,
    vertex_color="k",
    vertex_marker="x",
    vertex_marker_size=0.1,
    face_color="green",
    face_alpha=0.5,
    face_edge_color="black",
    face_edge_width=0.2,
):
    for vkey in mesh["vertices"]:
        ax.plot(
            mesh["vertices"][vkey][0],
            mesh["vertices"][vkey][1],
            marker=vertex_marker,
            color=vertex_color,
            markersize=vertex_marker_size,
        )

    for mkey in mesh["materials"]:
        faces = mesh["materials"][mkey]
        for fkey in faces:
            vs = []
            for ii in range(3):
                vkey = faces[fkey]["vertices"][ii]
                vs.append(mesh["vertices"][vkey][0:2])
            vs = np.array(vs)
            ax_add_face(
                ax=ax,
                vertices=vs,
                face_alpha=face_alpha,
                face_color=face_color,
                face_edge_color=face_edge_color,
                face_edge_width=face_edge_width,
            )


def plot_mesh(mesh):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.set_aspect("equal")
    ax_add_mesh_xy(ax=ax, mesh=mesh)
    plt.show()


def fig_ax_3d(figsize=(4, 4), dpi=320):
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, projection="3d")
    ax.grid(False)
    ax.axes.set_xlim3d(left=-1, right=1)
    ax.axes.set_ylim3d(bottom=-1, top=1)
    ax.axes.set_zlim3d(bottom=-1, top=1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    return fig, ax


def ax_aspect_equal_3d(ax):
    extents = np.array(
        [getattr(ax, "get_{}lim".format(dim))() for dim in "xyz"]
    )
    sz = extents[:, 1] - extents[:, 0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize / 2
    for ctr, dim in zip(centers, "xyz"):
        getattr(ax, "set_{}lim".format(dim))(ctr - r, ctr + r)


def ax_add_mesh_3d(
    ax,
    mesh,
    face_edge_width=1.0,
    face_edge_color="black",
    face_color="white",
    material_colors={},
    face_alpha=0.5,
    vertex_normal_color="pink",
    vertex_normal_width=0.5,
    vertex_normal_length=0.05,
    vertex_normal_alpha=1.0,
    zorder=1,
):
    obj = oow.export.reduce_mesh_to_obj(mesh)

    vertices = [(v[0], v[1], v[2]) for v in obj["v"]]

    # faces
    # -----
    polygons = []
    facecolors = []
    edgecolors = []
    linewidths = []
    for material in obj["mtl"]:
        for face in obj["mtl"][material]:
            polygons.append(
                [
                    vertices[face["v"][0]],
                    vertices[face["v"][1]],
                    vertices[face["v"][2]],
                ]
            )

            edgecolors.append(face_edge_color)
            linewidths.append(face_edge_width)

            if material in material_colors:
                facecolors.append(material_colors[material])
            else:
                facecolors.append(face_color)

    # normals
    # -------
    for material in obj["mtl"]:
        for face in obj["mtl"][material]:
            for n in range(3):
                normal = vertex_normal_length * np.array(
                    obj["vn"][face["vn"][n]]
                )
                start = obj["v"][face["v"][n]]
                stop = start + normal

                polygons.append(
                    [
                        start,
                        stop,
                        stop,
                    ]
                )

                edgecolors.append(vertex_normal_color)
                linewidths.append(vertex_normal_width)
                facecolors.append("None")

    ax.add_collection3d(
        Poly3DCollection(
            polygons,
            edgecolors=edgecolors,
            facecolors=facecolors,
            linewidths=linewidths,
            alpha=face_alpha,
            zorder=zorder,
        )
    )
