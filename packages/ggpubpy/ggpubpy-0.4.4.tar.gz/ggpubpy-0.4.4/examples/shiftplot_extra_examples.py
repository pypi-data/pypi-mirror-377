#!/usr/bin/env python3
"""
Additional Shift Plot examples for integration and advanced usage.

Generates images referenced in docs/shiftplot.md:
- shift_plot_integration_shift.png
- shift_plot_integration_boxplot.png
- shift_plot_advanced_wilcoxon.png
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add the parent directory to sys.path to import ggpubpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ggpubpy
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def integration_examples() -> None:
    """Generate integration examples: shift + boxplot using Iris dataset."""
    iris = ggpubpy.datasets.load_iris()
    x = iris[iris["species"] == "setosa"]["sepal_length"].values
    y = iris[iris["species"] == "versicolor"]["sepal_length"].values

    # Shift plot (Iris)
    fig_shift = ggpubpy.plot_shift(
        x,
        y,
        x_label="Setosa",
        y_label="Versicolor",
        title="Integration: Shift Plot (Iris)",
        alpha=0.8,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "shift_plot_integration_shift.png"), dpi=300, bbox_inches="tight")
    plt.close(fig_shift)

    # Box plot (Iris) for comparison
    df = pd.DataFrame(
        {"Group": ["Setosa"] * len(x) + ["Versicolor"] * len(y), "Value": np.concatenate([x, y])}
    )
    fig_box, ax_box = ggpubpy.plot_boxplot(
        df,
        x="Group",
        y="Value",
        x_label="Species",
        y_label="Sepal Length (cm)",
        title="Integration: Boxplot (Iris)",
        parametric=False,
        alpha=0.6,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "shift_plot_integration_boxplot.png"), dpi=300, bbox_inches="tight")
    plt.close(fig_box)


def advanced_example() -> None:
    """Generate advanced example: custom statistical annotation (Wilcoxon)."""
    np.random.seed(42)
    n = 30
    before = np.random.normal(10, 2, n)
    after = before + np.random.normal(1, 1.5, n)

    fig = ggpubpy.plot_shift(
        before,
        after,
        x_label="Before",
        y_label="After",
        title="Advanced: Shift with custom stat",
        subtitle="Wilcoxon signed-rank",
        alpha=0.7,
    )

    # Add custom Wilcoxon test annotation
    from scipy import stats

    ax = fig.axes[0]
    wilcoxon_stat, wilcoxon_p = stats.wilcoxon(before, after)
    ax.text(
        0.02,
        0.98,
        f"Wilcoxon signed-rank test:\np = {wilcoxon_p:.3f}",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7),
    )

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "shift_plot_advanced_wilcoxon.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    integration_examples()
    advanced_example()


if __name__ == "__main__":
    main()
