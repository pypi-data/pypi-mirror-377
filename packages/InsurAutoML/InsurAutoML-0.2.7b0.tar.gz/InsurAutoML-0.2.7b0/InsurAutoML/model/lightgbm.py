"""
File Name: lightgbm.py
Author: Panyi Dong
GitHub: https://github.com/PanyiDong/
Mathematics Department, University of Illinois at Urbana-Champaign (UIUC)

Project: InsurAutoML
Latest Version: 0.2.5
Relative Path: /InsurAutoML/model/lightgbm.py
File Created: Monday, 24th October 2022 11:56:57 pm
Author: Panyi Dong (panyid2@illinois.edu)

-----
Last Modified: Monday, 4th December 2023 9:54:20 pm
Modified By: Panyi Dong (panyid2@illinois.edu)

-----
MIT License

Copyright (c) 2022 - 2022, Panyi Dong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from typing import Union, List
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier, LGBMRegressor

from ..constant import (
    LIGHTGBM_BINARY_CLASSIFICATION,
    LIGHTGBM_MULTICLASS_CLASSIFICATION,
    LIGHTGBM_REGRESSION,
    LIGHTGBM_BOOSTING,
    LIGHTGBM_TREE_LEARNER,
)
from .base import BaseModel

##########################################################################
# LightGBM support
# https://lightgbm.readthedocs.io/en/latest/Parameters-Tuning.html


class LightGBM_Base:

    """
    LightGBM Classification/Regression Wrapper

    Parameters
    ----------
    task_type: task type, one of classification or regression, default = "classification"

    objective: objective function (metric/loss) to evaluate model, default = "regression"

    boosting: boosting method, default = "gbdt"
    support ["gbdt", "rf", "dart", "goss"]

    n_estimators: number of estimators to build, default = 100

    max_depth: max depth of trees built, default = -1
    -1 stands for no limitation

    num_leaves: number of leaf nodes to build, default = 31

    min_data_in_leaf: minimum number of data to generate a leaf node, default = 20

    learning_rate: learning rate of the building process, default = 0.1

    tree_learner: tree learner algorithm, default = "serial"
    support ["serial", "feature", "data", "voting"]

    num_iterations: number of iterations for the algorithm, default = 100

    seed: random seed, default = 1
    """

    def __init__(
        self,
        task_type: str = "classification",
        objective: str = "regression",
        boosting: str = "gbdt",
        max_depth: int = -1,
        num_leaves: int = 31,
        min_data_in_leaf: int = 20,
        learning_rate: float = 0.1,
        tree_learner: str = "serial",
        num_iterations: int = 100,
        min_gain_to_split: float = 0.0,
        early_stopping_round: int = 0,
        max_bin: int = 255,
        feature_fraction: float = 1.0,
        seed: int = None,
    ) -> None:
        self.task_type = task_type
        self.objective = objective
        self.boosting = boosting
        self.max_depth = max_depth
        self.num_leaves = num_leaves
        self.min_data_in_leaf = min_data_in_leaf
        self.learning_rate = learning_rate
        self.tree_learner = tree_learner
        self.num_iterations = num_iterations
        self.min_data_in_leaf = min_data_in_leaf
        self.min_gain_to_split = min_gain_to_split
        self.early_stopping_round = early_stopping_round
        self.max_bin = max_bin
        self.feature_fraction = feature_fraction
        self.seed = seed

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, pd.Series, np.ndarray],
        eval_set: List,
    ) -> LightGBM_Base:
        # get binary classification and multiclass classification
        if self.task_type == "classification":
            if len(pd.unique(y)) == 2:
                self.task_type = "binary"
            else:
                self.task_type = "multiclass"

        # check categorical hyperparameters in range
        # objective
        if (
            self.task_type == "binary"
            and self.objective not in LIGHTGBM_BINARY_CLASSIFICATION
        ):
            raise AttributeError(
                "For {} tasks, only accept objects: {}, get {}.".format(
                    self.task_type,
                    ", ".join(LIGHTGBM_BINARY_CLASSIFICATION),
                    self.objective,
                )
            )
        elif (
            self.task_type == "multiclass"
            and self.objective not in LIGHTGBM_MULTICLASS_CLASSIFICATION
        ):
            raise AttributeError(
                "For {} tasks, only accept objects: {}, get {}.".format(
                    self.task_type,
                    ", ".join(LIGHTGBM_MULTICLASS_CLASSIFICATION),
                    self.objective,
                )
            )
        elif (
            self.task_type == "regression" and self.objective not in LIGHTGBM_REGRESSION
        ):
            raise AttributeError(
                "For {} tasks, only accept objects: {}, get {}.".format(
                    self.task_type, ", ".join(LIGHTGBM_REGRESSION), self.objective
                )
            )

        # boosting
        if self.boosting not in LIGHTGBM_BOOSTING:
            raise AttributeError(
                "Expect one of {} boosting method, get {}.".format(
                    ", ".join(LIGHTGBM_BOOSTING), self.boosting
                )
            )

        # tree learner
        if self.tree_learner not in LIGHTGBM_TREE_LEARNER:
            raise AttributeError(
                "Expect one of {} tree learner, get {}.".format(
                    ", ".join(LIGHTGBM_TREE_LEARNER), self.tree_learner
                )
            )

        # model
        if self.task_type in ["binary", "multiclass"]:
            self.model = LGBMClassifier(
                objective=self.objective,
                boosting_type=self.boosting,
                max_depth=self.max_depth,
                num_leaves=self.num_leaves,
                min_data_in_leaf=self.min_data_in_leaf,
                learning_rate=self.learning_rate,
                tree_learner=self.tree_learner,
                num_iterations=self.num_iterations,
                min_split_gain=self.min_gain_to_split,
                early_stopping_rounds=self.early_stopping_round,
                max_bin=self.max_bin,
                feature_fraction=self.feature_fraction,
                verbosity=0,
                n_jobs=1,
            )
        elif self.task_type == "regression":
            self.model = LGBMRegressor(
                objective=self.objective,
                boosting_type=self.boosting,
                max_depth=self.max_depth,
                num_leaves=self.num_leaves,
                min_data_in_leaf=self.min_data_in_leaf,
                learning_rate=self.learning_rate,
                tree_learner=self.tree_learner,
                num_iterations=self.num_iterations,
                min_split_gain=self.min_gain_to_split,
                early_stopping_rounds=self.early_stopping_round,
                max_bin=self.max_bin,
                feature_fraction=self.feature_fraction,
                verbosity=0,
                n_jobs=1,
            )

        try:
            self.model.fit(X, y, eval_set=eval_set)
        except Exception as e:
            raise e

        self._fitted = True

        return self

    def predict(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        return self.model.predict(X)

    def predict_proba(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        return self.model.predict_proba(X)


class LightGBM_Classifier(LightGBM_Base, BaseModel):

    """
    LightGBM Classification Wrapper

    Parameters
    ----------
    objective: objective function (metric/loss) to evaluate model, default = "multiclass"

    boosting: boosting method, default = "gbdt"
    support ["gbdt", "rf", "dart", "goss"]

    n_estimators: number of estimators to build, default = 100

    max_depth: max depth of trees built, default = -1
    -1 stands for no limitation

    num_leaves: number of leaf nodes to build, default = 31

    min_data_in_leaf: minimum number of data to generate a leaf node, default = 20

    learning_rate: learning rate of the building process, default = 0.1

    tree_learner: tree learner algorithm, default = "serial"
    support ["serial", "feature", "data", "voting"]

    num_iterations: number of iterations for the algorithm, default = 100

    seed: random seed, default = 1
    """

    def __init__(
        self,
        objective: str = "multiclass",
        boosting: str = "gbdt",
        max_depth: int = -1,
        num_leaves: int = 31,
        min_data_in_leaf: int = 20,
        learning_rate: float = 0.1,
        tree_learner: str = "serial",
        num_iterations: int = 100,
        min_gain_to_split: float = 0.0,
        early_stopping_round: int = 0,
        max_bin: int = 255,
        feature_fraction: float = 1.0,
        seed: int = None,
    ) -> None:
        self.objective = objective
        self.boosting = boosting
        self.max_depth = max_depth
        self.num_leaves = num_leaves
        self.min_data_in_leaf = min_data_in_leaf
        self.learning_rate = learning_rate
        self.tree_learner = tree_learner
        self.num_iterations = num_iterations
        self.min_data_in_leaf = min_data_in_leaf
        self.min_gain_to_split = min_gain_to_split
        self.early_stopping_round = early_stopping_round
        self.max_bin = max_bin
        self.feature_fraction = feature_fraction
        self.seed = seed

        self._fitted = False

        super().__init__(
            task_type="classification",
            objective=self.objective,
            boosting=self.boosting,
            max_depth=self.max_depth,
            num_leaves=self.num_leaves,
            min_data_in_leaf=self.min_data_in_leaf,
            learning_rate=self.learning_rate,
            tree_learner=self.tree_learner,
            num_iterations=self.num_iterations,
            min_gain_to_split=self.min_gain_to_split,
            early_stopping_round=self.early_stopping_round,
            max_bin=self.max_bin,
            feature_fraction=self.feature_fraction,
            seed=self.seed,
        )

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, pd.Series, np.ndarray],
    ) -> LightGBM_Classifier:
        super(LightGBM_Classifier, self).fit(X, y, eval_set=(X, y))

        self._fitted = True

        return self

    def predict(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        return super(LightGBM_Classifier, self).predict(X)

    def predict_proba(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        return super(LightGBM_Classifier, self).predict_proba(X)


class LightGBM_Regressor(LightGBM_Base, BaseModel):

    """
    LightGBM Regression Wrapper

    Parameters
    ----------
    objective: objective function (metric/loss) to evaluate model, default = "regression"

    boosting: boosting method, default = "gbdt"
    support ["gbdt", "rf", "dart", "goss"]

    n_estimators: number of estimators to build, default = 100

    max_depth: max depth of trees built, default = -1
    -1 stands for no limitation

    num_leaves: number of leaf nodes to build, default = 31

    min_data_in_leaf: minimum number of data to generate a leaf node, default = 20

    learning_rate: learning rate of the building process, default = 0.1

    tree_learner: tree learner algorithm, default = "serial"
    support ["serial", "feature", "data", "voting"]

    num_iterations: number of iterations for the algorithm, default = 100

    seed: random seed, default = 1
    """

    def __init__(
        self,
        objective: str = "regression",
        boosting: str = "gbdt",
        max_depth: int = -1,
        num_leaves: int = 31,
        min_data_in_leaf: int = 20,
        learning_rate: float = 0.1,
        tree_learner: str = "serial",
        num_iterations: int = 100,
        min_gain_to_split: float = 0.0,
        early_stopping_round: int = 0,
        max_bin: int = 255,
        feature_fraction: float = 1.0,
        seed: int = None,
    ) -> None:
        self.objective = objective
        self.boosting = boosting
        self.max_depth = max_depth
        self.num_leaves = num_leaves
        self.min_data_in_leaf = min_data_in_leaf
        self.learning_rate = learning_rate
        self.tree_learner = tree_learner
        self.num_iterations = num_iterations
        self.min_data_in_leaf = min_data_in_leaf
        self.min_gain_to_split = min_gain_to_split
        self.early_stopping_round = early_stopping_round
        self.max_bin = max_bin
        self.feature_fraction = feature_fraction
        self.seed = seed

        self._fitted = False

        super().__init__(
            task_type="regression",
            objective=self.objective,
            boosting=self.boosting,
            max_depth=self.max_depth,
            num_leaves=self.num_leaves,
            min_data_in_leaf=self.min_data_in_leaf,
            learning_rate=self.learning_rate,
            tree_learner=self.tree_learner,
            num_iterations=self.num_iterations,
            min_gain_to_split=self.min_gain_to_split,
            early_stopping_round=self.early_stopping_round,
            max_bin=self.max_bin,
            feature_fraction=self.feature_fraction,
            seed=self.seed,
        )

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, pd.Series, np.ndarray],
    ) -> LightGBM_Regressor:
        super(LightGBM_Regressor, self).fit(X, y, eval_set=(X, y))

        self._fitted = True

        return self

    def predict(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        return super(LightGBM_Regressor, self).predict(X)

    def predict_proba(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        raise NotImplementedError("predict_proba is not implemented for regression.")
