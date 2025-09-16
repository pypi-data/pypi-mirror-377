#!/usr/bin/env python3
"""
Shift plot examples for ggpubpy using the Iris dataset.

Generates the images referenced in docs/shiftplot.md:
- shift_plot_example_basic.png
- shift_plot_example.png
- shift_plot_with_diff_example.png
"""

import os
import sys

import matplotlib.pyplot as plt

# Add the parent directory to sys.path to import ggpubpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ggpubpy
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    iris = ggpubpy.datasets.load_iris()
    iris_2groups = iris[iris["species"].isin(["setosa", "versicolor"])]

    # Basic (no connectors, no bottom subplot)
    print("Generating shift_plot_example_basic.png ...")
    x = iris_2groups[iris_2groups["species"] == "setosa"]["sepal_length"].values
    y = iris_2groups[iris_2groups["species"] == "versicolor"]["sepal_length"].values
    fig = ggpubpy.plot_shift(x, y)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "shift_plot_example_basic.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Main only with quantile connectors
    print("Generating shift_plot_example.png ...")
    fig = ggpubpy.plot_shift(
        x,
        y,
        paired=False,
        n_boot=1000,
        percentiles=[10, 50, 90],
        confidence=0.95,
        violin=True,
        show_quantiles=True,
        show_quantile_diff=False,
        x_label="Setosa",
        y_label="Versicolor",
        title="Iris: Setosa vs Versicolor Shift Plot",
        subtitle="Main plot with quantile connectors",
        color="#27AE60",
        line_color="#2C3E50",
        alpha=0.8,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "shift_plot_example.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # With quantile differences subplot
    print("Generating shift_plot_with_diff_example.png ...")
    fig = ggpubpy.plot_shift(
        x,
        y,
        paired=False,
        n_boot=1000,
        percentiles=[10, 50, 90],
        confidence=0.95,
        violin=True,
        show_quantiles=True,
        show_quantile_diff=True,
        x_label="Setosa",
        y_label="Versicolor",
        title="Iris: Setosa vs Versicolor Shift Plot",
        subtitle="With quantile differences subplot",
        color="#27AE60",
        line_color="#2C3E50",
        alpha=0.8,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "shift_plot_with_diff_example.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("Done generating shift plot examples.")


if __name__ == "__main__":
    main()
