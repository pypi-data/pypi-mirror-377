from typing import Dict, Hashable, Union, List, Literal, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.optimize import root_scalar
from EqUMP.base import create_prob_df, trf
from ...linking/helper import transform_item_params

def tse_bound(
    params: Dict[Hashable, Dict[str, Union[float, np.ndarray]]],
) -> Tuple[float, float]:
    lower = sum(float(v["c"]) for v in params.values() if "c" in v)
    upper = sum(np.atleast_1d(v["b"]).size for v in params.values())
    
    output = lower, upper
    return output

def tse_loss(
    ts: float,
    params: Dict[Hashable, Dict[str, Union[float, np.ndarray]]],
    model: Dict[Hashable, Literal["1PL", "2PL", "3PL", "GPCM"]],
    theta: float = 0.0,
    D: float = 1.702
) -> float: 
    keys = list(params.keys())
    params = [params[k] for k in keys]
    model = [model[k] for k in keys]
    df = create_prob_df(theta=theta, items=params, model=model, D=D)
    T = float(trf(df))
    
    loss = ts - T
    return loss

def tse(
    ts: float,
    params_new: Dict[Hashable, Dict[str, Union[float, np.ndarray]]],
    params_old: Dict[Hashable, Dict[str, Union[float, np.ndarray]]],
    common_new: List[Hashable],
    common_old: List[Hashable],
    model_new: Dict[Hashable, Literal["1PL", "2PL", "3PL", "GPCM"]],
    model_old: Dict[Hashable, Literal["1PL", "2PL", "3PL", "GPCM"]],
    theta: float = 0.0,
    D: float = 1.702, 
    anchor: Literal["internal", "external"] = "internal"
) -> Tuple[float, float]:
    """
    Performs true score equating of the new test form to the old test form under a common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design. 
    Calculate the latent trait level and the true score on the old test form that corresponds to a given score on the new form, using the linking results.
    """
    
    if anchor == "external":
        params_new = {k: v for k, v in params_new.items() if k not in common_new}
        params_old = {k: v for k, v in params_old.items() if k not in common_old}
        model_new = {k: v for k, v in model_new.items()  if k not in common_new}
        model_old = {k: v for k, v in model_old.items()  if k not in common_old}

    def obj(v: float) -> float:
        return tse_loss(
            ts=ts,
            theta=v,
            params=params_new,
            model=model_new,
            D=D
        )
    
    res = root_scalar(obj, bracket=[-10.0, 10.0], method='brentq', xtol=1e-7)
    theta_updated = float(res.root)
    
    df_old = create_prob_df(
        theta=theta_updated,
        items=params_old,
        model=model_old,
        D=D
        )
    T_old = float(trf(df_old))
    
    output = theta_updated, T_old
    return output
    
    
