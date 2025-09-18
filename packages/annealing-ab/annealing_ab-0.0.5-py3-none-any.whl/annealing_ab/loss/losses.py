from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from scipy.stats import ks_2samp, levene, ttest_ind


class BaseLoss(ABC):
    """
    Abstract base class for statistical loss functions in A/B testing.

    This class provides an interface for implementing different statistical
    tests to measure how well a subset matches a target population. Each
    concrete subclass must define how to calculate test statistics, convert
    them into normalized values, and produce a scalar loss for optimization.

    Parameters
    ----------
    X : np.ndarray, optional
        Subset dataset (e.g., A/B test group), by default an empty array.
    Y : np.ndarray, optional
        Target dataset (e.g., full population), by default an empty array.

    Attributes
    ----------
    X : np.ndarray
        Subset dataset.
    Y : np.ndarray
        Target dataset.
    criteria_name : str
        Descriptive name of the loss criterion. Must be defined in subclasses.
    """

    criteria_name: str = None

    def __init__(self, X: Optional[np.ndarray] = None, Y: Optional[np.ndarray] = None) -> None:
        if not isinstance(self.criteria_name, str):
            raise TypeError(f"{self.__class__.__name__}.criteria_name must be a string")
        self.X = X.copy() if X is not None else np.array([])
        self.Y = Y.copy() if Y is not None else np.array([])

    @abstractmethod
    def calculate_test_statistic(self) -> np.ndarray:
        """
        Compute the raw test statistics comparing X and Y.

        Each concrete subclass should implement the appropriate statistical
        test for the datasets. The result is typically per-feature.

        Returns
        -------
        np.ndarray
            Array of test statistics, one per feature dimension.
        """
        pass

    @abstractmethod
    def normalization_functions(self, test_stats: np.ndarray) -> np.ndarray:
        """
        Apply normalization or scaling to the test statistics.

        This allows different statistical tests to produce values
        that are comparable or suitable for the loss function.

        Parameters
        ----------
        test_stats : np.ndarray
            Raw test statistics from `calculate_test_statistic`.

        Returns
        -------
        np.ndarray
            Normalized test statistics.
        """
        pass

    @abstractmethod
    def loss_function(self, test_stats: np.ndarray) -> float:
        """
        Convert normalized test statistics into a scalar loss value.

        Each subclass defines how to combine multiple test statistics
        into a single value suitable for optimization.

        Parameters
        ----------
        test_stats : np.ndarray
            Normalized test statistics.

        Returns
        -------
        float
            Single loss value.
        """
        pass

    def calculate_norm_test_statistic(self) -> np.ndarray:
        """
        Calculate the normalized test statistics.

        Convenience method that combines `calculate_test_statistic` with
        `normalization_functions`.

        Returns
        -------
        np.ndarray
            Normalized test statistics.
        """
        return self.normalization_functions(self.calculate_test_statistic())

    @abstractmethod
    def calculate_p_value(self) -> np.ndarray:
        pass

    def calculate_loss(self) -> float:
        """
        Compute the total loss for the current datasets.

        This method first calculates the normalized test statistics
        and then converts them into a scalar loss using `loss_function`.

        Returns
        -------
        float
            Total loss value.
        """
        return self.loss_function(self.calculate_norm_test_statistic())

    def update(
        self,
        new_val: Optional[np.ndarray] = None,
        old_val: Optional[np.ndarray] = None,
        X: Optional[np.ndarray] = None,
        Y: Optional[np.ndarray] = None,
    ) -> None:
        """
        Update the datasets with new values.

        Can replace the full dataset or allow incremental updates
        by specifying new and old values. Subclasses can override
        to efficiently handle incremental changes.

        Parameters
        ----------
        new_val : np.ndarray, optional
            New values to add, by default None.
        old_val : np.ndarray, optional
            Old values to remove, by default None.
        X : np.ndarray, optional
            Full replacement for subset dataset, by default None.
        Y : np.ndarray, optional
            Full replacement for target dataset, by default None.
        """
        if X is not None:
            self.X = X.copy()
        if Y is not None:
            self.Y = Y.copy()


class TTestLoss(BaseLoss):
    """
    T-test based loss function for comparing two populations.

    This class implements a two-sample t-test to compare means between
    two populations. It supports both equal and unequal variance assumptions
    and provides efficient incremental updates for optimization.

    Parameters
    ----------
    X : np.ndarray
        First dataset (subset population).
    Y : np.ndarray
        Second dataset (target population).
    new_val : np.ndarray or None, optional
        New value for incremental updates, by default None.
    old_val : np.ndarray or None, optional
        Old value for incremental updates, by default None.
    equal_var : bool, optional
        Whether to assume equal variances, by default False.

    Attributes
    ----------
    new_val : np.ndarray or None
        New value for incremental updates.
    old_val : np.ndarray or None
        Old value for incremental updates.
    equal_var : bool
        Whether to assume equal variances.
    mean_X : np.ndarray
        Mean of first dataset.
    var_X : np.ndarray
        Variance of first dataset.
    n_X : int
        Sample size of first dataset.
    mean_Y : np.ndarray
        Mean of second dataset.
    var_Y : np.ndarray
        Variance of second dataset.
    n_Y : int
        Sample size of second dataset.
    criteria_name : str
        Descriptive name of the loss criterion. Must be defined in subclasses.
    """

    criteria_name = "ttest"

    def __init__(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        new_val: Optional[np.ndarray] = None,
        old_val: Optional[np.ndarray] = None,
        equal_var: bool = False,
    ) -> None:
        super().__init__(X, Y)
        self.new_val = new_val
        self.old_val = old_val
        self.equal_var = equal_var
        self.mean_X, self.var_X, self.n_X = self._compute_stats(self.X)
        self.mean_Y, self.var_Y, self.n_Y = self._compute_stats(self.Y)

    def loss_function(self, test_stats: np.ndarray) -> float:
        """
        Convert t-test statistics to loss value.

        Uses a custom loss function that penalizes large t-statistics
        more heavily, encouraging better matches between populations.

        Parameters
        ----------
        test_stats : np.ndarray
            Array of t-test statistics.

        Returns
        -------
        float
            Loss value based on t-test statistics.
        """
        return np.mean(-((1 - test_stats) ** 5) * 5 * np.log(test_stats))

    def _compute_stats(self, arr: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
        """
        Compute mean, variance, and sample size for an array.

        Parameters
        ----------
        arr : np.ndarray
            Input array to compute statistics for.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, int]
            Tuple containing (mean, variance, sample_size).
        """
        mean = arr.mean(axis=0)
        var = np.var(arr, ddof=1, axis=0)
        return mean, var, len(arr)

    def _update_mean_var_x(self) -> None:
        """
        Update mean and variance of X using incremental formulas.

        This method efficiently updates the statistics when only
        one element changes, avoiding full recomputation.

        Returns
        -------
        None
        """
        if self.new_val is not None and self.old_val is not None:
            new_mean = self.mean_X + (self.new_val - self.old_val) / self.n_X
            new_var = self.var_X + (
                (self.new_val - self.old_val)
                * (self.new_val - self.mean_X + self.old_val - new_mean)
            ) / (self.n_X - 1)
            self.mean_X = new_mean
            self.var_X = new_var

    def update(
        self,
        new_val: Optional[np.ndarray] = None,
        old_val: Optional[np.ndarray] = None,
        X: Optional[np.ndarray] = None,
        Y: Optional[np.ndarray] = None,
    ) -> None:
        """
        Update datasets with new values.

        Supports both incremental updates (for optimization) and
        full dataset updates.

        Parameters
        ----------
        new_val : np.ndarray or None, optional
            New value for incremental update, by default None.
        old_val : np.ndarray or None, optional
            Old value for incremental update, by default None.
        X : np.ndarray or None, optional
            New first dataset, by default None.
        Y : np.ndarray or None, optional
            New second dataset, by default None.

        Returns
        -------
        None
        """
        if new_val is not None and old_val is not None:
            self.new_val = new_val
            self.old_val = old_val
            self._update_mean_var_x()
        else:
            super().update(X=X, Y=Y)
            self.mean_X, self.var_X, self.n_X = self._compute_stats(self.X)
            self.mean_Y, self.var_Y, self.n_Y = self._compute_stats(self.Y)

    def calculate_test_statistic(self) -> np.ndarray:
        """
        Calculate t-test statistics between the two populations.

        Computes two-sample t-test statistics, supporting both equal
        and unequal variance assumptions.

        Returns
        -------
        np.ndarray
            Array of t-test statistics converted to similarity scores.
        """
        if self.equal_var:
            pooled_var = ((self.n_X - 1) * self.var_X + (self.n_Y - 1) * self.var_Y) / (
                self.n_X + self.n_Y - 2
            )
            pooled_var = np.where(pooled_var == 0, 1e-16, pooled_var)
            t_stat = (self.mean_X - self.mean_Y) / np.sqrt(
                pooled_var * (1 / self.n_X + 1 / self.n_Y)
            )
        else:
            pooled_var = self.var_X / self.n_X + self.var_Y / self.n_Y
            pooled_var = np.where(pooled_var == 0, 1e-16, pooled_var)
            t_stat = (self.mean_X - self.mean_Y) / np.sqrt(pooled_var)
        return t_stat

    def normalization_functions(self, test_stats: np.ndarray) -> np.ndarray:
        """
        Normalize t-test statistics to similarity scores in [0, 1].

        Formula: similarity = 1 / (1 + |t_stat|)

        Parameters
        ----------
        test_stats : np.ndarray
            Raw t-test statistics.

        Returns
        -------
        np.ndarray
            Normalized similarity scores.
        """
        return 1 / (1 + np.abs(test_stats))

    def calculate_p_value(self) -> np.ndarray:
        _, pvals = ttest_ind(self.X, self.Y, equal_var=self.equal_var)
        return pvals[0]


class KSLoss(BaseLoss):
    """
    Kolmogorov-Smirnov test based loss function for comparing distributions.

    This class implements the two-sample Kolmogorov-Smirnov test to compare
    the empirical cumulative distribution functions of two populations.
    It measures the maximum difference between the CDFs across all features.

    Parameters
    ----------
    X : np.ndarray or None, optional
        First dataset (subset population), by default None.
    Y : np.ndarray or None, optional
        Second dataset (target population), by default None.

    Attributes
    ----------
    X : np.ndarray
        First dataset (subset population).
    Y : np.ndarray
        Second dataset (target population).
    criteria_name : str
        Descriptive name of the loss criterion. Must be defined in subclasses.
    """

    criteria_name = "KS"

    def calculate_test_statistic(self) -> np.ndarray:
        """
        Calculate Kolmogorov-Smirnov test statistics.

        Computes the maximum difference between empirical CDFs
        for each feature dimension.

        Returns
        -------
        np.ndarray
            Array of KS test statistics (maximum CDF differences).
        """
        D_list = []
        for i in range(self.X.shape[1]):
            all_vals = np.sort(np.concatenate([self.X[:, i], self.Y[:, i]]))
            cdf_X = np.searchsorted(np.sort(self.X[:, i]), all_vals, side="right") / len(self.X)
            cdf_Y = np.searchsorted(np.sort(self.Y[:, i]), all_vals, side="right") / len(self.Y)
            D_list.append(np.max(np.abs(cdf_X - cdf_Y)))
        return np.array(D_list)

    def normalization_functions(self, test_stats: np.ndarray) -> np.ndarray:
        """
        Normalize KS statistics to similarity scores in [0, 1].

        Formula: similarity = 1 - D

        Parameters
        ----------
        test_stats : np.ndarray
            Raw KS statistics.

        Returns
        -------
        np.ndarray
            Normalized similarity scores.
        """
        return 1 - test_stats

    def loss_function(self, test_stats: np.ndarray) -> float:
        """
        Convert KS test statistics to loss value.

        Uses a custom loss function that penalizes large KS statistics
        more heavily, encouraging better distribution matches.

        Parameters
        ----------
        test_stats : np.ndarray
            Array of KS test statistics.

        Returns
        -------
        float
            Loss value based on KS test statistics.
        """
        eps = 1e-16
        test_stats = np.clip(test_stats, eps, 1)
        return np.mean(-((1 - test_stats) ** 0.5) * 2 * np.log(test_stats))

    def calculate_p_value(self) -> np.ndarray:
        n_features = self.X.shape[1]
        pvals = np.zeros(n_features)
        for i in range(n_features):
            _, pvals[i] = ks_2samp(self.X[:, i], self.Y[:, i])
        return pvals[0]


class LeveneLoss(BaseLoss):
    """
    Levene's test based loss function for comparing variances.

    This class implements Levene's test to compare the variances of two
    populations. It tests whether the variances are equal across groups
    by examining the absolute deviations from group means.

    Parameters
    ----------
    X : np.ndarray or None, optional
        First dataset (subset population), by default None.
    Y : np.ndarray or None, optional
        Second dataset (target population), by default None.

    Attributes
    ----------
    X : np.ndarray
        First dataset (subset population).
    Y : np.ndarray
        Second dataset (target population).
    criteria_name : str
        Descriptive name of the loss criterion. Must be defined in subclasses.
    """

    criteria_name = "levene"

    def calculate_test_statistic(self) -> np.ndarray:
        """
        Calculate Levene's test statistics.

        Computes the Levene's W statistic for each feature dimension,
        testing for equal variances between the two populations.

        Returns
        -------
        np.ndarray
            Array containing a single Levene's test statistic.
        """
        Z_X = np.abs(self.X - self.X.mean(axis=0))  # (n_X, d)
        Z_Y = np.abs(self.Y - self.Y.mean(axis=0))  # (n_Y, d)

        mean_Z_X = Z_X.mean(axis=0)  # (d,)
        mean_Z_Y = Z_Y.mean(axis=0)  # (d,)

        numerator = (
            len(self.X) * (mean_Z_X - (mean_Z_X + mean_Z_Y) / 2) ** 2
            + len(self.Y) * (mean_Z_Y - (mean_Z_X + mean_Z_Y) / 2) ** 2
        )  # (d,)

        denominator = ((Z_X - mean_Z_X) ** 2).sum(axis=0) + ((Z_Y - mean_Z_Y) ** 2).sum(
            axis=0
        )  # (d,)

        W = (len(self.X) + len(self.Y) - 2) * (numerator / denominator)  # (d,)

        # Average across columns to get a single number
        return W

    def normalization_functions(self, test_stats: np.ndarray) -> np.ndarray:
        """
        Normalize Levene's statistics to similarity scores in [0, 1].

        Formula: similarity = 1 / (1 + |W|)

        Parameters
        ----------
        test_stats : np.ndarray
            Raw Levene's W statistics.

        Returns
        -------
        np.ndarray
            Normalized similarity scores.
        """
        return 1 / (1 + np.abs(test_stats))

    def loss_function(self, test_stats: np.ndarray) -> float:
        """
        Convert Levene's test statistics to loss value.

        Uses a custom loss function that penalizes large Levene statistics
        more heavily, encouraging better variance matches.

        Parameters
        ----------
        test_stats : np.ndarray
            Array of Levene's test statistics.

        Returns
        -------
        float
            Loss value based on Levene's test statistics.
        """
        return np.mean(-((1 - test_stats) ** 1) * 5 * np.log(test_stats))

    def calculate_p_value(self) -> np.ndarray:
        n_features = self.X.shape[1]
        pvals = np.zeros(n_features)
        for i in range(n_features):
            _, pvals[i] = levene(self.X[:, i], self.Y[:, i])
        return pvals[0]
