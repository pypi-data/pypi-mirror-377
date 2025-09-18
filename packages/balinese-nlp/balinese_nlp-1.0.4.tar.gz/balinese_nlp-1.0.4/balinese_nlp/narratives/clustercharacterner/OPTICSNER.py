from .Base import Base
from sklearn.cluster import OPTICS
import numpy as np


class OPTICSNER(OPTICS, Base):
    """
    A custom OPTICS class inheriting from sklearn.cluster.OPTICS and Base.
    Overrides 'fit' to include custom NER logic.
    """

    def __init__(self, min_samples=5, max_eps=np.inf, metric='minkowski',
                 p=2, metric_params=None, cluster_method='xi', eps=None,
                 xi=0.05, predecessor_correction=True, min_cluster_size=None,
                 algorithm='auto', leaf_size=30, n_jobs=None):
        Base.__init__(self)
        super().__init__(
            min_samples=min_samples, max_eps=max_eps, metric=metric,
            p=p, metric_params=metric_params, cluster_method=cluster_method,
            eps=eps, xi=xi, predecessor_correction=predecessor_correction,
            min_cluster_size=min_cluster_size, algorithm=algorithm,
            leaf_size=leaf_size, n_jobs=n_jobs
        )
        self.cluster_model_name = "OPTICS"

    def fit(self, X, y=None):
        X_preprocessed = self._input_validation_and_preprocessing(X)
        super().fit(X_preprocessed, y=y)  # Pass only X and y
        self.X_train = X
        self.model = self
        return self
