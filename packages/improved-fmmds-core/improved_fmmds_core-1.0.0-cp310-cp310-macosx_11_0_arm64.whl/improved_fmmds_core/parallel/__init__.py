"""
Parallel computation utilities for FMMD algorithm.

This module provides Cython-compiled parallel functions for distance computations 
and edge creation in the FMMD algorithm.
"""

from typing import List, Tuple

import numpy as np

# Import Cython-compiled functions
from .cython_utils import (
    angular_dist_py,
    cdist,
    cdist_serial,
    edges,
    edges_sequential,
    l1_dist_py,
    l2_dist_py,
    pdist,
    pdist_serial,
    update_dists,
    update_dists_sequential,
)


# Create a parallel_utils module for backward compatibility
class ParallelUtils:
    """Wrapper class for parallel utilities"""
    def __init__(self):
        self.update_dists = update_dists
        self.update_dists_sequential = update_dists_sequential
        self.pdist = pdist
        self.pdist_serial = pdist_serial
        self.cdist = cdist
        self.cdist_serial = cdist_serial
        self.edges = edges
        self.edges_sequential = edges_sequential
        self.l2_dist_py = l2_dist_py
        self.l1_dist_py = l1_dist_py
        self.angular_dist_py = angular_dist_py

parallel_utils = ParallelUtils()

__all__ = [
    'update_dists',
    'update_dists_sequential', 
    'pdist',
    'pdist_serial',
    'cdist',
    'cdist_serial',
    'edges',
    'edges_sequential',
    'l2_dist_py',
    'l1_dist_py',
    'angular_dist_py',
    'parallel_utils'
]
