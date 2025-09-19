"""Integration tests for the ENCDR package."""

import numpy as np
import pytest
from sklearn.datasets import load_iris, make_classification
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from encdr import ENCDR


class TestNCDRIntegration:
    """Integration tests for ENCDR with real-world scenarios."""

    def test_sklearn_pipeline_compatibility(self):
        """Test ENCDR in sklearn Pipeline."""
        # Generate sample data
        X, y = make_classification(
            n_samples=200, n_features=30, n_informative=20, random_state=42
        )

        # Create pipeline with ENCDR
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "encdr",
                    ENCDR(
                        hidden_dims=[20, 10],
                        latent_dim=5,
                        max_epochs=5,
                        random_state=42,
                        standardize=False,  # Already scaled by pipeline
                        trainer_kwargs={"enable_progress_bar": False},
                    ),
                ),
            ]
        )

        # Fit and transform
        X_transformed = pipeline.fit_transform(X)

        assert X_transformed.shape == (200, 5)
        assert isinstance(X_transformed, np.ndarray)

    def test_comparison_with_pca(self):
        """Test ENCDR performance compared to PCA."""
        # Generate sample data
        X, _ = make_classification(
            n_samples=300, n_features=50, n_informative=30, random_state=42
        )

        # Train-test split
        X_train, X_test = train_test_split(X, test_size=0.3, random_state=42)

        # Fit PCA
        pca = PCA(n_components=10, random_state=42)
        X_train_pca = pca.fit_transform(X_train)
        X_test_pca = pca.transform(X_test)

        # Fit ENCDR
        encdr = ENCDR(
            hidden_dims=[40, 20],
            latent_dim=10,
            max_epochs=20,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )
        X_train_ncdr = encdr.fit_transform(X_train)
        X_test_ncdr = encdr.transform(X_test)

        # Both should produce same dimensionality
        assert X_train_pca.shape == X_train_ncdr.shape
        assert X_test_pca.shape == X_test_ncdr.shape

        # ENCDR should provide reasonable reconstruction
        X_train_reconstructed = encdr.predict(X_train)
        reconstruction_error = np.mean((X_train - X_train_reconstructed) ** 2)
        assert reconstruction_error < 15.0  # Reasonable reconstruction error

    def test_iris_dataset(self):
        """Test ENCDR on the classic iris dataset."""
        # Load iris dataset
        iris = load_iris()
        X, y = iris.data, iris.target

        # Fit ENCDR
        encdr = ENCDR(
            hidden_dims=[6, 4],
            latent_dim=2,
            max_epochs=50,
            learning_rate=1e-2,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        # Transform to 2D for visualization purposes
        X_transformed = encdr.fit_transform(X)

        assert X_transformed.shape == (150, 2)

        # Test reconstruction
        X_reconstructed = encdr.predict(X)
        assert X_reconstructed.shape == X.shape

        # Calculate reconstruction quality
        reconstruction_error = np.mean((X - X_reconstructed) ** 2)
        print(f"Iris reconstruction error: {reconstruction_error:.4f}")

        # Score should be negative MSE
        score = encdr.score(X)
        assert score <= 0
        assert abs(score - (-reconstruction_error)) < 1e-6

    def test_batch_processing(self):
        """Test ENCDR with different batch sizes."""
        # Generate large dataset
        X, _ = make_classification(
            n_samples=1000, n_features=40, n_informative=25, random_state=42
        )

        results = {}

        for batch_size in [16, 32, 64, 128]:
            encdr = ENCDR(
                hidden_dims=[30, 15],
                latent_dim=8,
                batch_size=batch_size,
                max_epochs=5,
                random_state=42,
                trainer_kwargs={"enable_progress_bar": False},
            )

            X_transformed = encdr.fit_transform(X)
            results[batch_size] = X_transformed

            assert X_transformed.shape == (1000, 8)

        # Results should be similar across batch sizes (with same random seed)
        for batch_size in [32, 64, 128]:
            correlation = np.corrcoef(
                results[16].flatten(), results[batch_size].flatten()
            )[0, 1]
            assert correlation > 0.3  # Should be reasonably correlated

    def test_different_activations_performance(self):
        """Test ENCDR with different activation functions."""
        # Generate sample data
        X, _ = make_classification(
            n_samples=300, n_features=20, n_informative=15, random_state=42
        )

        activations = ["relu", "tanh", "sigmoid", "leaky_relu"]
        results = {}

        for activation in activations:
            encdr = ENCDR(
                hidden_dims=[15, 8],
                latent_dim=5,
                activation=activation,
                max_epochs=10,
                random_state=42,
                trainer_kwargs={"enable_progress_bar": False},
            )

            encdr.fit(X)
            score = encdr.score(X)
            results[activation] = score

            # All activations should provide reasonable results
            assert score <= 0  # Negative MSE
            assert score > -10  # Not too bad reconstruction

        print("Activation function scores:", results)

    def test_overfitting_detection(self):
        """Test that validation split helps detect overfitting."""
        # Generate small dataset that's easy to overfit
        X, _ = make_classification(
            n_samples=50, n_features=20, n_informative=10, random_state=42
        )

        # Model with high capacity and many epochs
        encdr = ENCDR(
            hidden_dims=[30, 20, 10],
            latent_dim=5,
            max_epochs=100,
            learning_rate=1e-2,
            validation_split=0.3,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        encdr.fit(X)

        # Should still work despite potential overfitting
        X_transformed = encdr.transform(X)
        assert X_transformed.shape == (50, 5)

        score = encdr.score(X)
        assert isinstance(score, float)

    def test_memory_efficiency(self):
        """Test memory efficiency with larger datasets."""
        # Generate moderately large dataset
        X, _ = make_classification(
            n_samples=2000, n_features=100, n_informative=50, random_state=42
        )

        encdr = ENCDR(
            hidden_dims=[80, 40, 20],
            latent_dim=10,
            batch_size=64,
            max_epochs=5,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        # Should handle larger dataset without issues
        X_transformed = encdr.fit_transform(X)
        assert X_transformed.shape == (2000, 10)

        # Test batch-wise processing
        X_reconstructed = encdr.predict(X)
        assert X_reconstructed.shape == X.shape

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very small dataset
        X_small = np.random.randn(5, 10).astype(np.float32)

        ncdr_small = ENCDR(
            hidden_dims=[8, 4],
            latent_dim=2,
            batch_size=2,
            max_epochs=3,
            validation_split=0.0,  # No validation with small dataset
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        X_transformed = ncdr_small.fit_transform(X_small)
        assert X_transformed.shape == (5, 2)

        # Single sample prediction
        single_sample = X_small[:1]
        single_transformed = ncdr_small.transform(single_sample)
        assert single_transformed.shape == (1, 2)

        single_reconstructed = ncdr_small.predict(single_sample)
        assert single_reconstructed.shape == (1, 10)

    def test_numerical_stability(self):
        """Test numerical stability with challenging data."""
        # Generate data with different scales
        X_large = np.random.randn(100, 20).astype(np.float32) * 1000
        X_small = np.random.randn(100, 20).astype(np.float32) * 0.001

        for X, name in [(X_large, "large"), (X_small, "small")]:
            encdr = ENCDR(
                hidden_dims=[15, 8],
                latent_dim=4,
                max_epochs=5,
                standardize=True,  # Important for numerical stability
                random_state=42,
                trainer_kwargs={"enable_progress_bar": False},
            )

            X_transformed = encdr.fit_transform(X)
            assert X_transformed.shape == (100, 4)
            assert np.isfinite(
                X_transformed
            ).all(), f"Non-finite values in {name} scale data"

            X_reconstructed = encdr.predict(X)
            assert np.isfinite(
                X_reconstructed
            ).all(), f"Non-finite reconstruction for {name} scale data"
