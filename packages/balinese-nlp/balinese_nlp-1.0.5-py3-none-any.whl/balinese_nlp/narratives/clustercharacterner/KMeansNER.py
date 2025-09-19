from .Base import Base
from sklearn.cluster import KMeans
from numpy import float32


class KMeansNER(KMeans, Base):
    """
    A custom KMeans class inheriting from sklearn.cluster.KMeans.

    This class overrides the 'fit' method to include custom logic
    (represented here by a placeholder for 'NER logic') while still
    calling the original KMeans fitting process via super().fit().
    """

    def __init__(self, n_clusters=8, *, init='k-means++', n_init=10,
                 max_iter=300, tol=1e-4, verbose=0, random_state=None,
                 copy_x=True, algorithm='lloyd'):
        """
        Initializes the KMeansNER instance.

        All parameters are passed directly to the parent KMeans constructor.
        """
        Base.__init__(self)
        # Call the constructor of the parent KMeans class to set up
        # all the standard KMeans parameters.
        super().__init__(
            n_clusters=n_clusters, init=init, n_init=n_init,
            max_iter=max_iter, tol=tol, verbose=verbose,
            random_state=random_state, copy_x=copy_x, algorithm=algorithm
        )
        # You can add any additional attributes specific to KMeansNER here
        # For example, if your NER logic needs specific configurations:
        self.cluster_model_name = "KMeans"

    def fit(self, X, y=None, sample_weight=None):
        """
        Fits the KMeansNER model to the data.

        This method first executes the original KMeans fitting process
        and then applies custom 'NER logic'.

        Args:
            X (array-like): The input data to cluster.
            y (Ignored): Not used, present for API consistency.
            sample_weight (array-like, optional): Weights for each sample.
                                                 Passed to super().fit().

        Returns:
            self: The fitted estimator.
        """
        print("--- KMeansNER: Starting custom fit method ---")

        # Validasi dan Preprocessing Input Data
        X_preprocessed = self._input_validation_and_preprocessing(X)

        # --- Your custom NER-related logic BEFORE KMeans fitting ---
        # This is where you might preprocess X specifically for NER,
        # or perform some initial analysis.
        # Example: If X were text data, you might do TF-IDF vectorization here
        # or extract specific linguistic features before passing to super().fit().
        # For this example, we'll just print a message.
        #
        # Note: If your pre-processing changes X, make sure to use the
        # transformed X when calling super().fit().

        # Call the original KMeans fit method from the parent class.
        # This performs the actual clustering algorithm.
        super().fit(X_preprocessed, y=y, sample_weight=sample_weight)

        # --- Your custom NER-related logic AFTER KMeans fitting ---
        # After super().fit() completes, the KMeans model will have
        # attributes like 'cluster_centers_' and 'labels_'.
        # You can use these results for your NER task.
        # Example: You might now iterate through the clusters and apply
        # specific NER rules or models based on the characteristics of
        # the documents/data points within each cluster.
        # self.labels_ contains the cluster assignments for X.
        # self.cluster_centers_ contains the coordinates of the cluster centers.
        # --- MODIFIKASI PENTING UNTUK MENGATASI BUG PICKLE ---
        # Setelah super().fit() selesai, `self.cluster_centers_` sudah ada.
        # Konversi tipe data menjadi float32 untuk menghindari masalah saat inference
        # setelah model di-load dari pickle.
        if hasattr(self, 'cluster_centers_'):
            self.cluster_centers_ = self.cluster_centers_.astype(float32)

        # keep the X_train
        self.X_train = X

        # keep the model after fitted with X_train
        self.model = self

        # The fit method should always return 'self' for scikit-learn estimator consistency.
        return self
