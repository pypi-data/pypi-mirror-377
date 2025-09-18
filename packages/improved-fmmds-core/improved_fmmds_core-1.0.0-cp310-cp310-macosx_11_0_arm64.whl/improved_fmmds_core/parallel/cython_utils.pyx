# distutils: language = c++
# distutils: extra_compile_args=-fopenmp -std=c++11 -std=gnu++11
# distutils: extra_link_args=-fopenmp

from cython.parallel cimport prange
cimport cython
from libc.math cimport sqrt, floor, acos
import numpy as np
cimport openmp
from libcpp.vector cimport vector

@cython.boundscheck(False)
@cython.wraparound(False)
cdef double l2_dist(double[::1] x, double[::1] y) nogil:
    cdef double total = 0
    cdef Py_ssize_t i
    cdef Py_ssize_t num = x.shape[0]
    cdef double tmp
    for i in range(num):
        tmp = x[i]-y[i]
        total += tmp*tmp
    return sqrt(total)

@cython.boundscheck(False)
@cython.wraparound(False)
cdef double l1_dist(double[::1] x, double[::1] y) nogil:
    cdef double total = 0
    cdef Py_ssize_t i
    cdef Py_ssize_t num = x.shape[0]
    for i in range(num):
        total += abs(x[i] - y[i])
    return total

@cython.boundscheck(False)
@cython.wraparound(False)
cdef double angular_dist(double[::1] x, double[::1] y) nogil:
    cdef double dot = 0
    cdef double norm_x = 0
    cdef double norm_y = 0
    cdef Py_ssize_t i
    cdef Py_ssize_t num = x.shape[0]
    for i in range(num):
        dot += x[i] * y[i]
        norm_x += x[i] * x[i]
        norm_y += y[i] * y[i]
    if norm_x == 0 or norm_y == 0:
        return acos(-1.0)
    cdef double cosine_sim = 0
    cosine_sim = dot / (sqrt(norm_x) * sqrt(norm_y))
    if cosine_sim > 1.0:
        cosine_sim = 1.0
    elif cosine_sim < -1.0:
        cosine_sim = -1.0
    return acos(cosine_sim)

# Helper to select distance function
cdef inline double dist_dispatch(double[::1] x, double[::1] y, str metric) nogil:
    if metric == "l2":
        return l2_dist(x, y)
    elif metric == "l1":
        return l1_dist(x, y)
    elif metric == "angular":
        return angular_dist(x, y)
    else:
        # fallback to l2
        return l2_dist(x, y)

ctypedef double (*dist_func_ptr)(double[::1], double[::1]) nogil

cdef dist_func_ptr get_dist_func(str metric) noexcept:
    if metric == "l2":
        return l2_dist
    elif metric == "l1":
        return l1_dist
    elif metric == "angular":
        return angular_dist
    else:
        return l2_dist

@cython.boundscheck(False)
@cython.wraparound(False)
def update_dists(double[::1] dists, double[:,::1] elements, double[::1] item, str metric="l2"):
    cdef dist_func_ptr dist_func = get_dist_func(metric)
    cdef Py_ssize_t num = elements.shape[0]
    cdef Py_ssize_t i
    cdef double tmp
    for i in prange(num, nogil=True):
        tmp = dist_func(elements[i], item)
        dists[i] = min(dists[i], tmp)

@cython.boundscheck(False)
@cython.wraparound(False)
def update_dists_sequential(double[::1] dists, double[:,::1] elements, double[::1] item, str metric="l2"):
    cdef dist_func_ptr dist_func = get_dist_func(metric)
    cdef Py_ssize_t num = elements.shape[0]
    cdef Py_ssize_t i
    cdef double tmp
    for i in range(num):
        tmp = dist_func(elements[i], item)
        dists[i] = min(dists[i], tmp)

@cython.boundscheck(False)
@cython.wraparound(False)
def pdist(double[:,::1] features, str metric="l2"):
    cdef dist_func_ptr dist_func = get_dist_func(metric)
    cdef Py_ssize_t N = features.shape[0]
    cdef Py_ssize_t M = N*(N-1)//2
    results = np.zeros(M)
    cdef Py_ssize_t i, j, idx
    cdef double[::1] results_view = results
    cdef double tmp = 0.0
    for idx in prange(M, nogil=True):
        i = N - 2 - <Py_ssize_t>(sqrt(-8*idx + 4*N*(N-1)-7)/2.0 - 0.5)
        j = idx + i + 1 - M + (N-i)*((N-i)-1)//2
        tmp = dist_func(features[i], features[j])
        results_view[idx] = tmp
    return results

@cython.boundscheck(False)
@cython.wraparound(False)
def cdist(double[:,::1] x, double[:,::1] y, str metric="l2"):
    cdef dist_func_ptr dist_func = get_dist_func(metric)
    cdef Py_ssize_t N = x.shape[0]
    cdef Py_ssize_t M = y.shape[0]
    results = np.zeros(N*M)
    cdef double[::1] results_view = results
    cdef Py_ssize_t i, j, idx
    cdef double tmp = 0.0
    for idx in prange(N*M, nogil=True):
        i = idx//M
        j = idx%M
        tmp = dist_func(x[i], y[j])
        results_view[idx] = tmp
    return results

@cython.boundscheck(False)
@cython.wraparound(False)
def pdist_serial(double[:,::1] features, str metric="l2"):
    """Serial version of pdist that computes pairwise distances between rows of features matrix.
    
    Args:
        features: Input feature matrix
        metric: Distance metric to use ("l2", "l1", or "angular")
        
    Returns:
        Array of pairwise distances in condensed form
    """
    cdef dist_func_ptr dist_func = get_dist_func(metric)
    cdef Py_ssize_t N = features.shape[0]
    cdef Py_ssize_t M = N*(N-1)//2
    results = np.zeros(M)
    cdef double[::1] results_view = results
    cdef Py_ssize_t i, j, idx
    cdef double tmp = 0.0
    for idx in range(M):
        i = N - 2 - <Py_ssize_t>(sqrt(-8*idx + 4*N*(N-1)-7)/2.0 - 0.5)
        j = idx + i + 1 - M + (N-i)*((N-i)-1)//2
        tmp = dist_func(features[i], features[j])
        results_view[idx] = tmp
    return results

@cython.boundscheck(False)
@cython.wraparound(False)
def cdist_serial(double[:,::1] x, double[:,::1] y, str metric="l2"):
    """Serial version of cdist that computes distances between each pair of rows from x and y.
    
    Args:
        x: First feature matrix
        y: Second feature matrix
        metric: Distance metric to use ("l2", "l1", or "angular")
        
    Returns:
        Array of distances between each pair of rows
    """
    cdef dist_func_ptr dist_func = get_dist_func(metric)
    cdef Py_ssize_t N = x.shape[0]
    cdef Py_ssize_t M = y.shape[0]
    results = np.zeros(N*M)
    cdef double[::1] results_view = results
    cdef Py_ssize_t i, j, idx
    cdef double tmp = 0.0
    for idx in range(N*M):
        i = idx//M
        j = idx%M
        tmp = dist_func(x[i], y[j])
        results_view[idx] = tmp
    return results

@cython.boundscheck(False)
@cython.wraparound(False)
def edges(double[:,::1] features, double diversity_threshold, str metric="l2"):
    """
    Returns the edges between items which have distance below a threshold.
    """
    cdef dist_func_ptr dist_func = get_dist_func(metric)
    cdef Py_ssize_t N = features.shape[0]
    cdef Py_ssize_t M = N*(N-1)//2
    cdef Py_ssize_t i, j, idx
    cdef vector[vector[Py_ssize_t]] us, vs
    cdef vector[vector[double]] dists
    cdef vector[Py_ssize_t] u, v
    cdef vector[double] dist
    cdef double tmp = 0.0
    cdef int tid, num_threads
    num_threads = openmp.omp_get_max_threads()
    us.resize(num_threads)
    vs.resize(num_threads)
    dists.resize(num_threads)
    for idx in prange(M, nogil=True):
        tid = openmp.omp_get_thread_num()
        i = N - 2 - <Py_ssize_t>(sqrt(-8*idx + 4*N*(N-1)-7)/2.0 - 0.5)
        j = idx + i + 1 - M + (N-i)*((N-i)-1)//2
        tmp = dist_func(features[i], features[j])
        if tmp < diversity_threshold:
            us[tid].push_back(i)
            vs[tid].push_back(j)
            dists[tid].push_back(tmp)
    for tid in range(num_threads):
        for _u in us[tid]:
            u.push_back(_u)
        for _v in vs[tid]:
            v.push_back(_v)
        for _dist in dists[tid]:
            dist.push_back(_dist)
    return u, v, dist

@cython.boundscheck(False)
@cython.wraparound(False)
def edges_sequential(double[:,::1] features, double diversity_threshold, str metric="l2"):
    """
    Returns the edges between items which have distance below a threshold.
    """
    cdef dist_func_ptr dist_func = get_dist_func(metric)
    cdef Py_ssize_t N = features.shape[0]
    cdef Py_ssize_t M = N*(N-1)//2
    cdef Py_ssize_t i, j, idx
    cdef vector[Py_ssize_t] u, v
    cdef vector[double] dist
    cdef double tmp = 0.0
    for idx in range(M):
        i = N - 2 - <Py_ssize_t>(sqrt(-8*idx + 4*N*(N-1)-7)/2.0 - 0.5)
        j = idx + i + 1 - M + (N-i)*((N-i)-1)//2
        tmp = dist_func(features[i], features[j])
        if tmp < diversity_threshold:
            u.push_back(i)
            v.push_back(j)
            dist.push_back(tmp)
    return u, v, dist

# Optional: Python-callable wrappers for testing
cpdef double l2_dist_py(double[::1] x, double[::1] y):
    return l2_dist(x, y)

cpdef double l1_dist_py(double[::1] x, double[::1] y):
    return l1_dist(x, y)

cpdef double angular_dist_py(double[::1] x, double[::1] y):
    return angular_dist(x, y)
