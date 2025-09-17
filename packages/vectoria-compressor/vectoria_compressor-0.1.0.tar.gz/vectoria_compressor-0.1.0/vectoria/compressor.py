"""
Vectoria Compressor: An adaptive vector quantization compressor.

This module contains the main VectorCompressor class and all related
functions for encoding and decoding bitstreams.
"""

__author__ = "John Drossos"
__email__ = "john@johndrossos.com"
__version__ = "0.1.0"

import random
import math
from collections import Counter, defaultdict
from typing import List, Tuple, Dict, Any
import sys
sys.stdout.reconfigure(encoding='utf-8')


# ==========================
# Pre-processing & Utilities
# ==========================

# --- Symbol Constants for Modeling ---
R0 = -2   # run-of-zero marker
ESC = -1  # literal/escape marker

# --- Rice utilities (for RLE payload) ---
def _rice_cost(x: int, k: int) -> int:
    """Calculates the number of bits to store x using Rice code with parameter k."""
    q = x >> k
    return (q + 1) + k  # q ones + 0 separator + k remainder bits

def _choose_rice_k(lengths: List[int], max_k: int = 5) -> int:
    """Finds the optimal Rice parameter k for a list of integers."""
    if not lengths:
        return 0
    best_k, best_cost = 0, float('inf')
    for k in range(max_k + 1):
        cost = sum(_rice_cost(L, k) for L in lengths)
        if cost < best_cost:
            best_k, best_cost = k, cost
    return best_k

# --- RLE(0) over MTF ranks ---
def _rle0_over_ranks(ranks: List[int], min_run: int = 2):
    """
    Converts a rank stream into a token stream with R0 markers for zero-runs
    and a separate list of the lengths of those runs.
    """
    tokens = []
    run_lengths = []
    i, n = 0, len(ranks)
    while i < n:
        if ranks[i] == 0:
            j = i
            while j < n and ranks[j] == 0:
                j += 1
            run = j - i
            if run >= min_run:
                tokens.append(R0)
                run_lengths.append(run)
            else: # Keep short runs as explicit zeros
                tokens.extend([0] * run)
            i = j
        else:
            tokens.append(ranks[i])
            i += 1
    return tokens, run_lengths

def _mtf_encode(indices: List[int], K: int) -> List[int]:
    """Encodes a list of indices using Move-to-Front transform."""
    mtf = list(range(K))
    out = []
    for x in indices:
        j = mtf.index(x)
        out.append(j)
        mtf.pop(j); mtf.insert(0, x)
    return out

def _huffman_code_lengths(freqs: Dict[Any, int]) -> Dict[Any, int]:
    """Return canonical Huffman *lengths* (not bit patterns)."""
    if not freqs: return {}
    items = [(w, s) for s, w in freqs.items() if w > 0]
    if not items: return {}
    if len(items) == 1: return {items[0][1]: 1}
    import heapq
    from itertools import count
    tiebreak = count()
    heap = []
    for w, s in items: heapq.heappush(heap, (w, next(tiebreak), {s: 0}))
    while len(heap) > 1:
        w1, _, m1 = heapq.heappop(heap)
        w2, _, m2 = heapq.heappop(heap)
        merged = {k: d + 1 for k, d in m1.items()}
        merged.update({k: d + 1 for k, d in m2.items()})
        heapq.heappush(heap, (w1 + w2, next(tiebreak), merged))
    return heap[0][2]

# ==========================
# Vector VQ + Entropy Model
# ==========================

class VectorCompressor:
    """
    Vector Quantization with an adaptive entropy model.
    It now compares a contextual model with an MTF+RLE(0)+Rice model.
    """
    def __init__(self, vector_size: int = 2, max_codebook_size: int = 16):
        self.vector_size = vector_size
        self.max_codebook_size = max_codebook_size
        self.best_k = None; self.codebook = []; self.vector_to_index_map = {}
        self.model_type = 'zeroth_order_mtf_rle'; self.token_model_info = {}

    def _create_vectors(self, bitstream: str) -> Tuple[List[Tuple[str, ...]], str]:
        chunk_size = 3
        triplets = [bitstream[i:i+chunk_size] for i in range(0, len(bitstream), chunk_size)]
        remainder = ""
        if triplets and len(triplets[-1]) < chunk_size:
            remainder = triplets.pop()
        num_vectors = len(triplets) // self.vector_size
        vectors = [tuple(triplets[i*self.vector_size : (i+1)*self.vector_size]) for i in range(num_vectors)]
        remainder = "".join(triplets[num_vectors*self.vector_size:]) + remainder
        return vectors, remainder

    def _build_token_stream(self, vectors: List[Tuple[str,...]], codebook: List[Tuple[str,...]]):
        v2i = {v: i for i, v in enumerate(codebook)}
        return [(v2i.get(vec, ESC)) for vec in vectors]

    def _estimate_zeroth_order_bits(self, tokens: List[int], K: int, num_vectors: int, remainder_bits: int):
        # Build MTF ranks for IDX tokens; keep literals as ESC
        idx_seq = [t for t in tokens if t != ESC]
        ranks = _mtf_encode(idx_seq, K) if K > 0 else []
        
        # Align ranks back to the token timeline
        ranks_iter = iter(ranks)
        modeled = [next(ranks_iter) if t != ESC else ESC for t in tokens]

        # --- RLE(0) over ranks (threshold >=2) ---
        idx_only_ranks = [r for r in modeled if r != ESC]
        rle_tokens, run_lengths = _rle0_over_ranks(idx_only_ranks, min_run=2)

        freqs = Counter(rle_tokens)
        esc_count = modeled.count(ESC)
        if esc_count > 0:
            freqs[ESC] = esc_count
        
        lengths = _huffman_code_lengths(freqs)

        token_bits = sum(count * lengths.get(sym, 0) for sym, count in freqs.items())
        
        # Payload bits:
        #  - literals: raw V*3 bits per ESC
        #  - R0 runs: Rice-coded lengths with globally optimal k
        literal_bits = freqs.get(ESC, 0) * (self.vector_size * 3)
        if run_lengths:
            k_opt = _choose_rice_k(run_lengths, max_k=5)
            rle_payload_bits = sum(_rice_cost(L, k_opt) for L in run_lengths)
            rle_header_bits = 3  # Header bits to store k
        else:
            k_opt, rle_payload_bits, rle_header_bits = 0, 0, 1

        codebook_bits = K * (self.vector_size * 3)

        huff_header_bits = (8 + len(lengths) * 8) if lengths else 0
        
        total_bits = (token_bits + literal_bits + rle_payload_bits +
                      codebook_bits + huff_header_bits + remainder_bits + rle_header_bits)


        fixed_header_bits = 5 + 8 + 8 + 32 + 8
        total_bits += fixed_header_bits
        pad_bits = (8 - (total_bits % 8)) % 8
        total_bits += pad_bits

        return {
            'model_type': 'zeroth_order_mtf_rle', 'total_bits': total_bits, 'lengths': lengths,
            'token_bits': token_bits, 'literal_bits': literal_bits, 'codebook_bits': codebook_bits,
            'huff_header_bits': huff_header_bits, 'remainder_bits': remainder_bits,
            'fixed_header_bits': fixed_header_bits, 'pad_bits': pad_bits,
            'rle': {'k': k_opt, 'runs': len(run_lengths), 'payload_bits': rle_payload_bits, 'header_bits': rle_header_bits}
        }

    def _estimate_contextual_bits(self, tokens: List[int], K: int, num_vectors: int, remainder_bits: int):
        if not tokens: return {'total_bits': float('inf')}
        
        START_CONTEXT, DEFAULT_CONTEXT = -3, 'DEFAULT'
        context_freqs = defaultdict(Counter)
        prev_token = START_CONTEXT
        for token in tokens:
            context_freqs[prev_token][token] += 1
            prev_token = token

        merged_freqs = defaultdict(Counter)
        min_support = 3
        for ctx, freqs in context_freqs.items():
            if sum(freqs.values()) < min_support and ctx != START_CONTEXT:
                merged_freqs[DEFAULT_CONTEXT].update(freqs)
            else:
                merged_freqs[ctx].update(freqs)
        
        context_lengths = {ctx: _huffman_code_lengths(freqs) for ctx, freqs in merged_freqs.items()}
        
        huff_header_bits = 8 + sum((8 + len(lengths) * 8) if lengths else 0 for lengths in context_lengths.values())

        token_bits = 0
        prev_token = START_CONTEXT
        for token in tokens:
            current_ctx = prev_token
            if current_ctx not in merged_freqs and current_ctx != START_CONTEXT:
                merged_ctx = DEFAULT_CONTEXT
            else:
                merged_ctx = current_ctx
            
            if token not in context_lengths[merged_ctx]:
                 token_bits += context_lengths[DEFAULT_CONTEXT][token]
            else:
                 token_bits += context_lengths[merged_ctx][token]
            prev_token = token
            
        literal_bits = tokens.count(ESC) * (self.vector_size * 3)
        codebook_bits = K * (self.vector_size * 3)
        
        total_bits = token_bits + literal_bits + codebook_bits + huff_header_bits + remainder_bits
        fixed_header_bits = 5 + 8 + 8 + 32 + 8
        total_bits += fixed_header_bits
        pad_bits = (8 - (total_bits % 8)) % 8
        total_bits += pad_bits

        return {
            'model_type': 'contextual', 'total_bits': total_bits, 'lengths': context_lengths,
            'token_bits': token_bits, 'literal_bits': literal_bits, 'codebook_bits': codebook_bits,
            'huff_header_bits': huff_header_bits, 'remainder_bits': remainder_bits,
            'fixed_header_bits': fixed_header_bits, 'pad_bits': pad_bits,
        }


    def _select_best_model_and_K(self, vectors: List[Tuple[str,...]], remainder: str):
        if not vectors: 
            base_bits, fixed_header_bits = len(remainder), 5 + 8 + 8 + 32 + 8
            total_bits = base_bits + fixed_header_bits
            pad_bits = (8 - (total_bits % 8)) % 8
            return {'K': 0, 'codebook': [], 'total_bits': total_bits + pad_bits, 'model_type': 'zeroth_order_mtf_rle', 'lengths': {}, 'token_bits': 0, 'literal_bits': 0, 'codebook_bits': 0, 'huff_header_bits': 0, 'remainder_bits': len(remainder), 'fixed_header_bits': fixed_header_bits, 'pad_bits': pad_bits}

        num_vectors = len(vectors)
        remainder_bits = len(remainder)
        literal_bits_k0 = num_vectors * self.vector_size * 3
        
        fixed_header_bits = 5 + 8 + 8 + 32 + 8
        total_k0_bits = literal_bits_k0 + remainder_bits + fixed_header_bits
        pad_bits_k0 = (8 - (total_k0_bits % 8)) % 8

        best_overall = {
            'total_bits': total_k0_bits + pad_bits_k0, 'K': 0, 'codebook': [],
            'model_type': 'all_literals', 'token_bits': 0, 'literal_bits': literal_bits_k0,
            'codebook_bits': 0, 'huff_header_bits': 0, 'remainder_bits': remainder_bits,
            'fixed_header_bits': fixed_header_bits, 'pad_bits': pad_bits_k0
        }
        

        vector_freqs = Counter(vectors)
        upper_k = min(self.max_codebook_size, len(vector_freqs))

        for K in range(1, upper_k + 1):
            codebook = [v for v, _ in vector_freqs.most_common(K)]
            tokens = self._build_token_stream(vectors, codebook)

            zeroth_model = self._estimate_zeroth_order_bits(tokens, K, num_vectors, remainder_bits)
            context_model = self._estimate_contextual_bits(tokens, K, num_vectors, remainder_bits)

            

            best_for_k = min(zeroth_model, context_model, key=lambda x: x['total_bits'])

            if best_for_k['total_bits'] < best_overall['total_bits']:
                best_overall = best_for_k
                best_overall['K'] = K
                best_overall['codebook'] = codebook
        return best_overall

    

    def encode(self, bitstream: str) -> Dict[str, Any]:
        vectors, remainder = self._create_vectors(bitstream)
        best_model = self._select_best_model_and_K(vectors, remainder)

        self.best_k = best_model['K']
        self.codebook = best_model.get('codebook', [])
        self.model_type = best_model['model_type']

        accounting_keys = [k for k in best_model if '_bits' in k or k == 'total_bits']
        bit_accounting = {k: best_model[k] for k in accounting_keys}
        if 'rle' in best_model:
            bit_accounting['rle'] = best_model['rle']

        
        if self.codebook:
            v2i = {v: i for i, v in enumerate(self.codebook)}
            # First, determine if each vector is an index or an escape
            token_values = [v2i.get(vec, ESC) for vec in vectors]
            # Then, build the final list
            encoded_data = [
                ('literal', vectors[i]) if val == ESC else ('index', val)
                for i, val in enumerate(token_values)
            ]
        else:
            # If there's no codebook, all vectors must be literals.
            encoded_data = [('literal', vec) for vec in vectors]
       

        return {'data': encoded_data, 'codebook': self.codebook, 'remainder': remainder,
                'model': {'K': self.best_k, 'model_type': self.model_type,
                          'vector_size': self.vector_size, # <-- ADD THIS LINE
                          'bit_accounting': bit_accounting}}
    def decode(self, compressed_form: Dict[str, Any]) -> str:
        decoded_triplets = []
        for type, value in compressed_form['data']:
            if type == 'index':
                decoded_triplets.extend(compressed_form['codebook'][value])
            else:
                decoded_triplets.extend(value)
        return "".join(decoded_triplets) + compressed_form['remainder']

# --- Utility Class for Generating Test Data ---
class BitStreamGenerator:
    def __init__(self, randomness_percentage: float, length: int = 1000):
        self.randomness, self.length = randomness_percentage / 100.0, length
    def generate(self) -> str:
        return "".join(('1' if str(i%2)=='0' else '0') if random.random()<self.randomness else str(i%2) for i in range(self.length))

# ======== Main Execution ========
if __name__ == "__main__":
    generator = BitStreamGenerator(randomness_percentage=5, length=10000)
    original_stream = generator.generate()

    print("--- Original Data ---")
    print(f"Stream Length: {len(original_stream)} bits ({len(original_stream)/8:.1f} bytes)")
    print(f"Preview: {original_stream[:80]}...")
    print("-" * 50)

    compressor = VectorCompressor(vector_size=2, max_codebook_size=16)
    compressed_form = compressor.encode(original_stream)
    model_info = compressed_form['model']
    ba = model_info['bit_accounting']

    print("--- Vector Compression Results ---")
    print(f"🏆 Best Model Found: {model_info['model_type'].upper()}")
    print(f"Chosen K (codebook size): {model_info['K']}")

    print("\n--- Bit Accounting (Byte-Perfect Estimate) ---")
    keys_to_print = ['token_bits', 'literal_bits', 'codebook_bits', 'huff_header_bits', 'remainder_bits', 'fixed_header_bits', 'pad_bits']
    for k in keys_to_print:
        if k in ba: print(f"{k:>20}: {ba[k]}")
    
    if 'rle' in ba:
        rle = ba['rle']
        print(f"{'rle_payload_bits':>20}: {rle['payload_bits']} ({rle['runs']} runs, k={rle['k']})")
        print(f"{'rle_header_bits':>20}: {rle['header_bits']}")

    total_bits, total_bytes = ba['total_bits'], math.ceil(ba['total_bits'] / 8)
    print("-" * 20)
    print(f"{'Total Bits':>20}: {total_bits}")
    print(f"{'Total Bytes':>20}: {total_bytes}")
    
    ratio = len(original_stream) / total_bits if total_bits > 0 else 0
    print(f"\nCompression Ratio: {ratio:.2f} : 1 (higher is better)")
    print(f"Space Saving: {100 * (1 - 1/ratio):.2f}%")

    reconstructed = compressor.decode(compressed_form)
    print("\n--- Decompression & Verification ---")
    print(f"Verification Successful: {reconstructed == original_stream} ✅")