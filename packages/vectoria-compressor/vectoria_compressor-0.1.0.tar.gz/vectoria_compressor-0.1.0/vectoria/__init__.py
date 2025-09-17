# In vectoria/__init__.py

"""
Vectoria: An adaptive vector quantization compressor.

Made by John Drossos <john@johndrossos.com>
"""

__author__ = "John Drossos"
__email__ = "john@johndrossos.com"
__version__ = "0.1.0"

from .compressor import VectorCompressor

# --- New Convenience Functions ---

def compress(bitstream: str, **kwargs) -> dict:
    """
    Compresses a bitstream using the Vectoria algorithm.

    Args:
        bitstream (str): A string of '0's and '1's to compress.
        **kwargs: Optional keyword arguments for the VectorCompressor,
                  e.g., vector_size=2, max_codebook_size=16.

    Returns:
        dict: The compressed data structure.
    """
    compressor = VectorCompressor(**kwargs)
    return compressor.encode(bitstream)

def decompress(compressed_form: dict) -> str:
    """
    Decompresses a Vectoria data structure back to a bitstream.

    Args:
        compressed_form (dict): The dictionary returned by the compress function.

    Returns:
        str: The original bitstream.
    """
    # A new compressor instance is fine since all state is in the compressed_form
    compressor = VectorCompressor()
    return compressor.decode(compressed_form)