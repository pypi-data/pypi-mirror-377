from abc import ABC, abstractmethod
import itertools
import random
from typing import Any, Dict, List, Type

import pandas as pd
from tqdm.auto import tqdm

from annealing_ab.algo.annealing_ab import AnnealingAB
from annealing_ab.analysis.results import MultiCriteriaEvaluator
from annealing_ab.loss.losses import BaseLoss


class BaseSelector(ABC):
    """
    Abstract base class for selecting groups from a dataset.

    Parameters
    ----------
    general : pd.DataFrame
        General population dataset.
    fk_key : str
        Column name used as unique identifier (foreign key).
    random_state : int
        Seed for random number generation.
    target : pd.DataFrame or None, optional
        Target population dataset, by default None.
    """

    def __init__(
        self,
        general: pd.DataFrame,
        fk_key: str,
        random_state: int,
        target: None | pd.DataFrame = None,
    ):
        self.general = general
        self.target = target
        self.fk_key = fk_key
        self.random_state = random_state

        self.control_annealer = None
        self.test_annealer = None

    @abstractmethod
    def select(self, **params) -> Dict[str, pd.DataFrame]:
        """
        Select groups based on provided parameters.

        Parameters
        ----------
        **params : dict
            Extra parameters for group selection.

        Returns
        -------
        dict of str -> pd.DataFrame
            Selected groups, e.g. {"control": df1, "test": df2}.
        """
        pass


class SingleGroupSelector(BaseSelector):
    """
    Selector for creating a single control group from the general population.

    Parameters
    ----------
    general : pd.DataFrame
        General population dataset.
    target : pd.DataFrame
        Target population dataset.
    fk_key : str
        Column name used as unique identifier (foreign key).
    n_sub : int
        Number of rows to select for the group.
    random_state : int
        Seed for random number generation.
    **annealer_params : dict
        Extra parameters passed to the AnnealingAB algorithm.
    """

    def __init__(
        self,
        general: pd.DataFrame,
        target: pd.DataFrame,
        fk_key: str,
        n_sub: int,
        random_state: int,
        **annealer_params,
    ):
        super().__init__(general, fk_key, random_state, target)
        self.n_sub = n_sub
        self.annealer_params = annealer_params

    def select(self, **extra_params):
        """
        Run simulated annealing to select a control group.

        Parameters
        ----------
        **extra_params : dict
            Extra annealing parameters.

        Returns
        -------
        dict of str -> pd.DataFrame
            Selected control group and given test group.
        """
        annealer = AnnealingAB(
            general_population=self.general,
            target_population=self.target,
            fk_key=self.fk_key,
            n_sub=self.n_sub,
            **self.annealer_params,
            **extra_params,
        )
        control = annealer.run()
        self.control_annealer = annealer
        return {"control": control, "test": self.target}


class TwoGroupSelector(BaseSelector):
    """
    Selector for creating both control and test groups from the general population.

    Parameters
    ----------
    general : pd.DataFrame
        General population dataset.
    target : pd.DataFrame
        Target population dataset.
    fk_key : str
        Column name used as unique identifier (foreign key).
    n_sub : int
        Number of rows to select for each group.
    random_state : int
        Seed for random number generation.
    **annealer_params : dict
        Extra parameters passed to the AnnealingAB algorithm.
    """

    def __init__(
        self,
        general: pd.DataFrame,
        target: pd.DataFrame,
        fk_key: str,
        n_sub: int,
        random_state: int,
        **annealer_params,
    ):
        super().__init__(general, fk_key, random_state, target)
        self.n_sub = n_sub
        self.annealer_params = annealer_params

    def select(self, **extra_params) -> Dict[str, pd.DataFrame]:
        """
        Run simulated annealing twice to create test and control groups.

        Parameters
        ----------
        **extra_params : dict
            Extra annealing parameters.

        Returns
        -------
        dict of str -> pd.DataFrame
            Selected control group, test group, and the original general population.
        """
        test_annealer = AnnealingAB(
            general_population=self.general,
            target_population=self.target,
            fk_key=self.fk_key,
            n_sub=self.n_sub,
            **self.annealer_params,
            **extra_params,
        )
        test = test_annealer.run()

        remaining = self.general[~self.general[self.fk_key].isin(test[self.fk_key])]

        control_annealer = AnnealingAB(
            general_population=remaining,
            target_population=self.target,
            fk_key=self.fk_key,
            n_sub=self.n_sub,
            **self.annealer_params,
            **extra_params,
        )
        control = control_annealer.run()
        self.test_annealer = test_annealer
        self.control_annealer = control_annealer

        return {"control": control, "test": test, "general": self.general}


class Evaluator:
    """
    Evaluate similarity between groups using multiple loss criteria.

    Parameters
    ----------
    loss_classes : list of type[BaseLoss]
        List of loss classes used for evaluation.
    fk_key : str
        Column name used as unique identifier (foreign key).
    columns : list of str or None, optional
        Subset of columns to evaluate. If None, all columns are used.
    """

    def __init__(
        self, loss_classes: list[type[BaseLoss]], fk_key: str, columns: list[str] | None = None
    ):
        self.loss_classes = loss_classes
        self.fk_key = fk_key
        self.columns = columns

    def evaluate(self, groups: Dict[str, pd.DataFrame]) -> float:
        """
        Evaluate group pairs and return the minimum score.

        Parameters
        ----------
        groups : dict of str -> pd.DataFrame
            Dictionary of groups: control, test, general.

        Returns
        -------
        float
            Minimum evaluation score.
        """
        scores: List[float] = []

        if groups.get("test") is not None and groups.get("control") is not None:
            scores.append(self._eval_pair(groups["test"], groups["control"]))

        if groups.get("test") is not None and groups.get("general") is not None:
            scores.append(self._eval_pair(groups["test"], groups["general"]))

        if groups.get("control") is not None and groups.get("general") is not None:
            scores.append(self._eval_pair(groups["control"], groups["general"]))
        return min(scores)

    def _eval_pair(self, df1: pd.DataFrame, df2: pd.DataFrame) -> float:
        """
        Evaluate a pair of datasets with all loss functions.

        Parameters
        ----------
        df1 : pd.DataFrame
            First dataset.
        df2 : pd.DataFrame
            Second dataset.

        Returns
        -------
        float
            Minimum score across all loss functions.
        """
        evaluator = MultiCriteriaEvaluator(
            df1=df1,
            df2=df2,
            fk_key=self.fk_key,
            loss_classes=self.loss_classes,
            columns=self.columns,
        )
        results = evaluator.evaluate()
        score = results.select_dtypes(include="number").min().min()
        return float(score)


class Optimizer:
    """
    Optimize group selection parameters using grid search or random search.

    Parameters
    ----------
    general : pd.DataFrame
        General population dataset.
    target : pd.DataFrame
        Target population dataset.
    fk_key : str
        Column name used as unique identifier (foreign key).
    eval_loss_classes : list of type[BaseLoss]
        Loss classes for evaluating group similarity.
    n_sub : int
        Number of rows to select for each group.
    random_state : int
        Seed for random number generation.
    selector_type : str, default="single"
        Type of selector: "single" for one control group, "two" for both control and test.
    columns : list of str or None, optional
        Columns to use in evaluation. If None, all columns are used.
    **selector_params : dict
        Extra parameters for the selector / annealer. Common keys include:
        - loss_classes : BaseLoss class
            Loss function class used for selection.
        - min_temperature : float
            Minimum temperature for simulated annealing.
        - early_stop_k : int
            Number of iterations for early stopping check.
        - early_stop_eps : float
            Minimum change in loss for early stopping.
        - any other parameters accepted by AnnealingAB.
    """

    def __init__(
        self,
        general: pd.DataFrame,
        target: pd.DataFrame,
        fk_key: str,
        eval_loss_classes: List[Type[BaseLoss]],
        n_sub: int,
        random_state: int,
        selector_type: str = "single",  # "single" or "two"
        columns: list[str] | None = None,
        **selector_params,
    ):
        if selector_type == "single":
            selector_cls = SingleGroupSelector
        elif selector_type == "two":
            selector_cls = TwoGroupSelector
        else:
            raise ValueError(f"Unknown selector_type '{selector_type}', use 'single' or 'two'.")

        self.selector: BaseSelector = selector_cls(
            general=general,
            target=target,
            fk_key=fk_key,
            n_sub=n_sub,
            random_state=random_state,
            **selector_params,
        )

        self.evaluator: Evaluator = Evaluator(
            loss_classes=eval_loss_classes, fk_key=fk_key, columns=columns
        )

        self.best_test_annealer = None
        self.best_control_annealer = None

    def grid_search(
        self, param_grid: List[Dict[str, List[Any]]], verbose: bool = True
    ) -> (Dict[str, Any], float):
        """
        Perform grid search over parameter combinations.

        Parameters
        ----------
        param_grid : list of dict
            List of parameter grids to search. Each dictionary defines one grid
            where keys are parameter names and values are lists of possible values.
            Possible keys include:
                - "temperature": float, initial temperature for annealing
                - "cooling_rate": float, rate at which temperature decreases
                - "max_iterations": int, maximum number of iterations
        verbose : bool, default=True
            If True, show progress bar.

        Returns
        -------
        best_params : dict
            Best parameter combination.
        best_score : float
            Best evaluation score.
        """
        all_combinations = []
        for grid in param_grid:
            keys, values = zip(*grid.items())
            for combo in itertools.product(*values):
                all_combinations.append(dict(zip(keys, combo)))

        best_score = -float("inf")
        best_params = None

        iterator = tqdm(all_combinations, desc="Grid Search", disable=not verbose)
        for params in iterator:
            groups = self.selector.select(**params)
            score = self.evaluator.evaluate(groups)
            if score > best_score:
                best_score = score
                best_params = params

                self.best_test_annealer = getattr(self.selector, "test_annealer", None)
                self.best_control_annealer = getattr(self.selector, "control_annealer", None)

            iterator.set_postfix(score=best_score, params=best_params)

        return best_params, best_score

    def random_search(
        self, param_grid: List[Dict[str, List[Any]]], n_iter: int = 10, verbose: bool = True
    ) -> (Dict[str, Any], float):
        """
        Perform random search over parameter combinations.

        Parameters
        ----------
        param_grid : list of dict
            List of parameter grids to sample from. Each dictionary defines one grid
            where keys are parameter names and values are lists of possible values.
            Possible keys include:
                - "temperature": float, initial temperature for annealing
                - "cooling_rate": float, rate at which temperature decreases
                - "max_iterations": int, maximum number of iterations
        n_iter : int, default=10
            Number of iterations.
        verbose : bool, default=True
            If True, show progress bar.

        Returns
        -------
        best_params : dict
            Best parameter combination.
        best_score : float
            Best evaluation score.
        """
        best_score = -float("inf")
        best_params = None

        iterator = tqdm(range(n_iter), desc="Random Search", disable=not verbose)
        for _ in iterator:
            params = {}
            for grid in param_grid:
                for k, v in grid.items():
                    params[k] = random.choice(v) if isinstance(v, list) else v

            groups = self.selector.select(**params)
            score = self.evaluator.evaluate(groups)

            if score > best_score:
                best_score = score
                best_params = params
                self.best_test_annealer = getattr(self.selector, "test_annealer", None)
                self.best_control_annealer = getattr(self.selector, "control_annealer", None)

            iterator.set_postfix(score=best_score, params=best_params)

        return best_params, best_score
