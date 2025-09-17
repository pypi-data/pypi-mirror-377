# Vectoria 🗜️

[](https://pypi.org/project/vectoria/)
[](https://opensource.org/licenses/MIT)

**Vectoria** is a sophisticated, adaptive lossless data compressor written in Python. It intelligently analyzes input data and selects the optimal compression strategy from a suite of advanced techniques, ensuring high compression ratios for a variety of data patterns.

It was created by John Drossos ([john@johndrossos.com](mailto:john@johndrossos.com)).

## \#\# Support This Project

If you find Vectoria useful, please consider supporting its development. Every contribution is greatly appreciated\!

[**❤️ Donate via Stripe (pay as much as you want)**](https://buy.stripe.com/fZeeVA8dGfEc0XS4gi)

-----

## \#\# Key Features

  * **🧠 Adaptive Model Selection:** Vectoria doesn't use a single, fixed algorithm. It evaluates multiple configurations and two distinct entropy models to find the one that yields the smallest possible output size for your specific data.
  * **⚙️ Sophisticated Compression Pipeline:** It combines several proven techniques, including Vector Quantization (VQ), Move-to-Front (MTF), Run-Length Encoding (RLE), Rice coding, and Huffman coding.
  * **📊 Precise Cost Analysis:** The decision engine is powered by a byte-perfect cost model that accounts for all overhead, including data payloads, headers, codebooks, and even padding bits.
  * **🐍 Pure Python:** Fully implemented in Python with no external dependencies, making it easy to integrate and understand.

-----

## \#\# Installation

You can install Vectoria directly from PyPI:

```bash
pip install vectoria
```

-----

## \#\# Quick Start

Using Vectoria is straightforward. The `VectorCompressor` object handles everything.

```python
from vectoria import VectorCompressor

# 1. Your data (as a string of '0's and '1's)
# This example has a lot of repeating patterns that Vectoria can exploit.
bitstream = ("010111" * 50) + ("000001" * 50) + ("010111000001" * 20)

# 2. Initialize the compressor
# You can configure vector_size and max_codebook_size.
compressor = VectorCompressor(vector_size=2, max_codebook_size=16)

# 3. Encode the data
compressed_form = compressor.encode(bitstream)

# 4. Check the results
original_size = len(bitstream)
compressed_size = compressed_form['model']['bit_accounting']['total_bits']
ratio = original_size / compressed_size

print(f"Original size: {original_size} bits")
print(f"Compressed size: {compressed_size} bits")
print(f"🏆 Best model chosen: {compressed_form['model']['model_type']}")
print(f"Compression Ratio: {ratio:.2f} : 1")

# 5. Decode to get the original data back
reconstructed_data = compressor.decode(compressed_form)

assert bitstream == reconstructed_data
print("\nVerification successful: Data was perfectly reconstructed! ✅")

```

### \#\#\# Simple API

For even simpler usage, you can use the top-level `compress` and `decompress` functions, which handle the creation of the `VectorCompressor` object for you.

```python
import vectoria

# Your data
bitstream = ("010111" * 50) + ("000001" * 50)

# Compress in one line
# You can still pass configuration options as keyword arguments
compressed_data = vectoria.compress(bitstream, vector_size=2, max_codebook_size=8)

# Decompress in one line
reconstructed_data = vectoria.decompress(compressed_data)

assert bitstream == reconstructed_data
print("Simple API roundtrip successful! ✅")
```

-----

## \#\# How Vectoria Works

Vectoria's power comes from its ability to choose the best strategy. Think of it as a competition where different compression models compete to see which can represent your data in the fewest bits.

### \#\#\# Step 1: Vectorization

First, the input bitstream is chopped into small, 3-bit chunks (e.g., `'010'`). These chunks are then grouped into **vectors**. For a `vector_size` of 2, the stream `'010111001...'` becomes `('010', '111')`, `('001', ...)` and so on. This step turns the raw bitstream into a sequence of higher-level symbols.

### \#\#\# Step 2: The Competition

For a range of possible dictionary sizes (the "codebook"), Vectoria simulates two powerful compression models to see which performs better.

#### **Model A: The MTF-RLE Pipeline**

This model is designed to excel with data that has **locality of reference** (i.e., where the same vectors appear frequently in bursts).

`Tokens -> Move-to-Front (MTF) -> Run-Length Encode (RLE) of Zeros -> Huffman/Rice Coding`

1.  **Move-to-Front (MTF):** The sequence of vectors is transformed. When a vector is seen, it's replaced by its current position in a dynamic list and then moved to the front. Frequent vectors consistently get encoded as small numbers (like 0, 1, 2).
2.  **Run-Length Encoding (RLE):** Because MTF generates long runs of zeros for the most frequent vector, a specialized RLE process efficiently compresses these runs.
3.  **Entropy Coding:** The resulting symbols and run-lengths are then compressed using Huffman and Rice coding.

#### **Model B: The Contextual Model**

This model is designed to excel with data that has **strong local patterns**, where the next vector is highly predictable from the current vector.

`Tokens -> Context-based Huffman Coding`

1.  **Context Modeling:** It builds a statistical model where the probability of the next vector depends on the vector that came just before it. For example, it learns that the vector `('010', '111')` is very likely to be followed by `('000', '001')`.
2.  **Huffman Coding:** It uses a different Huffman table for each context, allowing for extremely tight compression when these local patterns are strong.

### \#\#\# Step 3: The Decision

Vectoria runs this competition for multiple codebook sizes (`K=1, 2, ... max_codebook_size`). Using its precise bit-accounting model, it calculates the exact final compressed size for every single configuration. Finally, it picks the **undisputed winner**—the combination of codebook size and model type that results in the absolute minimum number of bits—and uses that to perform the final encoding.

-----

## \#\# License

This project is licensed under the MIT License. See the `LICENSE` file for details.