"""
NCDR: Neural Component Dimensionality Reduction

A scikit-learn compatible autoencoder library for dimensionality reduction.
"""

from .autoencoder import AutoEncoder
from .ncdr import NCDR

__version__ = "0.1.0"
__all__ = ["NCDR", "AutoEncoder"]


def main() -> None:
    print("Hello from ncdr!")
