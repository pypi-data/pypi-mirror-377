import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils.validation import check_array
from .utils import cluster_tri

# import your existing functions here
# from .deltric_core import cluster_tri   # keep your implementation intact

class DelTriC(BaseEstimator, ClusterMixin):
    """
    DelTriC clustering algorithm.
    Compatible with scikit-learn estimator API.
    """

    def __init__(
        self,
        prune_param=-0.8,
        merge_param=0.0,
        min_cluster_size=10,
        dim_reduction="umap",
        back_proj=True,
        anomaly_sensitivity=0.99,
        random_state=42,
    ):
        self.prune_param = prune_param
        self.merge_param = merge_param
        self.min_cluster_size = min_cluster_size
        self.dim_reduction = dim_reduction
        self.back_proj = back_proj
        self.anomaly_sensitivity = anomaly_sensitivity
        self.random_state = random_state

    def fit(self, X, y=None):
        """
        Fit the DelTriC model to data X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data.
        y : Ignored
            Not used, present for API consistency by convention.
        """
        X = check_array(X)

        # keep original DelTriC core untouched
        self.labels_ = cluster_tri(
            X,
            prune_param=self.prune_param,
            merge_param=self.merge_param,
            min_cluster_size=self.min_cluster_size,
            dim_reduction=self.dim_reduction,
            back_proj=self.back_proj,
            anomaly_sensitivity=self.anomaly_sensitivity,
        )

        return self

    def fit_predict(self, X, y=None):
        """
        Fit to data X and return cluster labels.
        """
        self.fit(X, y)
        return self.labels_

    def get_params(self, deep=True):
        return {
            "prune_param": self.prune_param,
            "merge_param": self.merge_param,
            "min_cluster_size": self.min_cluster_size,
            "dim_reduction": self.dim_reduction,
            "back_proj": self.back_proj,
            "anomaly_sensitivity": self.anomaly_sensitivity,
            "random_state": self.random_state,
        }

    def set_params(self, **params):
        for k, v in params.items():
            setattr(self, k, v)
        return self
