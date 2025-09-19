# NCDR - Neural Component Dimensionality Reduction

A Python library for autoencoder-based dimensionality reduction with a scikit-learn compatible interface.

## Features

- **Scikit-learn Compatible**: Implements `fit()`, `transform()`, `predict()`, and `fit_transform()` methods
- **PyTorch Lightning Backend**: Deep learning framework with automatic GPU support
- **Configurable Architecture**: Customizable encoder/decoder layers, activation functions, and training parameters
- **Automatic Standardization**: Optional feature scaling for improved training stability
- **Validation Support**: Built-in train/validation splits for monitoring training progress
- **Multiple Activation Functions**: Support for ReLU, Tanh, Sigmoid, LeakyReLU, ELU, and GELU

## Installation

```bash
uv add pyncdr
# or
pip install pyncdr
```

## Dependencies

- Python ≥ 3.12
- PyTorch Lightning ≥ 2.5.5
- scikit-learn ≥ 1.7.2
- torch ≥ 2.0.0
- numpy ≥ 1.21.0

## Quick Start

```python
from ncdr import NCDR
from sklearn.datasets import make_classification
import numpy as np

# Generate sample data
X, _ = make_classification(n_samples=1000, n_features=50, n_informative=30, random_state=42)

# Create and train autoencoder
ncdr = NCDR(
    hidden_dims=[64, 32, 16],  # Encoder layer sizes
    latent_dim=8,              # Bottleneck dimension
    max_epochs=50,             # Training epochs
    random_state=42
)

# Fit and transform data
X_reduced = ncdr.fit_transform(X)
print(f"Original shape: {X.shape}, Reduced shape: {X_reduced.shape}")

# Reconstruct original data
X_reconstructed = ncdr.predict(X)
reconstruction_error = np.mean((X - X_reconstructed) ** 2)
print(f"Reconstruction MSE: {reconstruction_error:.4f}")
```

## Advanced Usage

### Custom Architecture

```python
ncdr = NCDR(
    hidden_dims=[128, 64, 32, 16],     # Deep architecture
    latent_dim=10,                     # 10D latent space
    activation="tanh",                 # Tanh activation
    dropout_rate=0.2,                  # 20% dropout for regularization
    learning_rate=1e-3,                # Learning rate
    weight_decay=1e-4,                 # L2 regularization
    batch_size=64,                     # Batch size
    max_epochs=100,                    # Training epochs
    validation_split=0.2,              # 20% validation split
    standardize=True,                  # Feature standardization
    random_state=42,                   # Reproducibility
    trainer_kwargs={"accelerator": "gpu", "devices": 1}  # GPU training
)
```

### Integration with Scikit-learn Pipelines

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('ncdr', NCDR(latent_dim=5, max_epochs=50, standardize=False))
])

# Split data
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

# Fit pipeline and transform
X_train_reduced = pipeline.fit_transform(X_train)
X_test_reduced = pipeline.transform(X_test)
```

### Dimensionality Reduction Workflow

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

# Load iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Reduce to 2D for visualization
ncdr = NCDR(latent_dim=2, max_epochs=100, random_state=42)
X_2d = ncdr.fit_transform(X)

# Plot results
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.scatter(X_2d[:, 0], X_2d[:, 1], c=y, cmap='viridis')
plt.title('NCDR: Iris Dataset (2D)')
plt.xlabel('Component 1')
plt.ylabel('Component 2')

# Compare reconstruction quality
X_reconstructed = ncdr.predict(X)
mse_per_feature = np.mean((X - X_reconstructed) ** 2, axis=0)

plt.subplot(1, 2, 2)
plt.bar(range(len(mse_per_feature)), mse_per_feature)
plt.title('Reconstruction Error by Feature')
plt.xlabel('Feature Index')
plt.ylabel('MSE')

plt.tight_layout()
plt.show()
```

## API Reference

### NCDR Class

#### Parameters

- **hidden_dims** (list of int, default=[64, 32]): Hidden layer dimensions for encoder
- **latent_dim** (int, default=10): Dimension of latent space
- **learning_rate** (float, default=1e-3): Learning rate for optimization
- **activation** (str, default='relu'): Activation function ('relu', 'tanh', 'sigmoid', 'leaky_relu', 'elu', 'gelu')
- **dropout_rate** (float, default=0.0): Dropout rate for regularization
- **weight_decay** (float, default=0.0): L2 regularization weight decay
- **batch_size** (int, default=32): Training batch size
- **max_epochs** (int, default=100): Maximum training epochs
- **validation_split** (float, default=0.2): Fraction of data for validation
- **standardize** (bool, default=True): Whether to standardize features
- **random_state** (int, optional): Random seed for reproducibility
- **trainer_kwargs** (dict, optional): Additional PyTorch Lightning Trainer arguments

#### Methods

- **fit(X, y=None)**: Train the autoencoder on data X
- **transform(X)**: Transform data to latent representation
- **fit_transform(X, y=None)**: Fit and transform in one step
- **inverse_transform(X)**: Reconstruct data from latent representation
- **predict(X)**: Reconstruct input data (alias for encode→decode)
- **score(X, y=None)**: Return negative reconstruction MSE

