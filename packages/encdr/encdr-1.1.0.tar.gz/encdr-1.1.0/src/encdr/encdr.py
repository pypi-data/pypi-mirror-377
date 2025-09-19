"""
NCDR: Neural Component Dimensionality Reduction

A scikit-learn compatible autoencoder for dimensionality reduction and reconstruction.
"""

import pickle
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import lightning as L
import numpy as np
import torch
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_array, check_X_y
from torch.utils.data import DataLoader, TensorDataset

from .autoencoder import AutoEncoder


class ENCDR(BaseEstimator, TransformerMixin):
    """
    Neural Component Dimensionality Reduction using autoencoders.

    This class provides a scikit-learn compatible interface for training
    and using PyTorch Lightning autoencoder models for dimensionality
    reduction and reconstruction tasks.

    Parameters
    ----------
    hidden_dims : list of int, default=[64, 32]
        List of hidden layer dimensions for the encoder.
    latent_dim : int, default=10
        Dimension of the latent (bottleneck) layer.
    learning_rate : float, default=1e-3
        Learning rate for optimization.
    activation : str, default='relu'
        Activation function ('relu', 'tanh', 'sigmoid', 'leaky_relu', 'elu', 'gelu').
    dropout_rate : float, default=0.0
        Dropout rate for regularization.
    weight_decay : float, default=0.0
        L2 regularization weight decay.
    batch_size : int, default=32
        Batch size for training.
    max_epochs : int, default=100
        Maximum number of training epochs.
    validation_split : float, default=0.2
        Fraction of data to use for validation.
    standardize : bool, default=True
        Whether to standardize input features.
    random_state : int, optional
        Random seed for reproducibility.
    trainer_kwargs : dict, optional
        Additional keyword arguments for PyTorch Lightning Trainer.
    """

    def __init__(
        self,
        hidden_dims: List[int] = [64, 32],
        latent_dim: int = 10,
        learning_rate: float = 1e-3,
        activation: str = "relu",
        dropout_rate: float = 0.0,
        weight_decay: float = 0.0,
        batch_size: int = 32,
        max_epochs: int = 100,
        validation_split: float = 0.2,
        standardize: bool = True,
        random_state: Optional[int] = None,
        trainer_kwargs: Optional[dict] = None,
    ):
        self.hidden_dims = hidden_dims
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        self.activation = activation
        self.dropout_rate = dropout_rate
        self.weight_decay = weight_decay
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.validation_split = validation_split
        self.standardize = standardize
        self.random_state = random_state
        self.trainer_kwargs = trainer_kwargs or {}

        # Internal attributes
        self.model_ = None
        self.trainer_ = None
        self.scaler_ = None
        self.input_dim_ = None
        self.is_fitted_ = False

    def _setup_random_state(self):
        """Setup random state for reproducibility."""
        if self.random_state is not None:
            torch.manual_seed(self.random_state)
            np.random.seed(self.random_state)
            L.seed_everything(self.random_state)

    def _prepare_data(
        self, X: np.ndarray, y: Optional[np.ndarray] = None
    ) -> Tuple[DataLoader, Optional[DataLoader]]:
        """Prepare data loaders for training."""
        X = torch.FloatTensor(X)

        if y is not None:
            y = torch.FloatTensor(y) if y.dtype != np.int64 else torch.LongTensor(y)
            dataset = TensorDataset(X, y)
        else:
            dataset = TensorDataset(X)

        # Split into train/validation if validation_split > 0
        if self.validation_split > 0:
            n_val = int(len(dataset) * self.validation_split)
            n_train = len(dataset) - n_val

            if self.random_state is not None:
                generator = torch.Generator().manual_seed(self.random_state)
                train_dataset, val_dataset = torch.utils.data.random_split(
                    dataset, [n_train, n_val], generator=generator
                )
            else:
                train_dataset, val_dataset = torch.utils.data.random_split(
                    dataset, [n_train, n_val]
                )

            train_loader = DataLoader(
                train_dataset, batch_size=self.batch_size, shuffle=True
            )
            val_loader = DataLoader(
                val_dataset, batch_size=self.batch_size, shuffle=False
            )
            return train_loader, val_loader
        else:
            train_loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
            return train_loader, None

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> "ENCDR":
        """
        Fit the autoencoder model to the data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,), optional
            Target values (ignored, present for API compatibility).

        Returns
        -------
        self : object
            Returns the instance itself.
        """
        self._setup_random_state()

        # Validate input
        X = check_array(X, accept_sparse=False, dtype=np.float32)

        # Store input dimension
        self.input_dim_ = X.shape[1]

        # Standardize features if requested
        if self.standardize:
            self.scaler_ = StandardScaler()
            X = self.scaler_.fit_transform(X)

        # Prepare data loaders
        train_loader, val_loader = self._prepare_data(X, y)

        # Create model
        self.model_ = AutoEncoder(
            input_dim=self.input_dim_,
            hidden_dims=self.hidden_dims,
            latent_dim=self.latent_dim,
            learning_rate=self.learning_rate,
            activation=self.activation,
            dropout_rate=self.dropout_rate,
            weight_decay=self.weight_decay,
        )

        # Setup trainer
        trainer_kwargs = {
            "max_epochs": self.max_epochs,
            "logger": False,  # Disable logging by default
            "enable_checkpointing": False,  # Disable checkpointing by default
            "enable_progress_bar": True,
            **self.trainer_kwargs,
        }

        self.trainer_ = L.Trainer(**trainer_kwargs)

        # Train model
        self.trainer_.fit(self.model_, train_loader, val_loader)

        self.is_fitted_ = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform data to latent representation.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Data to transform.

        Returns
        -------
        X_transformed : ndarray of shape (n_samples, latent_dim)
            Latent representation of the data.
        """
        if not self.is_fitted_:
            raise ValueError("This NCDR instance is not fitted yet. Call 'fit' first.")

        X = check_array(X, accept_sparse=False, dtype=np.float32)

        # Check input dimension
        if X.shape[1] != self.input_dim_:
            raise ValueError(
                f"X has {X.shape[1]} features, but NCDR was fitted with {self.input_dim_} features."
            )

        # Standardize if scaler was fitted
        if self.scaler_ is not None:
            X = self.scaler_.transform(X)

        # Convert to tensor and encode
        self.model_.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X)
            latent = self.model_.encode(X_tensor)

        return latent.numpy()

    def fit_transform(
        self, X: np.ndarray, y: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Fit the model and transform the data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,), optional
            Target values (ignored).

        Returns
        -------
        X_transformed : ndarray of shape (n_samples, latent_dim)
            Latent representation of the training data.
        """
        return self.fit(X, y).transform(X)

    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Reconstruct data from latent representation.

        Parameters
        ----------
        X : array-like of shape (n_samples, latent_dim)
            Latent representation to reconstruct.

        Returns
        -------
        X_reconstructed : ndarray of shape (n_samples, n_features)
            Reconstructed data.
        """
        if not self.is_fitted_:
            raise ValueError("This NCDR instance is not fitted yet. Call 'fit' first.")

        X = check_array(X, accept_sparse=False, dtype=np.float32)

        # Check latent dimension
        if X.shape[1] != self.latent_dim:
            raise ValueError(
                f"X has {X.shape[1]} features, but expected {self.latent_dim} (latent_dim)."
            )

        # Convert to tensor and decode
        self.model_.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X)
            reconstruction = self.model_.decode(X_tensor)

        reconstruction = reconstruction.numpy()

        # Inverse standardize if scaler was fitted
        if self.scaler_ is not None:
            reconstruction = self.scaler_.inverse_transform(reconstruction)

        return reconstruction

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict (reconstruct) the input data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Data to reconstruct.

        Returns
        -------
        X_reconstructed : ndarray of shape (n_samples, n_features)
            Reconstructed data.
        """
        if not self.is_fitted_:
            raise ValueError("This NCDR instance is not fitted yet. Call 'fit' first.")

        X = check_array(X, accept_sparse=False, dtype=np.float32)

        # Check input dimension
        if X.shape[1] != self.input_dim_:
            raise ValueError(
                f"X has {X.shape[1]} features, but NCDR was fitted with {self.input_dim_} features."
            )

        # Standardize if scaler was fitted
        if self.scaler_ is not None:
            X = self.scaler_.transform(X)

        # Convert to tensor and get reconstruction
        self.model_.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X)
            reconstruction = self.model_(X_tensor)

        reconstruction = reconstruction.numpy()

        # Inverse standardize if scaler was fitted
        if self.scaler_ is not None:
            reconstruction = self.scaler_.inverse_transform(reconstruction)

        return reconstruction

    def score(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> float:
        """
        Return the mean reconstruction error (negative MSE).

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test data.
        y : array-like of shape (n_samples,), optional
            Target values (ignored).

        Returns
        -------
        score : float
            Mean reconstruction error (negative MSE).
        """
        reconstruction = self.predict(X)
        mse = np.mean((X - reconstruction) ** 2)
        return float(-mse)  # Return negative MSE (higher is better)

    def save(self, filepath: Union[str, Path]) -> None:
        """
        Save the fitted ENCDR model to disk.

        Parameters
        ----------
        filepath : str or Path
            Path where the model will be saved. If no extension is provided,
            '.pkl' will be added automatically.

        Raises
        ------
        ValueError
            If the model has not been fitted yet.
        """
        if not self.is_fitted_:
            raise ValueError("Cannot save an unfitted model. Call 'fit' first.")

        filepath = Path(filepath)
        if not filepath.suffix:
            filepath = filepath.with_suffix(".pkl")

        # Create directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Prepare state to save
        save_state = {
            # Model parameters
            "hidden_dims": self.hidden_dims,
            "latent_dim": self.latent_dim,
            "learning_rate": self.learning_rate,
            "activation": self.activation,
            "dropout_rate": self.dropout_rate,
            "weight_decay": self.weight_decay,
            "batch_size": self.batch_size,
            "max_epochs": self.max_epochs,
            "validation_split": self.validation_split,
            "standardize": self.standardize,
            "random_state": self.random_state,
            "trainer_kwargs": self.trainer_kwargs,
            # Fitted state
            "input_dim_": self.input_dim_,
            "is_fitted_": self.is_fitted_,
            # Model state dict
            "model_state_dict": self.model_.state_dict(),
            # Scaler
            "scaler_": self.scaler_,
        }

        with open(filepath, "wb") as f:
            pickle.dump(save_state, f)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "ENCDR":
        """
        Load a saved ENCDR model from disk.

        Parameters
        ----------
        filepath : str or Path
            Path to the saved model file.

        Returns
        -------
        encdr : ENCDR
            The loaded ENCDR instance.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, "rb") as f:
            save_state = pickle.load(f)

        # Extract parameters for initialization
        init_params = {
            "hidden_dims": save_state["hidden_dims"],
            "latent_dim": save_state["latent_dim"],
            "learning_rate": save_state["learning_rate"],
            "activation": save_state["activation"],
            "dropout_rate": save_state["dropout_rate"],
            "weight_decay": save_state["weight_decay"],
            "batch_size": save_state["batch_size"],
            "max_epochs": save_state["max_epochs"],
            "validation_split": save_state["validation_split"],
            "standardize": save_state["standardize"],
            "random_state": save_state["random_state"],
            "trainer_kwargs": save_state["trainer_kwargs"],
        }

        # Create new instance
        encdr = cls(**init_params)

        # Restore fitted state
        encdr.input_dim_ = save_state["input_dim_"]
        encdr.is_fitted_ = save_state["is_fitted_"]
        encdr.scaler_ = save_state["scaler_"]

        # Recreate and load model
        if encdr.is_fitted_:
            encdr.model_ = AutoEncoder(
                input_dim=encdr.input_dim_,
                hidden_dims=encdr.hidden_dims,
                latent_dim=encdr.latent_dim,
                learning_rate=encdr.learning_rate,
                activation=encdr.activation,
                dropout_rate=encdr.dropout_rate,
                weight_decay=encdr.weight_decay,
            )
            encdr.model_.load_state_dict(save_state["model_state_dict"])
            encdr.model_.eval()

        return encdr
