"""
Example script demonstrating NCDR usage.

This script shows how to use the NCDR autoencoder for dimensionality reduction
and reconstruction on sample datasets.
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_iris, make_classification
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

from encdr import ENCDR


def basic_example():
    """Basic ENCDR usage example."""
    print("=== Basic ENCDR Example ===")

    # Generate sample data
    X, y = make_classification(
        n_samples=500, n_features=20, n_informative=15, random_state=42
    )
    print(f"Generated dataset: {X.shape[0]} samples, {X.shape[1]} features")

    # Create and train ENCDR
    encdr = ENCDR(
        hidden_dims=[32, 16],
        latent_dim=5,
        max_epochs=50,
        random_state=42,
        trainer_kwargs={"enable_progress_bar": True},
    )

    # Fit and transform
    X_reduced = encdr.fit_transform(X)
    print(f"Reduced to {X_reduced.shape[1]} dimensions")

    # Reconstruct data
    X_reconstructed = encdr.predict(X)
    mse = np.mean((X - X_reconstructed) ** 2)
    print(f"Reconstruction MSE: {mse:.4f}")

    # Score (negative MSE)
    score = encdr.score(X)
    print(f"ENCDR Score: {score:.4f}")
    print()


def iris_visualization():
    """Visualize iris dataset reduction to 2D."""
    print("=== Iris Dataset Visualization ===")

    # Load iris dataset
    iris = load_iris()
    X, y = iris.data, iris.target
    print(f"Iris dataset: {X.shape[0]} samples, {X.shape[1]} features")

    # Compare ENCDR with PCA
    encdr = ENCDR(
        hidden_dims=[6, 4],
        latent_dim=2,
        max_epochs=100,
        random_state=42,
        trainer_kwargs={"enable_progress_bar": False},
    )

    pca = PCA(n_components=2, random_state=42)

    # Transform data
    X_encdr = encdr.fit_transform(X)
    X_pca = pca.fit_transform(X)

    # Calculate reconstruction errors
    X_encdr_reconstructed = encdr.predict(X)
    X_pca_reconstructed = pca.inverse_transform(X_pca)

    encdr_mse = np.mean((X - X_encdr_reconstructed) ** 2)
    pca_mse = np.mean((X - X_pca_reconstructed) ** 2)

    print(f"ENCDR reconstruction MSE: {encdr_mse:.4f}")
    print(f"PCA reconstruction MSE: {pca_mse:.4f}")

    # Plot comparison
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # ENCDR plot
    scatter1 = axes[0].scatter(X_encdr[:, 0], X_encdr[:, 1], c=y, cmap="viridis")
    axes[0].set_title(f"ENCDR (MSE: {encdr_mse:.4f})")
    axes[0].set_xlabel("Component 1")
    axes[0].set_ylabel("Component 2")

    # PCA plot
    scatter2 = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap="viridis")
    axes[1].set_title(f"PCA (MSE: {pca_mse:.4f})")
    axes[1].set_xlabel("Component 1")
    axes[1].set_ylabel("Component 2")

    # Add colorbar
    plt.colorbar(scatter1, ax=axes, label="Species")
    plt.tight_layout()
    plt.savefig("iris_comparison.png", dpi=150, bbox_inches="tight")
    print("Visualization saved as 'iris_comparison.png'")
    print()


def compression_example():
    """Demonstrate data compression capabilities."""
    print("=== Data Compression Example ===")

    # Generate larger dataset
    X, _ = make_classification(
        n_samples=1000, n_features=50, n_informative=30, random_state=42
    )

    # Original size
    original_size = X.size * X.itemsize
    print(f"Original data size: {original_size / 1024:.1f} KB")

    # Test different compression ratios
    latent_dims = [5, 10, 15, 20]

    for latent_dim in latent_dims:
        encdr = ENCDR(
            hidden_dims=[64, 32],
            latent_dim=latent_dim,
            max_epochs=30,
            random_state=42,
            trainer_kwargs={"enable_progress_bar": False},
        )

        # Compress data
        X_compressed = encdr.fit_transform(X)
        compressed_size = X_compressed.size * X_compressed.itemsize

        # Measure reconstruction quality
        X_reconstructed = encdr.predict(X)
        mse = np.mean((X - X_reconstructed) ** 2)

        # Calculate compression metrics
        compression_ratio = original_size / compressed_size
        variance_explained = 1 - mse / np.var(X)

        print(
            f"Latent dim {latent_dim:2d}: "
            f"Compression {compression_ratio:.1f}x, "
            f"Quality {variance_explained:.3f}, "
            f"MSE {mse:.4f}"
        )
    print()


def sklearn_pipeline_example():
    """Show integration with sklearn pipelines."""
    print("=== Scikit-learn Pipeline Example ===")

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    # Generate classification dataset
    X, y = make_classification(
        n_samples=800, n_features=30, n_informative=20, random_state=42
    )

    # Create pipeline with NCDR
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "encdr",
                ENCDR(
                    hidden_dims=[20, 10],
                    latent_dim=8,
                    max_epochs=30,
                    standardize=False,  # Already scaled by pipeline
                    random_state=42,
                    trainer_kwargs={"enable_progress_bar": False},
                ),
            ),
            ("classifier", RandomForestClassifier(random_state=42)),
        ]
    )

    # Cross-validation
    scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
    print(f"Cross-validation accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

    # Compare with PCA pipeline
    pca_pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=8, random_state=42)),
            ("classifier", RandomForestClassifier(random_state=42)),
        ]
    )

    pca_scores = cross_val_score(pca_pipeline, X, y, cv=5, scoring="accuracy")
    print(f"PCA pipeline accuracy:    {pca_scores.mean():.3f} ± {pca_scores.std():.3f}")
    print()


def main():
    """Run all examples."""
    print("NCDR Library Demonstration")
    print("=" * 40)

    try:
        basic_example()
        iris_visualization()
        compression_example()
        sklearn_pipeline_example()

        print("All examples completed successfully!")

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
