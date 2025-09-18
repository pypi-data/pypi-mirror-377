from typing import Dict, Union, Literal, Mapping, overload
import numpy as np
import pandas as pd
from scipy.special import expit


@overload
def irf(
    theta: float,
    params: Dict[str, float],
    model: Literal["Rasch", "1PL", "2PL", "3PL"],
    D: float = 1.702,
) -> pd.DataFrame: ...
@overload
def irf(
    theta: float,
    params: Dict[str, Union[list, np.ndarray]],
    model: Literal["GRM","GPCM", "GPCM2"],
    D: float = 1.702,
) -> pd.DataFrame: ...

def irf(
    theta: float,
    params: Union[Dict[str, float], Dict[str, Union[list, np.ndarray]]],
    model: Literal["Rasch", "1PL", "2PL", "3PL", "GRM", "GPCM", "GPCM2"],
    D: float = 1.702,  # scaling constant
) -> pd.DataFrame:
    """
    Compute the Probability of correct response by Item Response Function (IRF) for various IRT models.

    Parameters
    ----------
    theta : float
        Latent trait value.
    params : dict
        Item parameters. Required keys depend on the model:
            - Rasch: {"b": float}
            - 1PL: {"a": float, "b": float}
            - 2PL: {"a": float, "b": float}
            - 3PL: {"a": float, "b": float, "c": float}
            - GRM: {"a": float, "b": list[float] or np.ndarray}
            - GPCM: {"a": float, "b": list[float] or np.ndarray}
    model : str
        IRT model name. One of {"Rasch", "1PL", "2PL", "3PL", "GRM", "GPCM", "GPCM2"}.
    D : float, optional
        Scaling constant (default: 1.702).

    Returns
    -------
    pd.DataFrame
        IRF probabilities. Rows: theta values; Columns: item categories.

    Examples
    --------
    >>> irf(theta=0.0, params={"b": 0.0}, model="Rasch")
    >>> irf(theta=0.5, params={"a": 1.5, "b": 0.2}, model="1PL")
    >>> irf(theta=-0.3, params={"a": 1.2, "b": 0.5}, model="2PL")
    >>> irf(theta=0.1, params={"a": 1.0, "b": 0.3, "c": 0.2}, model="3PL")
    >>> irf(theta=0.0, params={"a": 1.1, "b": [-0.74, 0.3, 0.91]}, model="GPCM")
    """
    _typecheck_irf(theta, params, model)
    model = model.upper()
    params = {k.lower(): v for k, v in params.items()}
    model_map = {
        "RASCH": irf_rasch,
        "1PL": irf_1pl,
        "2PL": irf_2pl,
        "3PL": irf_3pl,
        "GRM": irf_grm,
        "GPCM": irf_GPCM,
        "GPCM2": irf_GPCM2,
    }
    return model_map[model](theta, params, D)

def _typecheck_irf(theta, params, model):
    # theta check
    if not isinstance(theta, (float, int)):
        raise TypeError(f"`theta` must be a float. But got {type(theta)}")

    # params & theta check
    if not isinstance(params, (dict, Mapping)):
        raise TypeError(
            f"params must be a dict or dict-like mapping. But got {type(params)}"
        )
    if not all(isinstance(key, str) for key in params.keys()):
        raise TypeError("All keys in `params(dictionary, Mapping)` must be strings.")
    
    # model check
    models = ["RASCH", "1PL", "2PL", "3PL", "GPCM", "GPCM2", "GRM"]
    if model.upper() not in models: 
        raise KeyError(
            f"`model` must be one of {models}, but got '{model}'. "
        )
    
    # model specific check
    model_map = {
        "RASCH": _typecheck_rasch,
        "1PL": _typecheck_1pl,
        "2PL": _typecheck_2pl,
        "3PL": _typecheck_3pl,
        "GRM": _typecheck_grm,
        "GPCM": _typecheck_GPCM,
        "GPCM2": _typecheck_GPCM,
    }
    model_map[model.upper()](params)

    return None

def irf_rasch(theta: float, params: Dict[str, float], D: float) -> pd.DataFrame:

    # parameters
    theta = float(theta)
    a = 1.0
    b = float(params["b"])

    # compute probability
    z = D * a * (theta - b)
    prob = 1 / (1.0 + np.exp(-z))

    # output
    output = pd.DataFrame(
        np.column_stack([1 - prob, prob]), index=[theta], columns=["0", "1"]
    )
    return output

def _typecheck_rasch(params) -> None:
    if "b" not in params or len(params) != 1:
        raise KeyError(
            f"Rasch model requires only 'b' parameter. But got {list(params.keys())}"
        )
    if not all(isinstance(val, (float, int)) for val in params.values()):
        typedict = {val: type(val) for val in params.values()}
        raise TypeError(
            f"Rasch model parameters must be float or int. But got {typedict}"
        )
    return None

def irf_1pl(theta: float, params: Dict[str, float], D: float) -> pd.DataFrame:

    ## parameters
    theta = float(theta)
    a = float(params["a"])
    b = float(params["b"])

    # compute probability
    z = D * a * (theta - b)
    prob = 1 / (1.0 + np.exp(-z))

    # output
    output = pd.DataFrame(
        np.column_stack([1 - prob, prob]), index=[theta], columns=["0", "1"]
    )

    return output

def _typecheck_1pl(params) -> None:
    if "a" not in params or "b" not in params or len(params) != 2:
        raise KeyError(
            f"1PL model requires 'a' and 'b' parameters. But got {list(params.keys())}"
        )
    if not all(isinstance(val, (float, int)) for val in params.values()):
        typedict = {val: type(val) for val in params.values()}
        raise TypeError(
            f"1PL model parameters must be float or int. But got {typedict}"
        )
    return None

def irf_2pl(theta: float, params: Dict[str, float], D: float) -> pd.DataFrame:

    ## parameters
    theta = float(theta)
    a = float(params["a"])
    b = float(params["b"])

    # compute probability
    z = D * a * (theta - b)
    prob = 1 / (1.0 + np.exp(-z))

    # output
    output = pd.DataFrame(
        np.column_stack([1 - prob, prob]), index=[theta], columns=["0", "1"]
    )

    return output

def _typecheck_2pl(params) -> None:
    if "a" not in params or "b" not in params or len(params) != 2:
        raise KeyError(
            f"2PL model requires 'a' and 'b' parameters. But got {list(params.keys())}"
        )
    if not all(isinstance(val, (float, int)) for val in params.values()):
        typedict = {val: type(val) for val in params.values()}
        raise TypeError(
            f"2PL model parameters must be float or int. But got {typedict}"
        )
    return None

def irf_3pl(theta: float, params: Dict[str, float], D: float) -> pd.DataFrame:

    ## parameters
    theta = float(theta)
    a = float(params.get("a", 1.0))
    b = float(params["b"])
    c = float(params.get("c", 0.0))

    # compute probability
    z = D * a * (theta - b)
    prob = c + (1.0 - c) * expit(z)

    # output
    output = pd.DataFrame(
        np.column_stack([1 - prob, prob]), index=[theta], columns=["0", "1"]
    )
    return output

def _typecheck_3pl(params) -> None:
    if (
        "a" not in params
        or "b" not in params
        or "c" not in params
        or len(params) != 3
    ):
        raise KeyError(
            f"3PL model requires 'a', 'b', and 'c' parameters. But got {list(params.keys())}"
        )
    if not all(isinstance(val, (float, int)) for val in params.values()):
        typedict = {val: type(val) for val in params.values()}
        raise TypeError(
            f"3PL model parameters must be float or int. But got {typedict}"
        )
    return None

def irf_grm(
    theta: float, 
    params: Dict[str, Union[float, np.ndarray]], 
    D: float
) -> pd.DataFrame:
    
    # Parameters
    theta = float(theta)
    a = float(params["a"])
    b = np.asarray(params["b"], dtype=float) #thresholds

    # Compute probability
    z = D * a * (theta - b)
    prob = 1 / (1.0 + np.exp(-z))
    raise NotImplementedError("GRM model is not implemented yet.")
    cumulative_prob = np.concatenate(([1.0], prob, [0.0]))
    categorical_prob = cumulative_prob[:-1] - cumulative_prob[1:]

    # Output
    total_categories = len(b) + 1
    output = pd.DataFrame(
        categorical_prob.reshape(1, total_categories),
        index=[theta],
        columns=[str(k) for k in range(total_categories)]
    )
    return output

def _typecheck_grm(params) -> None:
    if "a" not in params or "b" not in params or len(params) != 2:
        raise KeyError(
            f"Graded Response Model requires 'a' and 'b' parameters. But got {list(params.keys())}"
        )
    if not isinstance(params["a"], (float, int)):
        raise TypeError(
            f"Graded Response Model parameter 'a' must be float or int. But got {type(params['a'])}"
        )
    if not isinstance(params["b"], (list, np.ndarray)):
        raise TypeError(
            f"Graded Response Model parameter 'b' must be list or np.ndarray. But got {type(params['b'])}"
        )
    return None

def irf_GPCM(
    theta: float, params: Dict[str, Union[np.ndarray]], D: float
) -> pd.DataFrame:
    """
    _summary_

    References
    ----------
    Muraki, E. (1992), A GENERALIZED PARTIAL CREDIT MODEL: APPLICATION OF AN EM ALGORITHM. ETS Research Report Series, 1992: i-30. https://doi.org/10.1002/j.2333-8504.1992.tb01436.x
    """

    ## parameters
    theta = float(theta)
    a = float(params.get("a", 1.0))
    b = np.asarray(params["b"], dtype=float) #step param

    # compute probability
    b_full = np.concatenate(([0.0], b))
    z = np.cumsum(D * a * (theta - b_full))
    numerator = np.exp(z)
    denominator = np.sum(numerator)
    prob = numerator / denominator

    m = len(b_full)
    output = pd.DataFrame(
        prob.reshape(1, m), index=[theta], columns=[str(k) for k in range(m)]
    )
    return output

def irf_GPCM2(
    theta: float, params: Dict[str, Union[np.ndarray]], D: float
) -> pd.DataFrame:

    raise NotImplementedError("GPCM2 model is not implemented yet.")

    return output

def _typecheck_GPCM(params) -> None:
    if "a" not in params or "b" not in params or len(params) != 2:
        raise KeyError(
            f"Generalized Partial Credit Model requires 'a' and 'b' parameters. But got {list(params.keys())}"
        )
    if not isinstance(params["a"], (float, int)):
        raise TypeError(
            f"Generalized Partial Credit Model parameter 'a' must be float or int. But got {type(params['a'])}"
        )
    if not isinstance(params["b"], (list, np.ndarray)):
        raise TypeError(
            f"Generalized Partial Credit Model parameter 'b' must be list or np.ndarray. But got {type(params['b'])}"
        )

    return None
