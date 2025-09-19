import numpy as np
from . import template


UNITA = np.array([1.0, 0.0, 0.0])
UNITB = np.array([0.0, 1.0, 0.0])


def init_from_spacing(spacing=1.0, ref="rectangular", fN=10):
    """
    Parameters
    ----------
    spacing : float
            The distance between to neighboring vertices in the grid.
    fN : int
            The number of vertices along the radius of the grid.
    ref : str
            Key in the references for the vertices.
    """
    return template.init(
        fN, vector_A=UNITA, vector_B=UNITB, ref=ref, spacing=spacing
    )
