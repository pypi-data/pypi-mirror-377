"""Type hints for the brisket Cython extension."""

import numpy as np

def encode_seq(seq: str) -> np.ndarray:
    """
    Convert a DNA sequence to one-hot encoding.
    
    Parameters
    ----------
    seq : str
        DNA sequence containing characters A, C, G, T (case insensitive)
        
    Returns
    -------
    np.ndarray
        2D numpy array of shape (seq_len, 4) with dtype uint8.
        Each row represents one nucleotide with one-hot encoding:
        - Column 0: A (Adenine)
        - Column 1: C (Cytosine) 
        - Column 2: G (Guanine)
        - Column 3: T (Thymine)
    """
    ...