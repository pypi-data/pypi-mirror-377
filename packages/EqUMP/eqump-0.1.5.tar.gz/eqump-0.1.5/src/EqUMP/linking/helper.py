import numpy as np
from typing import Tuple

def transform_item_params(
    a: np.ndarray, b: np.ndarray, A: float, B: float, direction: str
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Transform item parameters according to Stocking-Lord/Haebara A, B.
    direction: 'to_old' (new -> old) or 'to_new' (old -> new)

    Parameters
    ----------
    a : np.ndarray
        item parameters a
    b : np.ndarray
        item parameters b
    A : float
        transformation constant A
    B : float
        transformation constant B
    """
    if direction == 'to_old':
        # new form → old scale
        a_star = a / A
        b_star = (b - B) / A
    elif direction == 'to_new':
        # old form → new scale
        a_star = a * A
        b_star = A * b + B
    else:
        raise ValueError(f"Invalid direction: {direction}")
    return a_star, b_star