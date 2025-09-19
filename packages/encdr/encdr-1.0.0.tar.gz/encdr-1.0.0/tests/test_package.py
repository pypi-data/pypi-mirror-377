"""Tests for the NCDR package imports and public API."""

import pytest


def test_package_import():
    """Test that the package can be imported."""
    import encdr

    assert encdr is not None


def test_ncdr_class_import():
    """Test that NCDR class can be imported."""
    from encdr import NCDR

    assert NCDR is not None


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
    assert "NCDR" in encdr.__all__
    assert "AutoEncoder" in encdr.__all__


def test_main_function():
    """Test that main function exists."""
    from encdr import main

    assert callable(main)


def test_ncdr_instantiation():
    """Test that NCDR can be instantiated."""
    from encdr import NCDR

    ncdr = NCDR()
    assert ncdr is not None
    assert hasattr(ncdr, "fit")
    assert hasattr(ncdr, "transform")
    assert hasattr(ncdr, "predict")


def test_autoencoder_instantiation():
    """Test that AutoEncoder can be instantiated."""
    from encdr import AutoEncoder

    model = AutoEncoder(input_dim=10, hidden_dims=[8, 4], latent_dim=2)
    assert model is not None
    assert hasattr(model, "forward")
    assert hasattr(model, "encode")
    assert hasattr(model, "decode")
