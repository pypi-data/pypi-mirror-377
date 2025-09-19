from .Base import Base
from sklearn.cluster import SpectralClustering


class SpectralClusteringNER(SpectralClustering, Base):
    """
    A custom SpectralClustering class inheriting from sklearn.cluster.SpectralClustering and Base.
    Overrides 'fit' to include custom NER logic.
    """

    def __init__(self, n_clusters=8, *, eigen_solver=None, random_state=None,
                 n_init=10, gamma=1.0, affinity='rbf', n_neighbors=10,
                 eigen_tol=0.0, assign_labels='kmeans', degree=3, coef0=1,
                 kernel_params=None, n_jobs=None):
        Base.__init__(self)
        super().__init__(
            n_clusters=n_clusters, eigen_solver=eigen_solver, random_state=random_state,
            n_init=n_init, gamma=gamma, affinity=affinity, n_neighbors=n_neighbors,
            eigen_tol=eigen_tol, assign_labels=assign_labels, degree=degree,
            coef0=coef0, kernel_params=kernel_params, n_jobs=n_jobs
        )
        self.cluster_model_name = "SpectralClustering"

    def fit(self, X, y=None):
        X_preprocessed = self._input_validation_and_preprocessing(X)
        super().fit(X_preprocessed, y=y)  # Pass only X and y
        self.X_train = X
        self.model = self
        return self
