"""Brisket: Fast Cython-powered one-hot encoding for DNA sequences."""

try:
    from importlib.metadata import version
    __version__ = version("brisket")
except ImportError:
    # Fallback for development
    __version__ = "0.0.0"

# Import the Cython extension function
try:
    from brisket.brisket import encode_seq
except ImportError:
    # Fallback for development when extension isn't built
    def encode_seq(seq: str):
        """Fallback implementation when Cython extension is not available."""
        raise ImportError(
            "Cython extension not available. Please build the package with 'poetry build' "
            "or install in development mode with 'poetry install'."
        )

__all__ = ["encode_seq", "__version__"]