"""Tests for the ENCDR package imports and public API."""

import pytest


def test_package_import():
    """Test that the package can be imported."""
    import encdr

    assert encdr is not None


def test_ncdr_class_import():
    """Test that ENCDR class can be imported."""
    from encdr import ENCDR

    assert ENCDR is not None


def test_autoencoder_import():
    """Test that AutoEncoder class can be imported."""
    from encdr import AutoEncoder

    assert AutoEncoder is not None


def test_package_version():
    """Test that package version is accessible."""
    import encdr

    assert hasattr(encdr, "__version__")
    assert isinstance(encdr.__version__, str)


def test_package_all():
    """Test that __all__ is properly defined."""
    import encdr

    assert hasattr(encdr, "__all__")
    assert "ENCDR" in encdr.__all__
    assert "AutoEncoder" in encdr.__all__


def test_main_function():
    """Test that main function exists."""
    from encdr import main

    assert callable(main)


def test_ncdr_instantiation():
    """Test that ENCDR can be instantiated."""
    from encdr import ENCDR

    encdr = ENCDR()
    assert encdr is not None
    assert hasattr(encdr, "fit")
    assert hasattr(encdr, "transform")
    assert hasattr(encdr, "predict")


def test_autoencoder_instantiation():
    """Test that AutoEncoder can be instantiated."""
    from encdr import AutoEncoder

    model = AutoEncoder(input_dim=10, hidden_dims=[8, 4], latent_dim=2)
    assert model is not None
    assert hasattr(model, "forward")
    assert hasattr(model, "encode")
    assert hasattr(model, "decode")
