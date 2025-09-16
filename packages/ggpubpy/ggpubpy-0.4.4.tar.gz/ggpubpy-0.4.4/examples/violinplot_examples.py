#!/usr/bin/env python3
"""
Violin plot examples for ggpubpy using the Iris dataset.

Generates the images referenced in docs/violinplot.md:
- violin_example.png (3 groups, non-parametric)
- violin_2groups_example.png (2 groups, parametric)
- violin_3groups_example.png (3 groups, parametric with ordering and palette)
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

    # 1) 3 groups (non-parametric)
    print("Generating violin_example.png ...")
    fig, ax = ggpubpy.plot_violin(
        df=iris,
        x="species",
        y="sepal_length",
        x_label="Species",
        y_label="Sepal Length (cm)",
        title="Iris: Sepal Length by Species",
        subtitle="Violin plot with non-parametric tests",
        parametric=False,
        alpha=0.6,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "violin_example.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 2) 2 groups (parametric)
    print("Generating violin_2groups_example.png ...")
    iris_2 = iris[iris["species"].isin(["setosa", "versicolor"])]
    fig, ax = ggpubpy.plot_violin(
        df=iris_2,
        x="species",
        y="sepal_length",
        x_label="Species",
        y_label="Sepal Length (cm)",
        title="Iris: Setosa vs Versicolor",
        subtitle="Violin plot with t-test",
        parametric=True,
        alpha=0.6,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "violin_2groups_example.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 3) 3 groups with ordering and palette (for docs example)
    print("Generating violin_3groups_example.png ...")
    order = ["setosa", "versicolor", "virginica"]
    palette = {"setosa": "#FF6B6B", "versicolor": "#4ECDC4", "virginica": "#45B7D1"}
    fig, ax = ggpubpy.plot_violin(
        df=iris,
        x="species",
        y="petal_length",
        x_label="Species",
        y_label="Petal Length (cm)",
        title="Petal Length Distribution by Species",
        order=order,
        palette=palette,
        figsize=(8, 6),
        parametric=True,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "violin_3groups_example.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("Done generating violin plot examples.")


if __name__ == "__main__":
    main()
