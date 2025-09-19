"""
PyTorch Lightning autoencoder model for dimensionality reduction.
"""

from typing import List, Optional, Union

import lightning as L
import torch
import torch.nn as nn
import torch.nn.functional as F


class AutoEncoder(L.LightningModule):
    """
    A configurable autoencoder model using PyTorch Lightning.

    This model supports various architectures with customizable layers,
    activation functions, and training parameters.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        latent_dim: int,
        learning_rate: float = 1e-3,
        activation: str = "relu",
        dropout_rate: float = 0.0,
        weight_decay: float = 0.0,
    ):
        """
        Initialize the autoencoder.

        Args:
            input_dim: Dimension of input features
            hidden_dims: List of hidden layer dimensions for encoder
            latent_dim: Dimension of the latent (bottleneck) layer
            learning_rate: Learning rate for optimization
            activation: Activation function ('relu', 'tanh', 'sigmoid', 'leaky_relu')
            dropout_rate: Dropout rate for regularization
            weight_decay: L2 regularization weight decay
        """
        super().__init__()
        self.save_hyperparameters()

        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        self.weight_decay = weight_decay

        # Get activation function
        self.activation_fn = self._get_activation_function(activation)

        # Build encoder
        encoder_layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            encoder_layers.extend(
                [
                    nn.Linear(prev_dim, hidden_dim),
                    self.activation_fn,
                    nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity(),
                ]
            )
            prev_dim = hidden_dim

        # Add final layer to latent space
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)

        # Build decoder (mirror of encoder)
        decoder_layers = []
        prev_dim = latent_dim

        # Reverse the hidden dimensions for decoder
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend(
                [
                    nn.Linear(prev_dim, hidden_dim),
                    self.activation_fn,
                    nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity(),
                ]
            )
            prev_dim = hidden_dim

        # Add final reconstruction layer
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)

    def _get_activation_function(self, activation: str) -> nn.Module:
        """Get activation function by name."""
        activation_map = {
            "relu": nn.ReLU(),
            "tanh": nn.Tanh(),
            "sigmoid": nn.Sigmoid(),
            "leaky_relu": nn.LeakyReLU(),
            "elu": nn.ELU(),
            "gelu": nn.GELU(),
        }

        if activation.lower() not in activation_map:
            raise ValueError(f"Unsupported activation function: {activation}")

        return activation_map[activation.lower()]

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation."""
        return self.encoder(x)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to reconstruction."""
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through autoencoder."""
        z = self.encode(x)
        reconstruction = self.decode(z)
        return reconstruction

    def training_step(self, batch, batch_idx):
        """Training step for PyTorch Lightning."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        x_hat = self(x)
        loss = F.mse_loss(x_hat, x)

        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        """Validation step for PyTorch Lightning."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        x_hat = self(x)
        loss = F.mse_loss(x_hat, x)

        self.log("val_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        """Test step for PyTorch Lightning."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        x_hat = self(x)
        loss = F.mse_loss(x_hat, x)

        self.log("test_loss", loss, on_step=False, on_epoch=True)
        return loss

    def configure_optimizers(self):
        """Configure optimizer for training."""
        optimizer = torch.optim.Adam(
            self.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
        )
        return optimizer

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        """Prediction step for inference."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        return self(x)
