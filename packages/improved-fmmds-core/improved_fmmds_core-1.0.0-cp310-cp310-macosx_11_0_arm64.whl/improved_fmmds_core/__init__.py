"""
Improved FMMD-S Core Algorithm Package

A clean, focused implementation of the Fair Max-Min Diversification algorithm
with significant performance improvements over the original implementation.

Key Features:
- Incremental graph updates to avoid redundant computations
- Working data persistence for efficient threshold relaxation
- Parallel distance computations using Cython
- Clean functional and class-based interfaces
- Comprehensive constraint handling

Usage:
    # Simple functional interface
    from improved_fmmds_core import solve_fmmd
    
    solution, diversity, timing = solve_fmmd(
        features=features,
        ids=ids,
        groups=groups,
        k=10,
        constraints=constraints
    )
    
    # Or class-based interface
    from improved_fmmds_core import FMMDSolver
    
    solver = FMMDSolver(k=10, constraints=constraints)
    result = solver.solve(features, ids, groups)
"""

from .algorithms import FMMDResult, FMMDSolver, fmmd, solve_fmmd
from .constraints import (
    ConstraintGenerator,
    Constraints,
    ConstraintStrategy,
    ManualConfig,
    ProportionalConfig,
    UniformBalancedConfig,
    proportional_constraints,
    uniform_balanced_constraints,
    validate_k_feasibility,
)

__version__ = "1.0.0"
__author__ = "Ananth Mahadevan"
__email__ = "ananth.mahadevan@helsinki.fi"

__all__ = [
    # Core algorithm
    "FMMDSolver",
    "FMMDResult", 
    "solve_fmmd",
    "fmmd",
    
    # Constraints
    "Constraints",
    "ConstraintStrategy",
    "ConstraintGenerator",
    "UniformBalancedConfig",
    "ProportionalConfig", 
    "ManualConfig",
    "uniform_balanced_constraints",
    "proportional_constraints",
    "validate_k_feasibility",
]
