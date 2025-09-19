"""Tests for the ENCDR class."""

import numpy as np
import pytest
import torch
from sklearn.datasets import make_classification
from sklearn.exceptions import NotFittedError

from encdr import ENCDR


class TestENCDR:
    """Test suite for ENCDR class."""

    def test_encdr_initialization_defaults(self):
        """Test ENCDR initialization with default parameters."""
        encdr = ENCDR()

        assert encdr.hidden_dims == [64, 32]
        assert encdr.latent_dim == 10
        assert encdr.learning_rate == 1e-3
        assert encdr.activation == "relu"
        assert encdr.dropout_rate == 0.0
        assert encdr.weight_decay == 0.0
        assert encdr.batch_size == 32
        assert encdr.max_epochs == 100
        assert encdr.validation_split == 0.2
        assert encdr.standardize == True
        assert encdr.random_state is None
        assert encdr.trainer_kwargs == {}
        assert not encdr.is_fitted_

    def test_encdr_initialization_custom(self):
        """Test ENCDR initialization with custom parameters."""
        encdr = ENCDR(
            hidden_dims=[128, 64, 32],
            latent_dim=20,
            learning_rate=0.01,
            activation="tanh",
            dropout_rate=0.3,
            weight_decay=1e-4,
            batch_size=64,
            max_epochs=50,
            validation_split=0.3,
            standardize=False,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        assert encdr.hidden_dims == [128, 64, 32]
        assert encdr.latent_dim == 20
        assert encdr.learning_rate == 0.01
        assert encdr.activation == "tanh"
        assert encdr.dropout_rate == 0.3
        assert encdr.weight_decay == 1e-4
        assert encdr.batch_size == 64
        assert encdr.max_epochs == 50
        assert encdr.validation_split == 0.3
        assert encdr.standardize == False
        assert encdr.random_state == 42
        assert encdr.trainer_kwargs == {"enable_progress_bar": False}

    def test_fit_basic(self, small_dataset, encdr_params):
        """Test basic fitting functionality."""
        encdr = ENCDR(**encdr_params)

        # Fit should return self
        result = encdr.fit(small_dataset)
        assert result is encdr

        # Check that model is fitted
        assert encdr.is_fitted_
        assert encdr.model_ is not None
        assert encdr.trainer_ is not None
        assert encdr.input_dim_ == small_dataset.shape[1]

        # Check scaler is fitted when standardize=True
        if encdr.standardize:
            assert encdr.scaler_ is not None
        else:
            assert encdr.scaler_ is None

    def test_fit_without_standardization(self, small_dataset):
        """Test fitting without standardization."""
        encdr = ENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=2,
            standardize=False,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        encdr.fit(small_dataset)
        assert encdr.scaler_ is None
        assert encdr.is_fitted_

    def test_transform_basic(self, small_dataset, encdr_params):
        """Test basic transform functionality."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        # Transform training data
        X_transformed = encdr.transform(small_dataset)

        assert X_transformed.shape == (small_dataset.shape[0], encdr.latent_dim)
        assert isinstance(X_transformed, np.ndarray)
        assert X_transformed.dtype == np.float32

    def test_transform_not_fitted(self, small_dataset):
        """Test that transform raises error when not fitted."""
        encdr = ENCDR()

        with pytest.raises(ValueError, match="not fitted yet"):
            encdr.transform(small_dataset)

    def test_transform_wrong_dimensions(self, small_dataset, encdr_params):
        """Test that transform raises error with wrong input dimensions."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        # Create data with wrong number of features
        wrong_data = np.random.randn(10, small_dataset.shape[1] + 5).astype(np.float32)

        with pytest.raises(ValueError, match="features"):
            encdr.transform(wrong_data)

    def test_fit_transform(self, small_dataset, encdr_params):
        """Test fit_transform method."""
        encdr = ENCDR(**encdr_params)

        X_transformed = encdr.fit_transform(small_dataset)

        assert X_transformed.shape == (small_dataset.shape[0], encdr.latent_dim)
        assert encdr.is_fitted_

    def test_inverse_transform(self, small_dataset, encdr_params):
        """Test inverse_transform functionality."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        # Transform and then inverse transform
        X_transformed = encdr.transform(small_dataset)
        X_reconstructed = encdr.inverse_transform(X_transformed)

        assert X_reconstructed.shape == small_dataset.shape
        assert isinstance(X_reconstructed, np.ndarray)

    def test_inverse_transform_not_fitted(self, encdr_params):
        """Test that inverse_transform raises error when not fitted."""
        encdr = ENCDR(**encdr_params)
        latent_data = np.random.randn(10, encdr_params["latent_dim"]).astype(np.float32)

        with pytest.raises(ValueError, match="not fitted yet"):
            encdr.inverse_transform(latent_data)

    def test_inverse_transform_wrong_dimensions(self, small_dataset, encdr_params):
        """Test that inverse_transform raises error with wrong latent dimensions."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        # Create data with wrong latent dimension
        wrong_latent = np.random.randn(10, encdr.latent_dim + 2).astype(np.float32)

        with pytest.raises(ValueError, match="expected"):
            encdr.inverse_transform(wrong_latent)

    def test_predict(self, small_dataset, encdr_params):
        """Test predict (reconstruction) functionality."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        X_reconstructed = encdr.predict(small_dataset)

        assert X_reconstructed.shape == small_dataset.shape
        assert isinstance(X_reconstructed, np.ndarray)

    def test_predict_not_fitted(self, small_dataset):
        """Test that predict raises error when not fitted."""
        encdr = ENCDR()

        with pytest.raises(ValueError, match="not fitted yet"):
            encdr.predict(small_dataset)

    def test_score(self, small_dataset, encdr_params):
        """Test score functionality."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        score = encdr.score(small_dataset)

        assert isinstance(score, float)
        assert score <= 0  # Negative MSE should be <= 0

    def test_reproducibility(self, small_dataset):
        """Test that results are reproducible with same random state."""
        params = {
            "hidden_dims": [16, 8],
            "latent_dim": 4,
            "max_epochs": 3,
            "random_state": 42,
            "trainer_kwargs": {"enable_progress_bar": False},
        }

        ncdr1 = ENCDR(**params)
        X_transformed1 = ncdr1.fit_transform(small_dataset)

        ncdr2 = ENCDR(**params)
        X_transformed2 = ncdr2.fit_transform(small_dataset)

        # Results should be very similar (allowing for small numerical differences)
        assert np.allclose(X_transformed1, X_transformed2, atol=1e-3)

    def test_different_validation_splits(self, small_dataset):
        """Test different validation split values."""
        for validation_split in [0.0, 0.1, 0.3, 0.5]:
            encdr = ENCDR(
                hidden_dims=[16, 8],
                latent_dim=4,
                max_epochs=2,
                validation_split=validation_split,
                random_state=42,
                trainer_kwargs={"enable_progress_bar": False},
            )

            encdr.fit(small_dataset)
            assert encdr.is_fitted_

    def test_y_parameter_ignored(self, small_dataset, encdr_params):
        """Test that y parameter is properly ignored in fit methods."""
        encdr = ENCDR(**encdr_params)
        y = np.random.randn(small_dataset.shape[0])

        # Should work with y parameter
        encdr.fit(small_dataset, y)
        assert encdr.is_fitted_

        # fit_transform should also work with y
        ncdr2 = ENCDR(**encdr_params)
        X_transformed = ncdr2.fit_transform(small_dataset, y)
        assert X_transformed.shape == (small_dataset.shape[0], ncdr2.latent_dim)

    def test_sklearn_compatibility(self, small_dataset, encdr_params):
        """Test compatibility with sklearn interface."""
        encdr = ENCDR(**encdr_params)

        # Test that it has required sklearn methods
        assert hasattr(encdr, "fit")
        assert hasattr(encdr, "transform")
        assert hasattr(encdr, "fit_transform")
        assert hasattr(encdr, "score")

        # Test that it works in sklearn-style pipeline
        encdr.fit(small_dataset)
        assert encdr.is_fitted_

        # Check that get_params works (inherited from BaseEstimator)
        params = encdr.get_params()
        assert "hidden_dims" in params
        assert "latent_dim" in params

    def test_medium_dataset(self, medium_dataset):
        """Test with medium-sized dataset to ensure scalability."""
        encdr = ENCDR(
            hidden_dims=[64, 32, 16],
            latent_dim=8,
            max_epochs=3,
            batch_size=32,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        X_transformed = encdr.fit_transform(medium_dataset)
        assert X_transformed.shape == (medium_dataset.shape[0], 8)

        X_reconstructed = encdr.predict(medium_dataset)
        assert X_reconstructed.shape == medium_dataset.shape

        score = encdr.score(medium_dataset)
        assert isinstance(score, float)

    def test_reconstruction_quality(self, regression_dataset):
        """Test that reconstruction has reasonable quality."""
        encdr = ENCDR(
            hidden_dims=[40, 20],
            latent_dim=10,
            max_epochs=10,
            learning_rate=1e-2,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        encdr.fit(regression_dataset)
        X_reconstructed = encdr.predict(regression_dataset)

        # Calculate reconstruction error
        mse = np.mean((regression_dataset - X_reconstructed) ** 2)

        # MSE should be reasonable (not too high)
        assert mse < 10.0  # Adjust threshold based on expected performance

    def test_latent_space_dimensionality(self, small_dataset):
        """Test that latent space has correct dimensionality."""
        for latent_dim in [2, 5, 8, 15]:
            encdr = ENCDR(
                hidden_dims=[20, 10],
                latent_dim=latent_dim,
                max_epochs=2,
                random_state=42,
                trainer_kwargs={"enable_progress_bar": False},
            )

            X_transformed = encdr.fit_transform(small_dataset)
            assert X_transformed.shape[1] == latent_dim
