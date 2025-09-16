#!/usr/bin/env python3
"""
Additional Correlation Matrix integration examples.

Generates images referenced in docs/correlation_matrix.md Integration section:
- correlation_integration_corr.png
- correlation_integration_boxplot.png
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

    # Correlation matrix integration image
    fig_corr, axes_corr = ggpubpy.plot_correlation_matrix(
        iris,
        title="Variable Relationships",
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "correlation_integration_corr.png"), dpi=300, bbox_inches="tight")
    plt.close(fig_corr)

    # Boxplot integration image
    fig_box, ax_box = ggpubpy.plot_boxplot(
        iris,
        x="species",
        y="sepal_length",
        x_label="Species",
        y_label="Sepal Length (cm)",
        title="Integration: Boxplot (Iris)",
        parametric=False,
        alpha=0.6,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "correlation_integration_boxplot.png"), dpi=300, bbox_inches="tight")
    plt.close(fig_box)


if __name__ == "__main__":
    main()
