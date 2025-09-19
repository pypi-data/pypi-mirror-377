"""
File: _sklearn.py
Author: Panyi Dong
GitHub: https://github.com/PanyiDong/
Mathematics Department, University of Illinois at Urbana-Champaign (UIUC)

Project: InsurAutoML
Latest Version: 0.2.5
Relative Path: /InsurAutoML/feature_selection/sklearn.py
File: _sklearn.py
Author: Panyi Dong (panyid2@illinois.edu)

-----
Last Modified: Thursday, 1st June 2023 9:27:54 am
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

from typing import Union
import scipy
import numpy as np
import pandas as pd
import sklearn.feature_selection
import sklearn.decomposition
import sklearn.cluster
import sklearn.kernel_approximation
import sklearn.preprocessing
import sklearn.ensemble
import warnings

from ..utils.base import is_none
from .base import BaseFeatureSelection

##########################################################################
# sklearn replacement of feature selection


class densifier(BaseFeatureSelection):
    def __init__(
        self,
    ) -> None:
        super().__init__()
        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> densifier:
        self._fitted = True
        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        from scipy import sparse

        if sparse.issparse(X):
            return X.todense().getA()
        else:
            return X


class extra_trees_preproc_for_classification(BaseFeatureSelection):
    def __init__(
        self,
        n_estimators: int = 5,
        criterion: str = "entropy",
        min_samples_leaf: int = 5,
        min_samples_split: int = 5,
        max_features: float = 0.5,
        bootstrap: bool = False,
        max_leaf_nodes: int = None,
        max_depth: int = None,
        min_weight_fraction_leaf: float = 0.0,
        min_impurity_decrease: float = 0.0,
    ) -> None:
        self.n_estimators = int(n_estimators)
        self.criterion = criterion
        self.min_samples_leaf = int(min_samples_leaf)
        self.min_samples_split = int(min_samples_split)
        self.max_features = max_features
        self.bootstrap = bootstrap
        self.max_leaf_nodes = None if is_none(max_leaf_nodes) else int(max_leaf_nodes)
        self.max_depth = None if is_none(max_depth) else int(max_depth)
        self.min_weight_fraction_leaf = float(min_weight_fraction_leaf)
        self.min_impurity_decrease = float(min_impurity_decrease)

        super().__init__()
        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> extra_trees_preproc_for_classification:
        from sklearn.ensemble import ExtraTreesClassifier
        from sklearn.feature_selection import SelectFromModel

        estimator = ExtraTreesClassifier(
            n_estimators=self.n_estimators,
            criterion=self.criterion,
            min_samples_leaf=self.min_samples_leaf,
            min_samples_split=self.min_samples_split,
            max_features=max(1, int(X.shape[1] * self.max_features)),
            bootstrap=self.bootstrap,
            max_leaf_nodes=self.max_leaf_nodes,
            max_depth=self.max_depth,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            min_impurity_decrease=self.min_impurity_decrease,
        )
        estimator.fit(X, y)
        self.selector = SelectFromModel(
            estimator,
            threshold="mean",
            prefit=True,
        )

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")
        return self.selector.transform(X)


class extra_trees_preproc_for_regression(BaseFeatureSelection):
    def __init__(
        self,
        n_estimators: int = 5,
        criterion: str = "squared_error",
        min_samples_leaf: int = 5,
        min_samples_split: int = 5,
        max_features: float = 0.5,
        bootstrap: bool = False,
        max_leaf_nodes: int = None,
        max_depth: int = None,
        min_weight_fraction_leaf: float = 0.0,
    ) -> None:
        self.n_estimators = int(n_estimators)
        self.criterion = criterion
        self.min_samples_leaf = int(min_samples_leaf)
        self.min_samples_split = int(min_samples_split)
        self.max_features = max_features
        self.bootstrap = bootstrap
        self.max_leaf_nodes = None if is_none(max_leaf_nodes) else int(max_leaf_nodes)
        self.max_depth = None if is_none(max_depth) else int(max_depth)
        self.min_weight_fraction_leaf = float(min_weight_fraction_leaf)

        super().__init__()
        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> extra_trees_preproc_for_regression:
        from sklearn.ensemble import ExtraTreesRegressor
        from sklearn.feature_selection import SelectFromModel

        estimator = ExtraTreesRegressor(
            n_estimators=self.n_estimators,
            criterion=self.criterion,
            min_samples_leaf=self.min_samples_leaf,
            min_samples_split=self.min_samples_split,
            max_features=max(
                1, int(np.log(X.shape[1] + 1) * self.max_features)
            ),  # make sure it's at least 1
            bootstrap=self.bootstrap,
            max_leaf_nodes=self.max_leaf_nodes,
            max_depth=self.max_depth,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
        )
        estimator.fit(X, y)
        self.selector = SelectFromModel(
            estimator,
            threshold="mean",
            prefit=True,
        )

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")
        return self.selector.transform(X)


class fast_ica(sklearn.decomposition.FastICA, BaseFeatureSelection):
    def __init__(
        self,
        algorithm: str = "parallel",
        whiten: bool = False,
        fun: str = "logcosh",
        n_components: int = 5,
    ) -> None:
        self.algorithm = algorithm
        self.whiten = whiten
        self.fun = fun
        self.n_components = None if is_none(n_components) else int(n_components)

        super(fast_ica, self).__init__(
            algorithm=self.algorithm,
            whiten=self.whiten,
            fun=self.fun,
            n_components=self.n_components,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> fast_ica:
        super(fast_ica, self).fit(X)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")
        return super(fast_ica, self).transform(X)


class feature_agglomeration(sklearn.cluster.FeatureAgglomeration, BaseFeatureSelection):
    def __init__(
        self,
        n_clusters: int = 5,
        affinity: str = "euclidean",
        linkage: str = "ward",
        pooling_func: str = "mean",
    ) -> None:
        self.n_clusters = int(n_clusters)
        self.affinity = affinity
        self.linkage = linkage
        self.pooling_func = pooling_func

        self.pooling_func_dict = {
            "mean": np.mean,
            "median": np.median,
            "max": np.max,
        }
        super().__init__()
        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> feature_agglomeration:
        if not callable(self.pooling_func):
            self.pooling_func = self.pooling_func_dict[self.pooling_func]

        super(feature_agglomeration, self).__init__(
            n_clusters=min(self.n_clusters, X.shape[1]),
            affinity=self.affinity,
            linkage=self.linkage,
            pooling_func=self.pooling_func,
        )
        super(feature_agglomeration, self).fit(X)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")
        return super(feature_agglomeration, self).transform(X)


class kernel_pca(sklearn.decomposition.KernelPCA, BaseFeatureSelection):
    def __init__(
        self,
        n_components: int = 5,
        kernel: str = "rbf",
        gamma: float = 0.1,
        degree: int = 3,
        coef0: float = 0.5,
    ) -> None:
        self.n_components = None if is_none(n_components) else int(n_components)
        self.kernel = kernel
        self.gamma = None if is_none(gamma) else float(gamma)
        self.degree = int(degree)
        self.coef0 = float(coef0)

        super(kernel_pca, self).__init__(
            n_components=self.n_components,
            kernel=self.kernel,
            gamma=self.gamma,
            degree=self.degree,
            coef0=self.coef0,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> kernel_pca:
        if scipy.sparse.issparse(X):
            X = X.stype(np.float64)

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            super(kernel_pca, self).fit(X)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            return super(kernel_pca, self).transform(X)


class kitchen_sinks(sklearn.kernel_approximation.RBFSampler, BaseFeatureSelection):
    def __init__(
        self,
        gamma: float = 0.1,
        n_components: int = 50,
    ) -> None:
        self.gamma = float(gamma)
        self.n_components = int(n_components)

        super(kitchen_sinks, self).__init__(
            gamma=self.gamma,
            n_components=self.n_components,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> kitchen_sinks:
        super(kitchen_sinks, self).fit(X)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        return super(kitchen_sinks, self).transform(X)


class liblinear_svc_preprocessor(BaseFeatureSelection):
    def __init__(
        self,
        penalty: str = "l1",
        loss: str = "squared_hinge",
        dual: bool = False,
        tol: float = 0.0001,
        C: float = 1.0,
        multi_class: str = "ovr",
        fit_intercept: bool = True,
        intercept_scaling: int = 1,
    ) -> None:
        self.penalty = penalty
        self.loss = loss
        self.dual = dual
        self.tol = float(tol)
        self.C = float(C)
        self.multi_class = multi_class
        self.fit_intercept = fit_intercept
        self.intercept_scaling = float(intercept_scaling)

        super().__init__()
        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> liblinear_svc_preprocessor:
        from sklearn.svm import LinearSVC
        from sklearn.feature_selection import SelectFromModel

        estimator = LinearSVC(
            penalty=self.penalty,
            loss=self.loss,
            dual=self.dual,
            tol=self.tol,
            C=self.C,
            multi_class=self.multi_class,
            fit_intercept=self.fit_intercept,
            intercept_scaling=self.intercept_scaling,
        )
        estimator.fit(X, y)

        self.selector = SelectFromModel(estimator, threshold="mean", prefit=True)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        return self.selector.transform(X)


class nystroem_sampler(sklearn.kernel_approximation.Nystroem, BaseFeatureSelection):
    def __init__(
        self,
        kernel: str = "rbf",
        n_components: int = 50,
        gamma: float = 0.1,
        degree: int = 3,
        coef0: float = 0.5,
    ) -> None:
        self.kernel = kernel
        self.n_components = int(n_components)
        self.gamma = None if is_none(gamma) else float(gamma)
        self.degree = int(degree)
        self.coef0 = float(coef0)

        super(nystroem_sampler, self).__init__(
            kernel=self.kernel,
            n_components=self.n_components,
            gamma=self.gamma,
            degree=self.degree,
            coef0=self.coef0,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> nystroem_sampler:
        # for kernel = "chi2", make sure non-negative values are passed
        if self.kernel == "chi2":
            if scipy.sparse.issparse(X):
                X.data[X.data < 0] = 0
            else:
                X[X < 0] = 0

        super(nystroem_sampler, self).fit(X)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        # for kernel = "chi2", make sure non-negative values are passed
        if self.kernel == "chi2":
            if scipy.sparse.issparse(X):
                X.data[X.data < 0] = 0
            else:
                X[X < 0] = 0

        return super(nystroem_sampler, self).transform(X)


class pca(sklearn.decomposition.PCA, BaseFeatureSelection):
    def __init__(
        self,
        keep_variance: float = 0.5,
        whiten: bool = True,
    ) -> None:
        self.keep_variance = float(keep_variance)
        self.with_whiten = whiten

        super(pca, self).__init__(
            n_components=self.keep_variance,
            whiten=self.with_whiten,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> pca:
        super(pca, self).fit(X)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        return super(pca, self).transform(X)


class polynomial(sklearn.preprocessing.PolynomialFeatures, BaseFeatureSelection):
    def __init__(
        self,
        degree: int = 3,
        interaction_only: bool = False,
        include_bias: bool = True,
    ) -> None:
        self.degree = int(degree)
        self.interaction_only = interaction_only
        self.include_bias = include_bias

        super(polynomial, self).__init__(
            degree=self.degree,
            interaction_only=self.interaction_only,
            include_bias=self.include_bias,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> polynomial:
        super(polynomial, self).fit(X, y)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        return super(polynomial, self).transform(X)


class random_trees_embedding(
    sklearn.ensemble.RandomTreesEmbedding, BaseFeatureSelection
):
    def __init__(
        self,
        n_estimators: int = 5,
        max_depth: int = 3,
        min_samples_split: int = 5,
        min_samples_leaf: int = 5,
        min_weight_fraction_leaf: float = 0.0,
        max_leaf_nodes: int = None,
        bootstrap: bool = True,
    ) -> None:
        self.n_estimators = int(n_estimators)
        self.max_depth = None if is_none(max_depth) else int(max_depth)
        self.min_samples_split = int(min_samples_split)
        self.min_samples_leaf = int(min_samples_leaf)
        self.min_weight_fraction_leaf = float(min_weight_fraction_leaf)
        self.max_leaf_nodes = None if is_none(max_leaf_nodes) else int(max_leaf_nodes)
        self.bootstrap = bootstrap

        super(random_trees_embedding, self).__init__(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            max_leaf_nodes=self.max_leaf_nodes,
            # bootstrap=self.bootstrap,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> random_trees_embedding:
        super(random_trees_embedding, self).fit(X, y)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        return super().transform(X)


class select_percentile_classification(
    sklearn.feature_selection.SelectPercentile, BaseFeatureSelection
):
    def __init__(
        self,
        percentile: int = 90,
        score_func: str = "chi2",
    ) -> None:
        self.percentile = int(percentile)
        if score_func == "chi2":
            self.score_func = sklearn.feature_selection.chi2
        elif score_func == "f_classif":
            self.score_func = sklearn.feature_selection.f_classif
        elif score_func == "mutual_info":
            self.score_func = sklearn.feature_selection.mutual_info_classif
        else:
            raise ValueError(
                "score_func must be one of 'chi2', 'f_classif', 'mutual_info', but got {}".format(
                    score_func
                )
            )

        super(select_percentile_classification, self).__init__(
            percentile=self.percentile,
            score_func=self.score_func,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> select_percentile_classification:
        # for score_func = "chi2", make sure non-negative values are passed
        if self.score_func == sklearn.feature_selection.chi2:
            if scipy.sparse.issparse(X):
                X.data[X.data < 0] = 0
            else:
                X[X < 0] = 0

        super(select_percentile_classification, self).fit(X, y)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        # for score_func = "chi2", make sure non-negative values are passed
        if self.score_func == sklearn.feature_selection.chi2:
            if scipy.sparse.issparse(X):
                X.data[X.data < 0] = 0
            else:
                X[X < 0] = 0

        return super(select_percentile_classification, self).transform(X)


class select_percentile_regression(
    sklearn.feature_selection.SelectPercentile, BaseFeatureSelection
):
    def __init__(
        self,
        percentile: int = 90,
        score_func: str = "f_regression",
    ) -> None:
        self.percentile = int(percentile)
        if score_func == "f_regression":
            self.score_func = sklearn.feature_selection.f_regression
        elif score_func == "mutual_info":
            self.score_func = sklearn.feature_selection.mutual_info_regression
        else:
            raise ValueError(
                "score_func must be one of 'f_regression', 'mutual_info', but got {}".format(
                    score_func
                )
            )

        super(select_percentile_regression, self).__init__(
            percentile=self.percentile,
            score_func=self.score_func,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> select_percentile_regression:
        super(select_percentile_regression, self).fit(X, y)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        return super(select_percentile_regression, self).transform(X)


class select_rates_classification(
    sklearn.feature_selection.GenericUnivariateSelect, BaseFeatureSelection
):
    def __init__(
        self,
        alpha: float = 0.3,
        score_func: str = "chi2",
        mode: str = "fpr",
    ) -> None:
        self.alpha = float(alpha)
        self.mode = mode
        if score_func == "chi2":
            self.score_func = sklearn.feature_selection.chi2
        elif score_func == "f_classif":
            self.score_func = sklearn.feature_selection.f_classif
        elif score_func == "mutual_info":
            self.score_func = sklearn.feature_selection.mutual_info_classif
            self.mode = "percentile"
        else:
            raise ValueError(
                "score_func must be one of 'chi2', 'f_classif', 'mutual_info', but got {}".format(
                    score_func
                )
            )

        super(select_rates_classification, self).__init__(
            param=self.alpha,
            score_func=self.score_func,
            mode=self.mode,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> select_rates_classification:
        # for score_func = "chi2", make sure non-negative values are passed
        if self.score_func == sklearn.feature_selection.chi2:
            if scipy.sparse.issparse(X):
                X.data[X.data < 0] = 0
            else:
                X[X < 0] = 0

        super(select_rates_classification, self).fit(X, y)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        # for score_func = "chi2", make sure non-negative values are passed
        if self.score_func == sklearn.feature_selection.chi2:
            if scipy.sparse.issparse(X):
                X.data[X.data < 0] = 0
            else:
                X[X < 0] = 0

        return super(select_rates_classification, self).transform(X)


class select_rates_regression(
    sklearn.feature_selection.GenericUnivariateSelect, BaseFeatureSelection
):
    def __init__(
        self,
        alpha: float = 0.3,
        score_func: str = "f_regression",
        mode: str = "fpr",
    ) -> None:
        self.alpha = float(alpha)
        self.mode = mode
        if score_func == "f_regression":
            self.score_func = sklearn.feature_selection.f_regression
        elif score_func == "mutual_info":
            self.score_func = sklearn.feature_selection.mutual_info_regression
            self.mode = "percentile"
        else:
            raise ValueError(
                "score_func must be one of 'f_regression', 'mutual_info', but got {}".format(
                    score_func
                )
            )

        super(select_rates_regression, self).__init__(
            param=self.alpha,
            score_func=self.score_func,
            mode=self.mode,
        )

        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> select_rates_regression:
        super(select_rates_regression, self).fit(X, y)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        return super(select_rates_regression, self).transform(X)


class truncatedSVD(sklearn.decomposition.TruncatedSVD, BaseFeatureSelection):
    def __init__(
        self,
        target_dim: int = 5,
    ):
        self.target_dim = int(target_dim)

        super().__init__()
        self._fitted = False

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray] = None,
    ) -> truncatedSVD:
        super(truncatedSVD, self).__init__(
            n_components=min(self.target_dim, X.shape[1] - 1),
            algorithm="randomized",
        )

        super(truncatedSVD, self).fit(X)

        self._fitted = True

        return self

    def transform(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        if not self._fitted:
            raise NotImplementedError("The model has not been fitted yet!")

        return super(truncatedSVD, self).transform(X)
