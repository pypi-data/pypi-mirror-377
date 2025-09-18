import numpy as np

def mean_sigma(b_ref: np.ndarray, b_tar: np.ndarray):
    """
    
    See Also
    -----
    Marco (1977)
    """
    A = np.std(b_ref, ddof=1) / np.std(b_tar, ddof=1)
    B = np.mean(b_ref) - A * np.mean(b_tar)
    return A, B
