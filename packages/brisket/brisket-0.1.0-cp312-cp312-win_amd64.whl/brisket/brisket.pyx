# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION

import numpy as np

cimport cython
cimport numpy as np


@cython.boundscheck(False)
@cython.wraparound(False)
def encode_seq(seq: str) -> np.ndarray:
    seq = seq.upper() # faster than checking lowercase in for loop, ~.3ms overhead

    cdef:
        int seq_len = len(seq)
        np.ndarray[np.uint8_t, ndim = 2] encoded = np.zeros((seq_len, 4), dtype = np.uint8)
        int i
        char base

    for i, base in enumerate(seq):
        if base == 'A':
            encoded[i, 0] = 1
        elif base == 'C':
            encoded[i, 1] = 1
        elif base == 'G':
            encoded[i, 2] = 1
        elif base == 'T':
            encoded[i, 3] = 1

    return encoded