#!/usr/bin/env python3
"""
Additional Violin Plot integration examples.

Generates images referenced in docs/violinplot.md Integration section:
- violin_integration_violin.png
- violin_integration_boxplot.png
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

    # Violin integration image
    fig_vio, ax_vio = ggpubpy.plot_violin(
        iris,
        x="species",
        y="sepal_length",
        x_label="Species",
        y_label="Sepal Length (cm)",
        title="Integration: Violin (Iris)",
        parametric=False,
        alpha=0.6,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "violin_integration_violin.png"), dpi=300, bbox_inches="tight")
    plt.close(fig_vio)

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
    plt.savefig(os.path.join(OUT_DIR, "violin_integration_boxplot.png"), dpi=300, bbox_inches="tight")
    plt.close(fig_box)


if __name__ == "__main__":
    main()
