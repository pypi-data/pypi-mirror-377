import math
from typing import List, Optional
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class LossVisualizer:
    """
    Visualize loss values across iterations.

    Parameters
    ----------
    values : list[float] | numpy.ndarray
        List or array of loss values.
    """

    def __init__(self, values):
        self.values = values

    def plot(self):
        """
        Plot the loss values.
        """
        plt.figure(figsize=(8, 5))
        plt.plot(self.values, linestyle="-", color="b")
        plt.title("Loss Over Iterations")
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.grid(True)
        plt.show()


class FeatureDistributionVisualizer:
    """
    Visualize distributions of features from two datasets.

    Parameters
    ----------
    df1 : pd.DataFrame
        First dataset.
    df2 : pd.DataFrame
        Second dataset.
    fk_key : str
        Column name to exclude from plotting (usually an ID column).
    columns : Optional[List[str]]
        List of feature columns to plot. If None, all columns except fk_key are used.
    n_rows : Optional[int]
        Number of rows in subplot grid. If None, automatically determined.
    n_cols : Optional[int]
        Number of columns in subplot grid. If None, automatically determined.
    plot_type : str
        Type of plot: "hist" for histogram, "kde" for kernel density estimate.
    dataset1_name : str
        Name of the first dataset to show in legend.
    dataset2_name : str
        Name of the second dataset to show in legend.
    """

    def __init__(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        fk_key: str,
        columns: Optional[List[str]] = None,
        n_rows: Optional[int] = None,
        n_cols: Optional[int] = None,
        plot_type: str = "hist",
        dataset1_name: str = "Dataset 1",
        dataset2_name: str = "Dataset 2",
    ):
        self.df1 = df1
        self.df2 = df2
        self.fk_key = fk_key
        self.columns = columns if columns is not None else self._get_all_columns()
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.plot_type = plot_type
        self.dataset1_name = dataset1_name
        self.dataset2_name = dataset2_name

        self._check_columns_exist()

    def _get_all_columns(self) -> List[str]:
        """Return all columns except fk_key"""
        return [col for col in self.df1.columns if col != self.fk_key]

    def _check_columns_exist(self):
        """Check that all columns exist in both datasets"""
        missing_in_df1 = [col for col in self.columns if col not in self.df1.columns]
        missing_in_df2 = [col for col in self.columns if col not in self.df2.columns]

        if missing_in_df1:
            raise ValueError(f"Columns missing in first dataset: {missing_in_df1}")
        if missing_in_df2:
            raise ValueError(f"Columns missing in second dataset: {missing_in_df2}")

    def plot_distributions(self):
        """
        Plot distributions for each column in columns list from both datasets.
        """
        warnings.simplefilter(action="ignore", category=FutureWarning)

        n_features = len(self.columns)

        # Determine subplot grid automatically if not specified
        if self.n_rows is None and self.n_cols is None:
            self.n_cols = math.ceil(math.sqrt(n_features))
            self.n_rows = math.ceil(n_features / self.n_cols)
        elif self.n_rows is None:
            self.n_rows = math.ceil(n_features / self.n_cols)
        elif self.n_cols is None:
            self.n_cols = math.ceil(n_features / self.n_rows)

        fig, axes = plt.subplots(
            self.n_rows, self.n_cols, figsize=(5 * self.n_cols, 4 * self.n_rows)
        )
        axes = np.array(axes).reshape(-1)  # flatten in case of 2D array

        for i, col in enumerate(self.columns):
            ax = axes[i]

            if self.plot_type == "hist":
                ax.hist(
                    self.df1[col],
                    bins=30,
                    alpha=0.5,
                    label=self.dataset1_name,
                    color="blue",
                    density=True,
                )
                ax.hist(
                    self.df2[col],
                    bins=30,
                    alpha=0.5,
                    label=self.dataset2_name,
                    color="orange",
                    density=True,
                )
            elif self.plot_type == "kde":
                sns.kdeplot(
                    self.df1[col],
                    ax=ax,
                    label=self.dataset1_name,
                    color="blue",
                    fill=True,
                    alpha=0.5,
                )
                sns.kdeplot(
                    self.df2[col],
                    ax=ax,
                    label=self.dataset2_name,
                    color="orange",
                    fill=True,
                    alpha=0.5,
                )
            else:
                raise ValueError("plot_type must be 'hist' or 'kde'")

            ax.set_title(f"Distribution of {col}")
            ax.set_xlabel(col)
            ax.set_ylabel("Density")
            ax.legend()

        # Turn off any extra subplots
        for j in range(i + 1, len(axes)):
            axes[j].axis("off")

        plt.tight_layout()
        plt.show()
