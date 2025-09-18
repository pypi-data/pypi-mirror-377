from .Base import Base
from hdbscan import HDBSCAN


class HDBSCANNER(HDBSCAN, Base):
    """
    A custom HDBSCAN class inheriting from hdbscan.HDBSCAN and Base.
    Overrides 'fit' to include custom NER logic.
    NOTE: This class requires the 'hdbscan' library to be installed.
    """

    def __init__(self, min_cluster_size=5, min_samples=None, cluster_selection_epsilon=0.0,
                 max_cluster_size=0, metric='euclidean', alpha=1.0, p=None,
                 algorithm='auto', leaf_size=40, memory=None, n_jobs=None,
                 allow_single_cluster=False, store_centers='centroid',
                 approx_min_span_tree=True, gen_min_span_tree=False,
                 core_dist_n_jobs=4, cluster_selection_method='eom',
                 prediction_data=False, gamma=0.0):
        Base.__init__(self)
        super().__init__(
            min_cluster_size=min_cluster_size, min_samples=min_samples,
            cluster_selection_epsilon=cluster_selection_epsilon,
            max_cluster_size=max_cluster_size, metric=metric, alpha=alpha, p=p,
            algorithm=algorithm, leaf_size=leaf_size, memory=memory, n_jobs=n_jobs,
            allow_single_cluster=allow_single_cluster, store_centers=store_centers,
            approx_min_span_tree=approx_min_span_tree, gen_min_span_tree=gen_min_span_tree,
            core_dist_n_jobs=core_dist_n_jobs, cluster_selection_method=cluster_selection_method,
            prediction_data=prediction_data, gamma=gamma
        )
        self.cluster_model_name = "HDBSCAN"

    def fit(self, X, y=None):
        X_preprocessed = self._input_validation_and_preprocessing(X)
        super().fit(X_preprocessed, y=y)  # Pass only X and y
        self.X_train = X
        self.model = self
        return self
