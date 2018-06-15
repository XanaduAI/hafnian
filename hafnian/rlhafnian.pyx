# Copyright 2018 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
cimport cython

import numpy as np
cimport numpy as np
from scipy.linalg.cython_lapack cimport dgees


cdef extern from "../src/rlhafnian.h":
    double hafnian (double mat[], int n)
    double hafnian_loops(double *mat, int n)


@cython.boundscheck(False)
@cython.wraparound(False)
cdef public void evals(double *z, double complex *vals, int n,
                       double *wr, double *wi, int lwork, double *work) nogil:

    cdef int lda = n, ldvs = n, sdim = 0, info, i

    dgees('N', 'N', NULL, &n, &z[0], &lda, &sdim,
        &wr[0], &wi[0], NULL, &ldvs, &work[0], &lwork, NULL, &info)

    for i in range(n):
        vals[i] = wr[i] + 1j*wi[i]


@cython.embedsignature(True)
@cython.boundscheck(False)
@cython.wraparound(False)
def haf_real(double[:, :] A, bint loop=False):
    """Returns the hafnian of a real matrix A via the C hafnian library.

    Args:
        A (array): a np.float64, square, symmetric array of even dimensions.
        loop (bool): If ``True``, the loop hafnian is returned. Default false.

    Returns:
        np.float64: the hafnian of matrix A
    """
    # Exposes a c function to python
    n = A.shape[0]
    if loop:
        return hafnian_loops(&A[0,0], n)
    return hafnian(&A[0,0], n)
