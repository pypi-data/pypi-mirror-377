from .Base import Base
from sklearn.cluster import AgglomerativeClustering


class AgglomerativeClusteringNER(AgglomerativeClustering, Base):
    """
    A custom AgglomerativeClustering class inheriting from sklearn.cluster.AgglomerativeClustering and Base.
    Overrides 'fit' to include custom NER logic.
    """

    def __init__(self, n_clusters=2, *, affinity='euclidean', memory=None,
                 connectivity=None, compute_full_tree='auto', linkage='ward',
                 distance_threshold=None, compute_distances=False):
        Base.__init__(self)
        super().__init__(
            n_clusters=n_clusters, affinity=affinity, memory=memory,
            connectivity=connectivity, compute_full_tree=compute_full_tree,
            linkage=linkage, distance_threshold=distance_threshold,
            compute_distances=compute_distances
        )
        self.cluster_model_name = "AgglomerativeClustering"

    def fit(self, X, y=None):
        X_preprocessed = self._input_validation_and_preprocessing(X)
        super().fit(X_preprocessed, y=y)  # Pass only X and y
        self.X_train = X
        self.model = self
        return self
