# In tests/test_api.py

import vectoria

# A simple, predictable bitstream for testing
API_STREAM = "010111000101" * 30

def test_convenience_functions_roundtrip():
    """
    Tests that the top-level compress() and decompress()
    functions work together correctly.
    """
    compressed = vectoria.compress(API_STREAM)
    reconstructed = vectoria.decompress(compressed)
    assert API_STREAM == reconstructed

def test_convenience_compress_with_kwargs():
    """
    Tests that keyword arguments (kwargs) are correctly
    passed to the compressor via the convenience function.
    """
    custom_vector_size = 4
    compressed = vectoria.compress(
        API_STREAM,
        vector_size=custom_vector_size,
        max_codebook_size=8
    )

    # Verify that the setting was used by checking the output model info
    assert compressed['model']['vector_size'] == custom_vector_size
    
    # Also ensure the roundtrip still works
    reconstructed = vectoria.decompress(compressed)
    assert API_STREAM == reconstructed