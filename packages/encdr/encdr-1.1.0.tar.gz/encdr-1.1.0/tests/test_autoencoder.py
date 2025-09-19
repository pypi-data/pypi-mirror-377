"""Tests for the AutoEncoder PyTorch Lightning module."""

import numpy as np
import pytest
import torch

from encdr.autoencoder import AutoEncoder


class TestAutoEncoder:
    """Test suite for AutoEncoder class."""

    def test_autoencoder_initialization(self):
        """Test AutoEncoder initialization with default parameters."""
        model = AutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)

        assert model.input_dim == 20
        assert model.hidden_dims == [16, 8]
        assert model.latent_dim == 4
        assert model.learning_rate == 1e-3
        assert model.dropout_rate == 0.0
        assert model.weight_decay == 0.0

    def test_autoencoder_initialization_custom_params(self):
        """Test AutoEncoder initialization with custom parameters."""
        model = AutoEncoder(
            input_dim=50,
            hidden_dims=[64, 32, 16],
            latent_dim=10,
            learning_rate=0.01,
            activation="tanh",
            dropout_rate=0.2,
            weight_decay=1e-4,
        )

        assert model.input_dim == 50
        assert model.hidden_dims == [64, 32, 16]
        assert model.latent_dim == 10
        assert model.learning_rate == 0.01
        assert model.dropout_rate == 0.2
        assert model.weight_decay == 1e-4

    def test_activation_functions(self):
        """Test different activation functions."""
        activations = ["relu", "tanh", "sigmoid", "leaky_relu", "elu", "gelu"]

        for activation in activations:
            model = AutoEncoder(
                input_dim=10, hidden_dims=[8], latent_dim=4, activation=activation
            )
            assert model.activation_fn is not None

    def test_invalid_activation_function(self):
        """Test that invalid activation function raises error."""
        with pytest.raises(ValueError, match="Unsupported activation function"):
            AutoEncoder(
                input_dim=10,
                hidden_dims=[8],
                latent_dim=4,
                activation="invalid_activation",
            )

    def test_encoder_decoder_architecture(self):
        """Test that encoder and decoder have correct architecture."""
        model = AutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)

        # Test encoder dimensions
        x = torch.randn(10, 20)
        encoded = model.encode(x)
        assert encoded.shape == (10, 4)

        # Test decoder dimensions
        z = torch.randn(10, 4)
        decoded = model.decode(z)
        assert decoded.shape == (10, 20)

        # Test full forward pass
        reconstruction = model(x)
        assert reconstruction.shape == x.shape

    def test_forward_pass_different_batch_sizes(self):
        """Test forward pass with different batch sizes."""
        model = AutoEncoder(input_dim=15, hidden_dims=[12, 6], latent_dim=3)

        for batch_size in [1, 5, 32, 100]:
            x = torch.randn(batch_size, 15)
            reconstruction = model(x)
            assert reconstruction.shape == (batch_size, 15)

    def test_training_step(self):
        """Test training step computation."""
        model = AutoEncoder(input_dim=10, hidden_dims=[8], latent_dim=4)

        batch = torch.randn(16, 10)
        loss = model.training_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0  # MSE loss should be non-negative

    def test_validation_step(self):
        """Test validation step computation."""
        model = AutoEncoder(input_dim=10, hidden_dims=[8], latent_dim=4)

        batch = torch.randn(16, 10)
        loss = model.validation_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_test_step(self):
        """Test test step computation."""
        model = AutoEncoder(input_dim=10, hidden_dims=[8], latent_dim=4)

        batch = torch.randn(16, 10)
        loss = model.test_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_predict_step(self):
        """Test predict step."""
        model = AutoEncoder(input_dim=10, hidden_dims=[8], latent_dim=4)

        batch = torch.randn(16, 10)
        prediction = model.predict_step(batch, 0)

        assert isinstance(prediction, torch.Tensor)
        assert prediction.shape == batch.shape

    def test_configure_optimizers(self):
        """Test optimizer configuration."""
        model = AutoEncoder(
            input_dim=10,
            hidden_dims=[8],
            latent_dim=4,
            learning_rate=0.01,
            weight_decay=1e-4,
        )

        optimizer = model.configure_optimizers()
        assert isinstance(optimizer, torch.optim.Adam)
        assert optimizer.param_groups[0]["lr"] == 0.01
        assert optimizer.param_groups[0]["weight_decay"] == 1e-4

    def test_dropout_in_training_mode(self):
        """Test that dropout works in training mode."""
        model = AutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, dropout_rate=0.5
        )

        x = torch.randn(100, 20)

        # Set to training mode
        model.train()
        output1 = model(x)
        output2 = model(x)

        # With dropout, outputs should be different
        assert not torch.allclose(output1, output2, atol=1e-6)

        # Set to evaluation mode
        model.eval()
        output3 = model(x)
        output4 = model(x)

        # Without dropout, outputs should be identical
        assert torch.allclose(output3, output4, atol=1e-6)

    def test_batch_handling_with_tuples(self):
        """Test handling of batch data as tuples."""
        model = AutoEncoder(input_dim=10, hidden_dims=[8], latent_dim=4)

        # Test with tuple batch (x, y)
        x = torch.randn(16, 10)
        y = torch.randn(16, 1)
        batch = (x, y)

        loss = model.training_step(batch, 0)
        assert isinstance(loss, torch.Tensor)

        # Test with single tensor batch
        batch = x
        loss = model.training_step(batch, 0)
        assert isinstance(loss, torch.Tensor)

    def test_model_reproducibility(self):
        """Test that model produces reproducible results with same seed."""
        torch.manual_seed(42)
        model1 = AutoEncoder(input_dim=10, hidden_dims=[8], latent_dim=4)

        torch.manual_seed(42)
        model2 = AutoEncoder(input_dim=10, hidden_dims=[8], latent_dim=4)

        x = torch.randn(5, 10)

        # Both models should produce same output
        with torch.no_grad():
            output1 = model1(x)
            output2 = model2(x)

        assert torch.allclose(output1, output2, atol=1e-6)
