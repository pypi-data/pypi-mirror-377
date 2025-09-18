import numpy as np
from typing import Tuple
from scipy.stats import norm
from EqUMP.linking.helper import transform_item_params
from EqUMP.base import irf
from scipy.optimize import minimize

def haebara_loss(
    params: Tuple[float, float],
    a_base: np.ndarray,
    b_base: np.ndarray,
    a_new: np.ndarray,
    b_new: np.ndarray,
    theta: np.ndarray = norm.ppf(np.linspace(0.001, 0.999, 81))
) -> float:
    A, B = params
    weights = norm.pdf(theta)[:, None]

    # old → new scale
    a_old_star, b_old_star = transform_item_params(a_base, b_base, A, B, direction='to_new')
    P_new = irf(theta[:, None], {"a": a_new, "b": b_new})
    P_old_star = irf(theta[:, None], {"a": a_old_star, "b": b_old_star})
    loss_1 = np.sum(weights * (P_new - P_old_star) ** 2)

    # new → old scale
    a_new_star, b_new_star = transform_item_params(a_new, b_new, A, B, direction='to_old')
    P_old = irf(theta[:, None], {"a": a_base, "b": b_base})
    P_new_star = irf(theta[:, None], {"a": a_new_star, "b": b_new_star})
    loss_2 = np.sum(weights * (P_old - P_new_star) ** 2)

    return (loss_1 + loss_2) / np.sum(weights)

def haebara_scale_linking(
    a_base: np.ndarray,
    b_base: np.ndarray,
    a_new: np.ndarray,
    b_new: np.ndarray,
    init_params: Tuple[float, float] = (1.0, 0.0),
    theta: np.ndarray = norm.ppf(np.linspace(0.001, 0.999, 81))
) -> Tuple[float, float]:
    """Haebara(1980) scale linking method

    Parameters
    ----------
    a_base : np.ndarray
        item discrimination parameters in base scale
    b_base : np.ndarray
        item difficulty parameters in base scale
    a_new : np.ndarray
        item discrimination parameters in new scale
    b_new : np.ndarray
        item difficulty parameters in new scale
    init_params : Tuple[float, float], optional
        initial parameters (A, B), by default (1.0, 0.0)
    theta : np.ndarray, optional
        theta values, by default norm.ppf(np.linspace(0.001, 0.999, 81))

    Returns
    -------
    Tuple[float, float]
        (A, B)
    """    
    result_haebara = minimize(haebara_loss, init_params, args=(a_base, b_base, a_new, b_new, theta))
    return result_haebara.x

