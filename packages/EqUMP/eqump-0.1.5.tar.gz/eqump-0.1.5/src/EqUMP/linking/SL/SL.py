from typing import Tuple
import numpy as np
from scipy.stats import norm
from EqUMP.linking.helper import transform_item_params
from EqUMP.base.irm import trf, irf
from scipy.optimize import minimize
from EqUMP.base.estimation import mmle_em

def _create_params_list(a_params: np.ndarray, b_params: np.ndarray):
    """Convert a and b parameter arrays to list of parameter dictionaries."""
    return [{'a': a, 'b': b, 'model': '2PL'} for a, b in zip(a_params, b_params)]

def _trf_with_d1(params_list, theta_range):
    """Test response function with D=1 to match R implementation."""
    n_items = len(params_list)
    n_theta = len(theta_range)
    probs = np.zeros((n_theta, n_items))

    for i, params in enumerate(params_list):
        probs[:, i] = irf(theta=theta_range, params=params, D=1.0)

    return probs

def stocking_lord_scale_linking(
    a_base: np.ndarray,
    b_base: np.ndarray,
    a_new: np.ndarray,
    b_new: np.ndarray,
    init_params: Tuple[float, float] = (1.0, 0.0),
    theta: np.ndarray = norm.ppf(np.linspace(0.001, 0.999, 81))
) -> Tuple[float, float]:
    """Stocking-Lord(1983) scale linking method

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
    def loss_function(params):
        A, B = params
        weights = norm.pdf(theta)

        # old → new scale
        a_old_star, b_old_star = transform_item_params(a_base, b_base, A, B, direction='to_new')
        trf_new = np.sum(_trf_with_d1(_create_params_list(a_new, b_new), theta), axis=1)
        trf_old_star = np.sum(_trf_with_d1(_create_params_list(a_old_star, b_old_star), theta), axis=1)
        loss_1 = np.sum(weights * (trf_new - trf_old_star) ** 2)

        # new → old scale
        a_new_star, b_new_star = transform_item_params(a_new, b_new, A, B, direction='to_old')
        trf_old = np.sum(_trf_with_d1(_create_params_list(a_base, b_base), theta), axis=1)
        trf_new_star = np.sum(_trf_with_d1(_create_params_list(a_new_star, b_new_star), theta), axis=1)
        loss_2 = np.sum(weights * (trf_old - trf_new_star) ** 2)

        return (loss_1 + loss_2) / np.sum(weights)
    result_sl = minimize(loss_function, init_params)
    return result_sl.x

def stocking_lord_scale_linking_based_on_response(
    responses_base: np.ndarray,
    responses_new: np.ndarray,
    a_base: np.ndarray,
    b_base: np.ndarray,
    a_new: np.ndarray,
    b_new: np.ndarray,
    init_params: Tuple[float, float] = (1.0, 0.0)
) -> Tuple[float, float]:
    """Stocking-Lord scale linking based on response data
    
    Parameters
    ----------
    responses_base : np.ndarray
        response data for base scale items
    responses_new : np.ndarray
        response data for new scale items
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
        
    Returns
    -------
    Tuple[float, float]
        (A, B)
    """
    
    # Estimate theta nodes and weights from response data
    result_base = mmle_em(responses_base, a_base, b_base)
    result_new = mmle_em(responses_new, a_new, b_new)
    
    theta_base, weights_base = result_base.theta_nodes, result_base.weights
    theta_new, weights_new = result_new.theta_nodes, result_new.weights
    
    # Combine theta nodes and weights
    theta_combined = np.concatenate([theta_base, theta_new])
    weights_combined = np.concatenate([weights_base, weights_new])
    
    def loss_function(params):
        A, B = params
        
        # old → new scale
        a_old_star, b_old_star = transform_item_params(a_base, b_base, A, B, direction='to_new')
        trf_new = np.sum(_trf_with_d1(_create_params_list(a_new, b_new), theta_combined), axis=1)
        trf_old_star = np.sum(_trf_with_d1(_create_params_list(a_old_star, b_old_star), theta_combined), axis=1)
        loss_1 = np.sum(weights_combined * (trf_new - trf_old_star) ** 2)
        
        # new → old scale
        a_new_star, b_new_star = transform_item_params(a_new, b_new, A, B, direction='to_old')
        trf_old = np.sum(_trf_with_d1(_create_params_list(a_base, b_base), theta_combined), axis=1)
        trf_new_star = np.sum(_trf_with_d1(_create_params_list(a_new_star, b_new_star), theta_combined), axis=1)
        loss_2 = np.sum(weights_combined * (trf_old - trf_new_star) ** 2)
        
        return (loss_1 + loss_2) / np.sum(weights_combined)
    
    result_sl = minimize(loss_function, init_params)
    return result_sl.x
