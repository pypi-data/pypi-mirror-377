import numpy as np
from sklearn.metrics import pairwise_distances
import pandas as pd


class Base:
    def __init__(self):
        self.X_train = None
        self.model = None

    def __get_X_train(self):
        if self.X_train is None:
            raise ValueError(
                'Your X_train is not fitted correctly! Please fit your model with correct X_train first!')
        return self.X_train

    def _input_validation_and_preprocessing(self, X):
        # --- VALIDASI DAN PRE-PROCESSING INPUT DATA ---
        # Ini adalah bagian terpenting untuk memperbaiki bug.
        # Pastikan data input adalah array numpy yang valid.
        X_processed = None
        try:
            # Mengubah X menjadi numpy array jika belum.
            # Menggunakan `float32` untuk mencegah error ini:
            # ValueError: Buffer dtype mismatch, expected 'float' but got 'double'
            if isinstance(X, pd.DataFrame):
                X_processed = X.values.astype(np.float32)
            else:
                X_processed = np.asarray(X, dtype=np.float32)

            # Menangani kemungkinan adanya nilai NaN (Not a Number) atau Inf.
            if not np.isfinite(X_processed).all():
                print(
                    "Warning: Input data contains NaN or Inf values. These will be removed.")
                # Menghapus baris yang mengandung nilai non-numerik.
                # Ini mungkin bukan perilaku yang Anda inginkan, jadi sesuaikan jika perlu.
                X_processed = X_processed[np.isfinite(X_processed).all(axis=1)]
                if X_processed.shape[0] == 0:
                    raise ValueError(
                        "Input data is empty after removing non-finite values.")

        except (ValueError, TypeError) as e:
            # Memberikan pesan kesalahan yang lebih jelas jika konversi gagal.
            raise ValueError(
                f"Error during input data validation in KMeansNER.fit: {e}")

        return X_processed

    def _predict_cluster_labels(self, X_test):
        """
        Predicts cluster labels for new data (X_test) based on a fitted scikit-learn
        clustering model.

        This function simulates a 'predict' method for clustering algorithms that
        do not inherently have one (e.g., DBSCAN, AgglomerativeClustering, SpectralClustering, OPTICS).
        It works by calculating the centroid of each cluster from the training data
        and then assigning each point in X_test to the closest cluster centroid.

        Args:
            model: A fitted scikit-learn clustering model (e.g., KMeans, DBSCAN, etc.).
                The model must have a 'labels_' attribute after fitting.
            X_train: The original training data (numpy array or similar) that was
                    used to fit the clustering model. This is necessary to
                    determine the centroids of the clusters.
            X_test: The new data (numpy array or similar) for which to predict
                    cluster labels.

        Returns:
            A numpy array of predicted cluster labels for X_test.
            Points that are considered noise in the training data (label -1)
            will not contribute to centroid calculation. New points will be
            assigned to the closest non-noise cluster.
        """
        model = self.model
        X_train = self.__get_X_train()

        # Ensure the model has been fitted and has the 'labels_' attribute
        if not hasattr(model, 'labels_'):
            raise AttributeError("The provided model does not have a 'labels_' attribute. "
                                 "Please ensure the model has been fitted by calling model.fit(X_train).")

        train_labels = model.labels_
        unique_labels = np.unique(train_labels)
        # Exclude the noise label (-1) from centroid calculation if present in the training labels
        cluster_labels_to_consider = [
            label for label in unique_labels if label != -1]

        # Handle cases where no valid clusters are found (e.g., all points are noise)
        if not cluster_labels_to_consider:
            print("Warning: No valid clusters found in training data (all points might be noise or "
                  "model failed to form clusters). Assigning all test points to a default label (-1).")
            return np.full(X_test.shape[0], -1)
        # Calculate centroids for each cluster based on X_train
        cluster_centroids = {}
        for label in cluster_labels_to_consider:
            # Get all training points that belong to the current cluster
            cluster_points = X_train[train_labels == label]
            if cluster_points.shape[0] > 0:
                # Calculate the mean of these points to get the centroid
                cluster_centroids[label] = np.mean(cluster_points, axis=0)
            else:
                # This case should ideally not happen if labels are valid, but good for robustness
                print(
                    f"Warning: Cluster {label} has no points in X_train after filtering. Skipping centroid calculation.")

        # If, after filtering, no centroids could be calculated (e.g., all clusters were empty or noise)
        if not cluster_centroids:
            print("Warning: No centroids could be calculated from the training data. Assigning all test points to -1.")
            return np.full(X_test.shape[0], -1)

        # Prepare centroids for distance calculation:
        # 1. Get the sorted list of cluster labels (important for consistent indexing)
        sorted_labels = sorted(cluster_centroids.keys())
        # 2. Create a NumPy array of centroids in the same order as sorted_labels
        centroids_array = np.array([cluster_centroids[label]
                                   for label in sorted_labels])

        # Calculate the Euclidean distance from each point in X_test to every centroid
        # The result is a matrix where distances[i, j] is the distance from X_test[i] to centroids_array[j]
        distances = pairwise_distances(
            X_test, centroids_array, metric='euclidean')

        # For each point in X_test, find the index of the closest centroid
        # np.argmin returns the index along the specified axis (axis=1 for rows)
        predicted_indices = np.argmin(distances, axis=1)

        # Map these indices back to the actual cluster labels using the sorted_labels list
        predicted_labels = np.array([sorted_labels[idx]
                                    for idx in predicted_indices])

        return predicted_labels
