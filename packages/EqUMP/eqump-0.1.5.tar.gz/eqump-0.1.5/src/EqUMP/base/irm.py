import numpy as np
from typing import Union, Mapping, Optional, List, Dict

def irf(
    theta: Union[float, np.ndarray],
    params: Mapping[str, Union[float, np.ndarray]],
    model: str = "auto",
    D: float = 1.7,
) -> np.ndarray:
    r"""
    Computation probability of a response given the latent trait and item parameters via Item Response Function (IRF).

    Arguments
    ----------
    theta : float or np.ndarray
        Latent trait value(s).
    params : dict
        Item parameters.
        - "a": discrimination parameter (float, optional, default 1.0)
        - "b": 
            Dihotomous: difficulty parameter (float)
            Polytomous: step difficulties parameter (1D array of length m-1)
        - "c": pseudo-guessing parameter (float, optional, default 0.0)
    model : str
        {'1PL','2PL','3PL','GPC','auto'}, default 'auto'
        If 'auto', choose model by inspecting `params`.
        - 1PL: {'b'}
        - 2PL: {'a','b'} # b is scalar
        - 3PL: {'a','b','c'}
        - GPC: {'a', 'b'} # b is array
    D : float, default 1.7
        Scaling constant.
    
    Returns
    ---------
    Numpy array
    """
    if not isinstance(params, Mapping):
        raise TypeError("`params` must be a dict-like mapping.")
    if "b" not in params:
        raise KeyError("Missing required parameter 'b'.")
    
    # parameters
    theta = np.atleast_1d(np.asarray(theta, float))
    a = float(params.get("a", 1.0))
    c = float(params.get("c", 0.0))
    b_raw = np.asarray(params["b"], float)
    
    # item response model detection and validation
    if model == "auto":
        if b_raw.ndim == 1 and b_raw.size > 1:
            model = "GPC"
            if "c" in params:
                raise ValueError("Pseudo-guessing parameter 'c' is not allowed for GPCM.")
        else: 
            if "c" in params: model = "3PL"
            elif "a" in params: model = "2PL"
            else: model = "1PL"
    else: # model is specified
        if model == "GPC":
            if b_raw.ndim == 0 or b_raw.size <= 1:
                raise ValueError("GPCM requires `b` as a 1D array of step difficulties (length m-1).")
            if "c" in params:
                raise ValueError("Pseudo-guessing parameter 'c' is not allowed for GPCM.")
        elif model in {"1PL", "2PL", "3PL"}:
            if b_raw.size != 1:
                raise ValueError("Dichotomous model expects scalar `b`.")
        else:
            raise ValueError(f"Unknown model. Supported models: 1PL, 2PL, 3PL, GPC.")
    
    # computation probability
    if model in {"1PL", "2PL", "3PL"}:      
        b = float(b_raw)
        
        z = D * a * (theta - b)
        p = 1.0 / (1.0 + np.exp(-z))
        prob = c + (1.0 - c) * p
        
        return prob
    
    elif model == "GPC": # b should be 1D array of step difficulties (length m-1)
        b = np.atleast_1d(b_raw).ravel()  # (m-1, )
        # increments for categories k=1..m-1
        z = D * a * (theta[:, None] - b[None, :])      # (N, m-1)
        s = np.cumsum(z, axis=1)                       # (N, m-1)
        s = np.concatenate([np.zeros((theta.size, 1)), s], axis=1)  # prepend s_0 = 0 → (N, m)
        
        numerator = np.exp(s)
        denominator = numerator.sum(axis=1, keepdims=True)
       
        prob = numerator / denominator
        return prob if theta.size > 1 else prob[0]

# item1 = {"a": 1.2, "b": -0.5}
# item2 = {"a": 1.1, "b": [-0.74, 0.3, 0.91, 2.19]}

# print(irf(theta = 0, params=item1))
# print(irf(theta = -0.53, params = item2))

def trf(params_list: List[Dict[str, Union[float, List[float]]]], theta_range=np.arange(-6, 6+0.01, 0.01)):
    """Test response function.

    Parameters
    ----------
    params_list : List[Dict[str, Union[float, List[float]]]]
        List of item parameters.
    theta_range : np.ndarray, optional
        The range of theta values to evaluate. Default is -6 to 6 with a gap of 0.01.

    Returns
    -------
    np.ndarray
        Probability for each theta value. Shape (len(theta_range), len(params_list)).
    """
    n_items = len(params_list)
    n_theta = len(theta_range)
    probs = np.zeros((n_theta, n_items))

    for i, params in enumerate(params_list):
        probs[:, i] = irf(theta=theta_range, params=params)

    return probs
