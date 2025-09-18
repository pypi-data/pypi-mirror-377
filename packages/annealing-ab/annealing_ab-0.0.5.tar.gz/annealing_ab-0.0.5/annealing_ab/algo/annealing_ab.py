import copy
from typing import List, Optional, Tuple, Type

import numpy as np
import pandas as pd

from annealing_ab.analysis.charts import FeatureDistributionVisualizer, LossVisualizer
from annealing_ab.analysis.results import MultiCriteriaEvaluator
from annealing_ab.loss.losses import BaseLoss, KSLoss, LeveneLoss, TTestLoss


class AnnealingAB:
    """
    Simulated Annealing algorithm for A/B testing population selection.

    This class implements a simulated annealing optimization algorithm to find
    a subset of the general population that best matches the target population
    based on statistical criteria.

    Parameters
    ----------
    general_population : pd.DataFrame
        The full population from which to select a subset.
    target_population : pd.DataFrame
        The target population to match against. It is taken from the
        general population and at the same time
        the general population does not contain the target.
        The target group can be the general population, when we want to select
        a test and control group from the general one at once, so that they
        describe the general population.
    class_loss : Type[BaseLoss]
        Class that calculates how well the subset matches the target.
    fk_key : str
        Column name that serves as the foreign key identifier.
    n_sub : int
        Number of samples to select from the general population.
    temperature : float, optional
        Initial temperature for the annealing process, by default 100.0.
    cooling_rate : float, optional
        Rate at which temperature decreases, by default 0.95.
    min_temperature : float, optional
        Minimum temperature threshold, by default 1e-3.
    max_iterations : int, optional
        Maximum number of iterations to run, by default 1000.
    random_state : int or None, optional
        Random seed for reproducible results, by default None.
    early_stop_k : int, optional
        Number of recent iterations to check for early stopping, by default 50.
    early_stop_eps : float, optional
        Minimum improvement threshold for early stopping, by default 1e-4.

    Attributes
    ----------
    temperature : float
        Current temperature of the annealing process.
    cooling_rate : float
        Rate at which temperature decreases.
    min_temperature : float
        Minimum temperature threshold.
    max_iterations : int
        Maximum number of iterations to run.
    random_state : np.random.RandomState
        Random number generator for reproducible results.
    history_loss : list[float]
        History of loss values during optimization.
    early_stop_k : int
        Number of recent iterations to check for early stopping.
    early_stop_eps : float
        Minimum improvement threshold for early stopping.
    fk_key : str
        Column name that serves as the foreign key identifier.
    general_population : pd.DataFrame
        The full population from which to select a subset.
    target_population : pd.DataFrame
        The target population to match against.
    class_loss : Type[BaseLoss]
        Class for calculating match quality.
    n_sub : int
        Number of samples to select from the general population.
    best_subset: pd.DataFrame | None
        selected subset
    """

    def __init__(
        self,
        general_population: pd.DataFrame,
        target_population: pd.DataFrame,
        class_loss: Type[BaseLoss],
        fk_key: str,
        n_sub: int,
        temperature: float = 100.0,
        cooling_rate: float = 0.95,
        min_temperature: float = 1e-3,
        max_iterations: int = 1000,
        random_state: Optional[int] = None,
        early_stop_k: int = 50,
        early_stop_eps: float = 1e-4,
    ) -> None:
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.max_iterations = max_iterations
        self.random_state = np.random.RandomState(random_state)

        self.history_loss = []

        self.early_stop_k = early_stop_k
        self.early_stop_eps = early_stop_eps

        self.fk_key = fk_key

        self.general_population = general_population
        self.target_population = target_population
        self._fk_key_fisrt_col()

        self.eval_loss_classes = class_loss
        self.test_stats_criteria = None

        self.n_sub = n_sub

        self.best_subset = None

    def _acceptance_probability(self, old_loss: float, new_loss: float) -> float:
        """
        Calculate the probability of accepting a new solution.

        In simulated annealing, worse solutions can be accepted with a probability
        that decreases as temperature decreases. This helps escape local optima.

        Parameters
        ----------
        old_loss : float
            Loss value of the current solution.
        new_loss : float
            Loss value of the proposed new solution.

        Returns
        -------
        float
            Probability between 0 and 1 of accepting the new solution.
        """
        if new_loss < old_loss:
            return 1.0
        return np.exp((old_loss - new_loss) / self.temperature)

    def _cool_down(self) -> None:
        """
        Reduce the temperature according to the cooling rate.

        Temperature is gradually reduced to make the algorithm more selective
        over time, eventually only accepting better solutions.

        Returns
        -------
        None
        """
        if self.temperature > self.min_temperature:
            self.temperature *= self.cooling_rate
            if self.temperature < self.min_temperature:
                self.temperature = self.min_temperature

    def _early_stop(self) -> bool:
        """
        Check if the algorithm should stop early due to lack of improvement.

        The algorithm stops early if the loss values in the recent window
        have not improved by more than the threshold.

        Returns
        -------
        bool
            True if the algorithm should stop early, False otherwise.
        """
        if len(self.history_loss) > self.early_stop_k:
            window = self.history_loss[-self.early_stop_k :]
            return max(window) - min(window) < self.early_stop_eps
        return False

    def _neighboring_state(
        self, X: np.ndarray, Y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate a neighboring state by swapping elements between two arrays.

        This method creates a new solution by randomly selecting one element
        from each array and swapping them. This is the core operation for
        exploring the solution space in simulated annealing.

        Parameters
        ----------
        X : np.ndarray
            First array (subset of general population).
        Y : np.ndarray
            Second array (remaining general population).

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            A tuple containing:
            - X_new: Modified first array after swap
            - Y_new: Modified second array after swap
            - old_val: Original value from X that was swapped out
            - new_val: Original value from Y that was swapped in
        """
        n_X, n_Y = len(X), len(Y)
        ind_X, ind_Y = np.random.randint(0, n_X), np.random.randint(0, n_Y)
        X_new, Y_new = np.copy(X), np.copy(Y)
        X_new[ind_X] = Y[ind_Y]
        Y_new[ind_Y] = X[ind_X]
        return X_new, Y_new, np.copy(X[ind_X]), np.copy(Y[ind_Y])

    def _initial_state(self, general_population: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create the initial state by randomly selecting a subset from the general population.

        This method randomly selects n_sub samples from the general population
        to form the initial subset, with the remaining samples forming the
        complement set.

        Parameters
        ----------
        general_population : np.ndarray
            The full population array to sample from.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            A tuple containing:
            - subset: Randomly selected subset of size n_sub
            - general_without_subset: Remaining population after subset removal
        """
        X = general_population.copy()
        n = X.shape[0]
        idx = np.random.choice(n, self.n_sub, replace=False)
        mask = np.ones(n, dtype=bool)
        mask[idx] = False
        subset = X[idx].copy()
        general_without_subset = X[mask].copy()
        return subset, general_without_subset

    def _fk_key_fisrt_col(self) -> None:
        """
        Move the foreign key column to the first position in both DataFrames.

        This ensures that the foreign key column is always in the first position
        for consistent indexing when working with numpy arrays.

        Returns
        -------
        None
        """

        def move_fk_key_first(df: pd.DataFrame, key: str) -> pd.DataFrame:
            cols = [key] + [c for c in df.columns if c != key]
            return df[cols]

        self.general_population = move_fk_key_first(self.general_population, self.fk_key)
        self.target_population = move_fk_key_first(self.target_population, self.fk_key)

    def loss_chart(self):
        """
        Visualize the loss history over iterations.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The function displays the plot but does not return any value.
        """
        loss_visual = LossVisualizer(self.history_loss)
        loss_visual.plot()

    def distribution_chart(self, plot_type: str):
        """
        Visualize the feature distributions for the subset and target datasets.

        Parameters
        ----------
        plot_type : str
            Type of plot to generate.
            (e.g., 'hist', 'kde').

        Returns
        -------
        None
            The function displays the plots but does not return any value.
        """
        visual = FeatureDistributionVisualizer(
            df1=self.best_subset,
            df2=self.target_population,
            fk_key=self.fk_key,
            plot_type=plot_type,
            dataset1_name="subset",
            dataset2_name="target",
        )
        visual.plot_distributions()

    def criteria_p_value_report(
        self, loss_classes: List[Type[BaseLoss]] = [TTestLoss, KSLoss, LeveneLoss]
    ) -> pd.DataFrame:
        """
        Generate a report of statistics for multiple loss criteria.

        Parameters
        ----------
        loss_classes : list of Type[BaseLoss], optional
            List of loss classes to evaluate. Defaults to [TTestLoss, KSLoss, LeveneLoss].

        Returns
        -------
        pd.DataFrame
            DataFrame with feature names in the first column and
            p_value for each loss criterion in the subsequent columns.
        """
        eval_criteria = MultiCriteriaEvaluator(
            df1=self.best_subset,
            df2=self.target_population,
            fk_key=self.fk_key,
            loss_classes=loss_classes,
        )
        return eval_criteria.evaluate()

    def run(self) -> np.ndarray:
        """
        Run the simulated annealing optimization algorithm.

        This method executes the main optimization loop, iteratively exploring
        the solution space by generating neighboring states and accepting or
        rejecting them based on the acceptance probability and temperature.

        Returns
        -------
        np.ndarray
            The best subset found that matches the target population.
        """
        target_np = self.target_population.copy().to_numpy()
        general_np = self.general_population.copy().to_numpy()

        subset, general_without_subset = self._initial_state(general_np)
        self.test_stats_criteria = self.eval_loss_classes(X=subset[:, 1:], Y=target_np[:, 1:])
        current_loss = self.test_stats_criteria.calculate_loss()

        for _ in range(self.max_iterations):
            subset_new, general_without_subset_new, old_val, new_val = self._neighboring_state(
                subset, general_without_subset
            )
            temp_test_criteria = copy.deepcopy(self.test_stats_criteria)
            temp_test_criteria.update(
                new_val=new_val[1:], old_val=old_val[1:], X=subset_new[:, 1:].copy()
            )
            new_loss = temp_test_criteria.calculate_loss()
            if self.random_state.rand() < self._acceptance_probability(current_loss, new_loss):
                current_loss = new_loss
                subset = subset_new
                general_without_subset = general_without_subset_new

                self.test_stats_criteria.update(
                    new_val=new_val[1:], old_val=old_val[1:], X=subset_new[:, 1:]
                )
                self.history_loss.append(current_loss)
            self._cool_down()
            if self._early_stop():
                break

        subset_df = pd.DataFrame(subset, columns=self.target_population.columns)
        self.best_subset = subset_df
        return subset_df
