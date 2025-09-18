import numpy as np
from typing import Hashable, Dict, Union, Literal, Tuple

def transform_item_params(
    params: Dict[Hashable, Dict[str, Union[float, np.ndarray]]],
    A: float = 1.0,
    B: float = 0.0,
    direction: Literal["to_old", "to_new"] = "to_old",
) -> Dict[Hashable, Dict[str, Union[float, np.ndarray]]]:
    """
    Transform the IRT scale according to the linking coefficient A, B.

    Parameters
    ----------
    params : Dict
        Item parameters for the new/old test form.
        - "a": discrimination parameter
        - "b":
            Dichotomous: difficulty parameter
            Polytomous: step difficulties parameter
        - "c": pseudo-guessing parameter
    A/B: float
        Linking coefficients.
    direction: {"to_old", "to_new"}, optional
        to_old: transform item parameters of the new test form to the old test form
        to_new: transform item parameters of the old test form to the new test form

    Returns
    -------
    Dict[item_id -> {'a': float, 'b': float|np.ndarray, 'c': float}]
    """

    output: Dict[Hashable, Dict[str, Union[float, np.ndarray]]] = {}

    if direction == "to_old":
        for key, par in params.items():
            a = float(par["a"])
            b = np.asarray(par["b"], dtype=float)

            a_t = a / A
            b_t = A * b + B
            b_t = float(b_t) if b_t.shape == () else b_t

            item = {"a": a_t, "b": b_t}
            if "c" in par:
                item["c"] = float(par["c"])

            output[key] = item

    elif direction == "to_new":
        for key, par in params.items():
            a = float(par["a"])
            b = np.asarray(par["b"], dtype=float)

            a_t = A * a
            b_t = (b - B) / A
            b_t = float(b_t) if b_t.shape == () else b_t

            item = {"a": a_t, "b": b_t}
            if "c" in par:
                item["c"] = float(par["c"])

            output[key] = item
    return output

def adjust_item_input(
    item_infos: Dict[Hashable, Dict[str, Union[float, np.ndarray]]]
) -> Tuple[Dict[Hashable, Literal["1PL", "2PL", "3PL", "GPCM"]], Dict[Hashable, Dict[str, Union[float, np.ndarray]]]]:
    """
    Adjust item information input into params and models

    Notes
    -----
    - (25.09.15) This function is a band-aid for terrible Item Response Function
    """    
    model = dict()
    params = dict()
    
    for key, info in item_infos.items():
        model[key] = info["model"]
        
        # redisudal key except model goes into params
        params[key] = {k: v for k, v in info.items() if k != "model"}
    
    return model, params
    
class SLResult:
    def plot(self):
        """plot linking result, 
        - transformed anchor items ICC,
        - transformed TCC
        """
        pass

    def summary(self):
        """_summary_
        """        
        pass