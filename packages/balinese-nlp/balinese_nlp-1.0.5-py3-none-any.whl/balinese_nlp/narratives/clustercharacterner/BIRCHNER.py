from .Base import Base
from sklearn.cluster import Birch


class BIRCHNER(Birch, Base):
    """
    A custom BIRCH class inheriting from sklearn.cluster.Birch and Base.
    Overrides 'fit' to include custom NER logic.
    """

    def __init__(self, threshold=0.5, branching_factor=50, n_clusters=3,
                 compute_labels=True, copy=True):
        Base.__init__(self)
        super().__init__(
            threshold=threshold, branching_factor=branching_factor,
            n_clusters=n_clusters, compute_labels=compute_labels, copy=copy
        )
        self.cluster_model_name = "BIRCH"

    def fit(self, X, y=None):
        X_preprocessed = self._input_validation_and_preprocessing(X)
        # Birch's fit method accepts
        super().fit(X_preprocessed, y=y)
        self.X_train = X
        self.model = self
        return self
