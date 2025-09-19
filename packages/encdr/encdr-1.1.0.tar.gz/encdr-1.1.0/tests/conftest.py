"""Test configuration and fixtures for ENCDR tests."""

import numpy as np
import pytest
import torch
from sklearn.datasets import make_classification, make_regression


@pytest.fixture
def random_state():
    """Random state for reproducible tests."""
    return 42


@pytest.fixture
def small_dataset(random_state):
    """Small dataset for quick tests."""
    X, _ = make_classification(
        n_samples=100,
        n_features=20,
        n_informative=10,
        n_redundant=5,
        random_state=random_state,
    )
    return X.astype(np.float32)


@pytest.fixture
def medium_dataset(random_state):
    """Medium dataset for more thorough tests."""
    X, _ = make_classification(
        n_samples=500,
        n_features=50,
        n_informative=25,
        n_redundant=10,
        random_state=random_state,
    )
    return X.astype(np.float32)


@pytest.fixture
def regression_dataset(random_state):
    """Regression dataset for reconstruction tests."""
    X, _ = make_regression(
        n_samples=200,
        n_features=30,
        n_informative=20,
        noise=0.1,
        random_state=random_state,
    )
    return X.astype(np.float32)


@pytest.fixture
def encdr_params():
    """Default ENCDR parameters for testing."""
    return {
        "hidden_dims": [32, 16],
        "latent_dim": 8,
        "learning_rate": 1e-3,
        "activation": "relu",
        "dropout_rate": 0.1,
        "batch_size": 16,
        "max_epochs": 5,  # Short epochs for testing
        "validation_split": 0.2,
        "standardize": True,
        "random_state": 42,
        "trainer_kwargs": {"enable_progress_bar": False},  # Quiet training
    }
