import numpy as np

def mean_difference(b_ref: np.ndarray, b_tar: np.ndarray):
    """

    Notes
    -----
    - This method commonly refered as "mean/mean" but SH, Kim(2022) claims to call this as "mean difference"
    
    See Also
    -----
    Loyd & Hoover (1980)
    """
    A = 1.0
    B = np.mean(b_ref) - A * np.mean(b_tar)
    return A, B
