# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union, Literal
import numpy as np
import pandas as pd

# from .irf import irf as _irf_single
from EqUMP.base.irf import irf as _irf_single


_SUPPORTED_PLOT_MODELS: Tuple[str, ...] = ("RASCH", "1PL", "2PL", "3PL", "GPCM")
_BLOCKED_PLOT_MODELS: Tuple[str, ...] = ("GRM", "GPCM2")


def _default_theta_grid() -> np.ndarray:
    # inclusive [-6, 6] with 0.05 step
    start, stop, step = -6.0, 6.0, 0.05
    # Ensure inclusion of stop within floating precision
    n = int(round((stop - start) / step)) + 1
    grid = start + step * np.arange(n)
    grid[-1] = stop
    return grid


def _is_dichotomous(model: str) -> bool:
    m = model.upper()
    return m in ("RASCH", "1PL", "2PL", "3PL")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure string columns "0","1",... and sort numerically
    cols = [str(c) for c in df.columns]
    # sort by integer value if possible
    try:
        order = np.argsort([int(c) for c in cols])
    except Exception:
        order = np.argsort(cols)
    df = df.copy()
    df.columns = cols
    df = df.iloc[:, order]
    return df


def _compute_curve(
    theta_grid: Sequence[float],
    params: Dict[str, Union[float, int, Sequence[float], np.ndarray]],
    model: str,
    D: float,
) -> pd.DataFrame:
    rows: List[pd.DataFrame] = []
    for th in theta_grid:
        out = _irf_single(theta=float(th), params=params, model=model, D=D)
        rows.append(out)
    df = pd.concat(rows, axis=0)
    df.index = np.asarray(theta_grid, dtype=float)
    df.index.name = "theta"
    df = _normalize_columns(df)
    return df


class IRFResult:
    """
    Container for IRF probabilities over a theta grid, with a plotting API.

    Attributes
    ----------
    df : pd.DataFrame
        Rows are theta values (index name: "theta").
        Columns are category strings: "0","1",... (dichotomous will have "0","1").
    model : str
        Model name (upper-cased).
    params : dict
        Item parameters used to compute IRF.
    D : float
        Scaling constant used.
    theta_grid : np.ndarray
        The theta grid used to compute the curve.

    Methods
    ----------
    plot(...)
        Plot IRF curves using matplotlib (lazy import).
    to_frame()
        Return the underlying DataFrame.
    summary()
        Text summary of the object.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        model: str,
        params: Dict[str, Union[float, int, Sequence[float], np.ndarray]],
        D: float,
        theta_grid: np.ndarray,
    ) -> None:
        self._df = _normalize_columns(df)
        self.model = model.upper()
        self.params = dict(params)
        self.D = float(D)
        self.theta_grid = np.asarray(theta_grid, dtype=float)

        # Basic numeric validation
        if not np.all(np.isfinite(self.theta_grid)):
            raise ValueError("theta_grid must contain only finite values.")
        if len(self.theta_grid) != len(self._df.index):
            raise ValueError("theta_grid length must match df row count.")

        # Ensure strictly ascending index
        if not np.all(np.diff(self.theta_grid) > 0) and len(self.theta_grid) > 1:
            # sort if provided out-of-order
            self._df = self._df.sort_index(axis=0)
            self.theta_grid = self._df.index.values

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def to_frame(self) -> pd.DataFrame:
        return self._df.copy()

    def summary(self) -> str:
        cats = list(self._df.columns)
        return (
            f"IRFResult(model={self.model}, D={self.D}, theta=[{self.theta_grid[0]},"
            f" {self.theta_grid[-1]}], n_theta={len(self.theta_grid)}, "
            f"categories={cats})"
        )

    def plot(
        self,
        ax=None,
        categories: Optional[Sequence[Union[int, str]]] = None,
        kind: Literal["line"] = "line",
        color=None,
        label: Optional[Union[str, Sequence[str]]] = None,
        show: bool = True,
        title: Optional[str] = None,
        legend: bool = True,
        grid: bool = True,
        xlim: Optional[Tuple[float, float]] = None,
        ylim: Optional[Tuple[float, float]] = (0.0, 1.0),
        linewidth: float = 2.0,
        linestyle: str = "-",
        alpha: float = 1.0,
        **mpl_kwargs,
    ):
        """
        Plot the IRF curves.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            If provided, draw on this axes. Otherwise, create a new figure/axes.
        categories : sequence of int or str, optional
            Which categories to plot. Defaults:
              - dichotomous: ["1"] (P(Y=1))
              - GPCM: all categories
        kind : "line"
            Currently only "line" is supported.
        color, label : optional
            Matplotlib color/label. For multi-line (GPCM), can be a sequence.
        show : bool
            If True and ax is None (we created the figure), call plt.show() at the end.
        title : str, optional
            Plot title. Defaults to "IRF - {model}".
        legend : bool
            Show legend if multiple lines or explicit label.
        grid : bool
            Show grid.
        xlim, ylim : tuple, optional
            Axis limits. Default ylim is (0,1).
        linewidth, linestyle, alpha : styling
            Matplotlib line style controls.
        **mpl_kwargs : dict
            Forwarded to matplotlib plot calls.

        Returns
        -------
        matplotlib.axes.Axes
        """
        model = self.model.upper()
        if model in _BLOCKED_PLOT_MODELS:
            raise NotImplementedError(f"Plotting for {model} is not implemented yet.")

        try:
            import matplotlib.pyplot as plt  # lazy import
        except Exception as e:
            raise RuntimeError("Matplotlib is required for plotting but is not available.") from e

        created_ax = False
        if ax is None:
            fig, ax = plt.subplots()
            created_ax = True

        df = self._df

        # Select categories
        if categories is None:
            if _is_dichotomous(model):
                selected_cols = ["1"] if "1" in df.columns else df.columns.tolist()
            else:
                # GPCM: all categories by default
                selected_cols = df.columns.tolist()
        else:
            selected_cols = []
            for c in categories:
                c_str = str(c)
                if c_str not in df.columns:
                    raise KeyError(f"Category {c!r} not found. Available: {list(df.columns)}")
                selected_cols.append(c_str)

        # Prepare labels and colors for possibly multiple lines
        if label is None:
            if _is_dichotomous(model):
                labels = ["P(Y=1)"] if selected_cols == ["1"] else [f"category {c}" for c in selected_cols]
            else:
                labels = [f"category {c}" for c in selected_cols]
        else:
            if isinstance(label, str):
                labels = [label] * len(selected_cols)
            else:
                labels = list(label)
                if len(labels) != len(selected_cols):
                    raise ValueError("Length of 'label' must match number of selected categories.")

        if color is None:
            colors = [None] * len(selected_cols)
        else:
            if isinstance(color, (str, tuple)):
                colors = [color] * len(selected_cols)
            else:
                colors = list(color)
                if len(colors) != len(selected_cols):
                    raise ValueError("Length of 'color' must match number of selected categories.")

        x = df.index.values
        # Plot each selected category
        for i, c in enumerate(selected_cols):
            y = df[c].values
            # Avoid plotting numerical noise outside [0,1] while not mutating stored data
            y_plot = np.clip(y, 0.0, 1.0)
            ax.plot(
                x,
                y_plot,
                label=labels[i],
                color=colors[i],
                linewidth=linewidth,
                linestyle=linestyle,
                alpha=alpha,
                **mpl_kwargs,
            )

        # Styling
        ax.set_xlabel("Theta")
        ax.set_ylabel("Probability")
        if title is None:
            title = f"IRF - {model}"
        ax.set_title(title)
        if grid:
            ax.grid(True, linestyle="--", alpha=0.4)
        if xlim is not None:
            ax.set_xlim(*xlim)
        if ylim is not None:
            ax.set_ylim(*ylim)

        # Legend conditions
        if legend and (len(selected_cols) > 1 or (labels and labels[0] is not None)):
            ax.legend()

        if created_ax and show:
            plt.show()

        return ax


def make_irf_object(
    theta_grid: Optional[Sequence[float]] = None,
    params: Optional[Dict[str, Union[float, int, Sequence[float], np.ndarray]]] = None,
    model: Optional[str] = None,
    D: float = 1.702,
) -> IRFResult:
    """
    Compute IRF over a theta grid and return an IRFResult object for plotting and inspection.

    Parameters
    ----------
    theta_grid : sequence of float, optional
        The theta values to evaluate. Defaults to np.arange(-6, 6 + 1e-12, 0.05).
    params : dict
        Item parameters accepted by base.irf.irf().
    model : str
        One of {"Rasch", "1PL", "2PL", "3PL", "GPCM", "GRM", "GPCM2"}.
    D : float
        Scaling constant (default: 1.702).

    Returns
    ----------
    IRFResult
        Object holding the computed probabilities and metadata.

    Notes
    ----------
    - Plotting support is currently enabled for: Rasch, 1PL, 2PL, 3PL, GPCM.
    - Plotting is intentionally disabled for GRM and GPCM2 (NotImplementedError).
    """
    if params is None or model is None:
        raise ValueError("Both 'params' and 'model' must be provided.")
    model_up = model.upper()

    if theta_grid is None:
        theta_grid = _default_theta_grid()

    theta_arr = np.asarray(theta_grid, dtype=float)
    if theta_arr.ndim != 1 or len(theta_arr) == 0:
        raise ValueError("'theta_grid' must be a non-empty 1D sequence of floats.")
    if not np.all(np.isfinite(theta_arr)):
        raise ValueError("'theta_grid' must contain only finite numbers.")

    df = _compute_curve(theta_arr, params=params, model=model_up, D=float(D))
    return IRFResult(df=df, model=model_up, params=params, D=float(D), theta_grid=theta_arr)

if __name__ == "__main__":
    obj = make_irf_object(params={"a": 1.2, "b": 0.0}, model="2PL", D=1.702)
    obj.plot()

    # obj = make_irf_object(params={"a": 1.0, "b": [-1.0, 0.5, 1.2]}, model="GPCM", D=1.702)
    # obj.plot()