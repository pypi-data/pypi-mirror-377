"""Tests for save/load functionality of the ENCDR class."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from sklearn.datasets import make_classification

from encdr import ENCDR


class TestENCDRSaveLoad:
    """Test suite for ENCDR save/load functionality."""

    def test_save_fitted_model(self, small_dataset, encdr_params, tmp_path):
        """Test saving a fitted model."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        # Save to a temporary file
        save_path = tmp_path / "test_model.pkl"
        encdr.save(save_path)

        # Check that file was created
        assert save_path.exists()
        assert save_path.stat().st_size > 0

    def test_save_unfitted_model(self, encdr_params, tmp_path):
        """Test that saving an unfitted model raises an error."""
        encdr = ENCDR(**encdr_params)
        save_path = tmp_path / "test_model.pkl"

        with pytest.raises(ValueError, match="Cannot save an unfitted model"):
            encdr.save(save_path)

    def test_save_auto_extension(self, small_dataset, encdr_params, tmp_path):
        """Test that .pkl extension is added automatically."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        # Save without extension
        save_path = tmp_path / "test_model"
        encdr.save(save_path)

        # Check that .pkl extension was added
        expected_path = tmp_path / "test_model.pkl"
        assert expected_path.exists()

    def test_save_creates_directory(self, small_dataset, encdr_params, tmp_path):
        """Test that save creates directories if they don't exist."""
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        # Save to a nested directory that doesn't exist
        save_path = tmp_path / "nested" / "dir" / "test_model.pkl"
        encdr.save(save_path)

        # Check that file was created
        assert save_path.exists()

    def test_load_basic(self, small_dataset, encdr_params, tmp_path):
        """Test basic loading functionality."""
        # Train and save model
        original_encdr = ENCDR(**encdr_params)
        original_encdr.fit(small_dataset)

        save_path = tmp_path / "test_model.pkl"
        original_encdr.save(save_path)

        # Load model
        loaded_encdr = ENCDR.load(save_path)

        # Check that loaded model has same parameters
        assert loaded_encdr.hidden_dims == original_encdr.hidden_dims
        assert loaded_encdr.latent_dim == original_encdr.latent_dim
        assert loaded_encdr.learning_rate == original_encdr.learning_rate
        assert loaded_encdr.activation == original_encdr.activation
        assert loaded_encdr.is_fitted_ == original_encdr.is_fitted_
        assert loaded_encdr.input_dim_ == original_encdr.input_dim_

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading from a non-existent file."""
        save_path = tmp_path / "nonexistent.pkl"

        with pytest.raises(FileNotFoundError, match="Model file not found"):
            ENCDR.load(save_path)

    def test_save_load_preserves_predictions(
        self, small_dataset, encdr_params, tmp_path
    ):
        """Test that save/load preserves model predictions."""
        # Train model
        original_encdr = ENCDR(**encdr_params)
        original_encdr.fit(small_dataset)

        # Get predictions from original model
        original_transform = original_encdr.transform(small_dataset)
        original_predict = original_encdr.predict(small_dataset)
        original_score = original_encdr.score(small_dataset)

        # Save and load model
        save_path = tmp_path / "test_model.pkl"
        original_encdr.save(save_path)
        loaded_encdr = ENCDR.load(save_path)

        # Get predictions from loaded model
        loaded_transform = loaded_encdr.transform(small_dataset)
        loaded_predict = loaded_encdr.predict(small_dataset)
        loaded_score = loaded_encdr.score(small_dataset)

        # Predictions should be identical (or very close due to floating point)
        np.testing.assert_allclose(original_transform, loaded_transform, rtol=1e-6)
        np.testing.assert_allclose(original_predict, loaded_predict, rtol=1e-6)
        assert abs(original_score - loaded_score) < 1e-6

    def test_save_load_with_scaler(self, small_dataset, tmp_path):
        """Test save/load with standardization enabled."""
        encdr_params = {
            "hidden_dims": [32, 16],
            "latent_dim": 8,
            "max_epochs": 3,
            "standardize": True,  # Enable standardization
            "random_state": 42,
            "trainer_kwargs": {"enable_progress_bar": False},
        }

        # Train model with scaler
        original_encdr = ENCDR(**encdr_params)
        original_encdr.fit(small_dataset)

        # Save and load
        save_path = tmp_path / "test_model_with_scaler.pkl"
        original_encdr.save(save_path)
        loaded_encdr = ENCDR.load(save_path)

        # Check that scaler is preserved
        assert loaded_encdr.scaler_ is not None
        assert hasattr(loaded_encdr.scaler_, "mean_")
        assert hasattr(loaded_encdr.scaler_, "scale_")

        # Verify predictions are identical
        original_predictions = original_encdr.predict(small_dataset)
        loaded_predictions = loaded_encdr.predict(small_dataset)
        np.testing.assert_allclose(original_predictions, loaded_predictions, rtol=1e-6)

    def test_save_load_without_scaler(self, small_dataset, tmp_path):
        """Test save/load without standardization."""
        encdr_params = {
            "hidden_dims": [32, 16],
            "latent_dim": 8,
            "max_epochs": 3,
            "standardize": False,  # Disable standardization
            "random_state": 42,
            "trainer_kwargs": {"enable_progress_bar": False},
        }

        # Train model without scaler
        original_encdr = ENCDR(**encdr_params)
        original_encdr.fit(small_dataset)

        # Save and load
        save_path = tmp_path / "test_model_no_scaler.pkl"
        original_encdr.save(save_path)
        loaded_encdr = ENCDR.load(save_path)

        # Check that scaler is None
        assert loaded_encdr.scaler_ is None

        # Verify predictions are identical
        original_predictions = original_encdr.predict(small_dataset)
        loaded_predictions = loaded_encdr.predict(small_dataset)
        np.testing.assert_allclose(original_predictions, loaded_predictions, rtol=1e-6)

    def test_save_load_different_architectures(self, small_dataset, tmp_path):
        """Test save/load with different model architectures."""
        architectures = [
            {"hidden_dims": [16], "latent_dim": 4},
            {"hidden_dims": [64, 32, 16], "latent_dim": 8},
            {"hidden_dims": [128, 64], "latent_dim": 16},
        ]

        for i, arch_params in enumerate(architectures):
            encdr_params = {
                **arch_params,
                "max_epochs": 3,
                "random_state": 42,
                "trainer_kwargs": {"enable_progress_bar": False},
            }

            # Train and save
            original_encdr = ENCDR(**encdr_params)
            original_encdr.fit(small_dataset)

            save_path = tmp_path / f"model_{i}.pkl"
            original_encdr.save(save_path)

            # Load and verify
            loaded_encdr = ENCDR.load(save_path)
            assert loaded_encdr.hidden_dims == arch_params["hidden_dims"]
            assert loaded_encdr.latent_dim == arch_params["latent_dim"]

            # Test predictions
            original_transform = original_encdr.transform(small_dataset)
            loaded_transform = loaded_encdr.transform(small_dataset)
            np.testing.assert_allclose(original_transform, loaded_transform, rtol=1e-6)

    def test_save_load_custom_parameters(self, small_dataset, tmp_path):
        """Test save/load with custom parameters."""
        custom_params = {
            "hidden_dims": [50, 25],
            "latent_dim": 12,
            "learning_rate": 0.005,
            "activation": "tanh",
            "dropout_rate": 0.3,
            "weight_decay": 1e-4,
            "batch_size": 64,
            "max_epochs": 5,
            "validation_split": 0.3,
            "standardize": True,
            "random_state": 123,
            "trainer_kwargs": {
                "enable_progress_bar": False,
                "enable_checkpointing": False,
            },
        }

        # Train and save
        original_encdr = ENCDR(**custom_params)
        original_encdr.fit(small_dataset)

        save_path = tmp_path / "custom_model.pkl"
        original_encdr.save(save_path)

        # Load and verify all parameters
        loaded_encdr = ENCDR.load(save_path)

        for param_name, param_value in custom_params.items():
            assert getattr(loaded_encdr, param_name) == param_value

    def test_load_model_is_in_eval_mode(self, small_dataset, encdr_params, tmp_path):
        """Test that loaded model is in evaluation mode."""
        # Train and save model
        original_encdr = ENCDR(**encdr_params)
        original_encdr.fit(small_dataset)

        save_path = tmp_path / "test_model.pkl"
        original_encdr.save(save_path)

        # Load model
        loaded_encdr = ENCDR.load(save_path)

        # Check that model is in eval mode
        assert not loaded_encdr.model_.training

    def test_save_load_with_string_path(self, small_dataset, encdr_params, tmp_path):
        """Test save/load using string paths instead of Path objects."""
        # Train model
        original_encdr = ENCDR(**encdr_params)
        original_encdr.fit(small_dataset)

        # Save using string path
        save_path = str(tmp_path / "string_path_model.pkl")
        original_encdr.save(save_path)

        # Load using string path
        loaded_encdr = ENCDR.load(save_path)

        # Verify functionality
        original_predictions = original_encdr.predict(small_dataset)
        loaded_predictions = loaded_encdr.predict(small_dataset)
        np.testing.assert_allclose(original_predictions, loaded_predictions, rtol=1e-6)

    def test_multiple_save_load_cycles(self, small_dataset, encdr_params, tmp_path):
        """Test multiple save/load cycles."""
        # Train initial model
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        original_predictions = encdr.predict(small_dataset)

        # Multiple save/load cycles
        for i in range(3):
            save_path = tmp_path / f"cycle_{i}.pkl"
            encdr.save(save_path)
            encdr = ENCDR.load(save_path)

        # Final predictions should still match
        final_predictions = encdr.predict(small_dataset)
        np.testing.assert_allclose(original_predictions, final_predictions, rtol=1e-6)

    def test_save_load_error_handling(self, small_dataset, encdr_params, tmp_path):
        """Test error handling in save/load operations."""
        # Test loading corrupted file
        corrupted_file = tmp_path / "corrupted.pkl"
        with open(corrupted_file, "w") as f:
            f.write("not a pickle file")

        with pytest.raises(
            Exception
        ):  # Should raise some kind of pickle/unpickling error
            ENCDR.load(corrupted_file)

        # Test saving to invalid path (permission error simulation)
        encdr = ENCDR(**encdr_params)
        encdr.fit(small_dataset)

        # This test might be platform-dependent, so we'll be careful
        try:
            invalid_path = Path("/") / "invalid_dir" / "model.pkl"
            # This should work on most systems as we create parent directories
            # but if it fails, that's also acceptable behavior
            encdr.save(invalid_path)
        except (PermissionError, OSError):
            # Expected on some systems
            pass

    def test_save_load_large_model(self, tmp_path):
        """Test save/load with a larger model to ensure scalability."""
        # Create larger dataset
        X, _ = make_classification(
            n_samples=1000, n_features=100, n_informative=50, random_state=42
        )
        X = X.astype(np.float32)

        # Train larger model
        large_encdr_params = {
            "hidden_dims": [256, 128, 64, 32],
            "latent_dim": 16,
            "max_epochs": 3,
            "batch_size": 64,
            "random_state": 42,
            "trainer_kwargs": {"enable_progress_bar": False},
        }

        encdr = ENCDR(**large_encdr_params)
        encdr.fit(X)

        # Save and load
        save_path = tmp_path / "large_model.pkl"
        encdr.save(save_path)
        loaded_encdr = ENCDR.load(save_path)

        # Verify predictions on subset of data (for speed)
        test_subset = X[:100]
        original_predictions = encdr.predict(test_subset)
        loaded_predictions = loaded_encdr.predict(test_subset)
        np.testing.assert_allclose(original_predictions, loaded_predictions, rtol=1e-6)
