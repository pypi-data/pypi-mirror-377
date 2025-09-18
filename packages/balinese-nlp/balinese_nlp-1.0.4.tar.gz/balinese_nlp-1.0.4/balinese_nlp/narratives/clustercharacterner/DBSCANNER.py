from .Base import Base
from sklearn.cluster import DBSCAN


class DBSCANNER(DBSCAN, Base):
    """
    A custom DBSCAN class inheriting from sklearn.cluster.DBSCAN and Base.
    Overrides 'fit' to include custom NER logic.
    """

    def __init__(self, eps=0.5, *, min_samples=5, metric='euclidean',
                 metric_params=None, algorithm='auto', leaf_size=30, p=None,
                 n_jobs=None):
        Base.__init__(self)
        super().__init__(
            eps=eps, min_samples=min_samples, metric=metric,
            metric_params=metric_params, algorithm=algorithm,
            leaf_size=leaf_size, p=p, n_jobs=n_jobs
        )
        self.cluster_model_name = "DBSCAN"

    def fit(self, X, y=None, sample_weight=None):
        X_preprocessed = self._input_validation_and_preprocessing(X)
        # DBSCAN's fit method accepts sample_weight
        super().fit(X_preprocessed, y=y, sample_weight=sample_weight)
        self.X_train = X
        self.model = self
        return self
