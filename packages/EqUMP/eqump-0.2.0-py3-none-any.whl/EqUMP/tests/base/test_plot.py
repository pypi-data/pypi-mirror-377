import os
import numpy as np
import pandas as pd

# Use headless backend for matplotlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pytest

from EqUMP.base.plot import make_irf_object, IRFResult


def test_make_irf_object_default_grid_2pl():
    obj = make_irf_object(params={"a": 1.2, "b": 0.0}, model="2PL", D=1.702)
    assert isinstance(obj, IRFResult)
    tg = obj.theta_grid
    assert tg[0] == -6.0
    assert tg[-1] == 6.0
    # step ~ 0.05
    diffs = np.diff(tg)
    assert np.allclose(diffs, 0.05, atol=1e-12)


def test_plot_dichotomous_defaults_is_PY1_label():
    obj = make_irf_object(params={"a": 1.3, "b": -0.2, "c": 0.2}, model="3PL", D=1.702)
    fig, ax = plt.subplots()
    out_ax = obj.plot(ax=ax, show=False)  # default should plot only P(Y=1)
    assert out_ax is ax
    # One line only and label is "P(Y=1)"
    assert len(ax.lines) == 1
    line = ax.lines[0]
    assert line.get_label() == "P(Y=1)"
    # Y values in [0,1]
    y = line.get_ydata()
    assert np.all((y >= 0.0) & (y <= 1.0))


def test_plot_gpcm_all_categories_and_sum_to_one():
    # GPCM with 4 categories (len(b)=3 => m=4)
    params = {"a": 1.0, "b": [-1.0, 0.5, 1.2]}
    obj = make_irf_object(params=params, model="GPCM", D=1.702)
    df = obj.df
    # Expect 4 columns named "0","1","2","3"
    assert list(df.columns) == ["0", "1", "2", "3"]

    # Probabilities across categories should sum to ~1 row-wise
    row_sums = df.sum(axis=1).values
    assert np.allclose(row_sums, 1.0, atol=1e-8)

    # Plot should create one line per category with labels "category K"
    fig, ax = plt.subplots()
    out_ax = obj.plot(ax=ax, show=False)
    assert out_ax is ax
    assert len(ax.lines) == 4
    labels = [ln.get_label() for ln in ax.lines]
    assert labels == ["category 0", "category 1", "category 2", "category 3"]


def test_blocked_models_grm_and_gpcm2_raise():
    # GRM currently not implemented at the IRF level; expect NotImplementedError during object creation
    with pytest.raises(NotImplementedError):
        make_irf_object(params={"a": 1.0, "b": [-1.0, 0.0, 1.0]}, model="GRM", D=1.702)

    # GPCM2 also not implemented
    with pytest.raises(NotImplementedError):
        make_irf_object(params={"a": 1.0, "b": [-1.0, 0.5, 1.2]}, model="GPCM2", D=1.702)


def test_axes_handling_and_styling():
    obj = make_irf_object(params={"a": 1.1, "b": 0.3}, model="2PL", D=1.702)
    fig, ax = plt.subplots()
    xlim = (-5, 5)
    ylim = (0.0, 1.0)
    title = "Custom Title"
    out_ax = obj.plot(
        ax=ax,
        show=False,
        title=title,
        xlim=xlim,
        ylim=ylim,
        legend=True,
        color="C1",
        linewidth=1.5,
        linestyle="--",
        alpha=0.8,
    )
    assert out_ax is ax
    # Limits and title applied
    assert tuple(map(float, ax.get_xlim())) == xlim
    assert tuple(map(float, ax.get_ylim())) == ylim
    assert ax.get_title() == title
    # A single line exists
    assert len(ax.lines) == 1
    # If legend was requested, a legend may or may not be auto-added for one line
    # Ensure no error: acceptable either way
    _ = ax.get_legend()  # no assertion, just ensure no exceptions
