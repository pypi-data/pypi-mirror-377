# Improved FMMD-S Core

A clean, focused implementation of the Improved FMMD-S algorithm for fair max-min diversification with significant performance improvements over the original implementation.

## Key Features

- **Incremental Graph Updates**: Avoids redundant distance computations by incrementally updating the coreset graph
- **Working Data Persistence**: Reuses intermediate computations when relaxing diversity thresholds
- **Parallel Computations**: Cython-compiled parallel distance computations and edge creation
- **Clean Interface**: Both functional and class-based APIs for easy integration
- **Flexible Constraints**: Support for uniform balanced, proportional, and manual constraint strategies
- **Comprehensive CLI**: Command-line interface with subcommand-based constraint strategies
- **Multiple Distance Metrics**: Support for L2 (Euclidean), L1 (Manhattan), and angular distance metrics
- **Detailed Metadata**: Rich timing and performance metadata for analysis

## Installation

### Prerequisites

- Python 3.8+
- Gurobi Optimizer (with academic license recommended for larger datasets)
- Cython (for parallel computations)

**Note for Mac users**: You need to have g++-13 installed via Homebrew and set the CXX environment variable before installing the library:

```bash
# Install g++-13 via Homebrew
brew install gcc@13

# Set CXX environment variable
export CXX=g++-13

# Then proceed with installation
pip install -e .
```

### Install from Source

```bash
git clone https://github.com/yourusername/improved-fmmds-core.git
cd improved-fmmds-core
pip install -e .
```

### Build Cython Extensions

The package includes Cython-compiled parallel utilities for significant performance improvements. If compilation fails, the package will fall back to pure Python implementations.

**Manual Building (if needed):**

If you encounter issues with automatic Cython compilation, you can build the extensions manually:

```bash
# Install build dependencies
pip install Cython numpy

# Build Cython extensions manually
python -c "
import numpy as np
from Cython.Build import cythonize
from setuptools import setup, Extension

ext_modules = [
    Extension(
        'improved_fmmds_core.parallel.cython_utils',
        sources=['improved_fmmds_core/parallel/cython_utils.pyx'],
        extra_compile_args=['-fopenmp', '-std=c++11', '-O3'],
        extra_link_args=['-fopenmp', '-std=c++11'],
        include_dirs=[np.get_include()]
    )
]

setup(
    ext_modules=cythonize(ext_modules, compiler_directives={'language_level': 3})
)
"
```
### Installation Troubleshooting

**Common Issues:**

1. **Gurobi License Issues**: Ensure you have a valid Gurobi license. Academic licenses are available for free.

2. **Cython Compilation Errors**: If Cython compilation fails:
   - Ensure you have a C++ compiler installed
   - On Mac: Install g++-13 via Homebrew and set `export CXX=g++-13`
   - On Linux: Install `build-essential` package
   - On Windows: Install Visual Studio Build Tools

3. **OpenMP Issues**: If you encounter OpenMP-related errors:
   - On Mac: `brew install libomp`
   - On Linux: `sudo apt-get install libomp-dev`
   - On Windows: OpenMP should be included with Visual Studio

### Development Installation

For development and testing:

```bash
git clone https://github.com/yourusername/improved-fmmds-core.git
cd improved-fmmds-core
pip install -e "."
```

## Quick Start

### Python API

#### Functional Interface

```python
import numpy as np
from improved_fmmds_core import solve_fmmd

# Generate sample data
np.random.seed(42)
features = np.random.random((1000, 50))  # 1000 items, 50 features
ids = np.arange(1000)
groups = np.random.randint(0, 5, 1000)  # 5 groups

# Define constraints (group_id: (lower_bound, upper_bound))
constraints = {
    0: (2, 5),  # Group 0: between 2 and 5 items
    1: (1, 3),  # Group 1: between 1 and 3 items
    2: (2, 4),  # Group 2: between 2 and 4 items
    3: (1, 2),  # Group 3: between 1 and 2 items
    4: (2, 6)   # Group 4: between 2 and 6 items
}

# Solve using functional interface
solution, diversity, metadata = solve_fmmd(
    features=features,
    ids=ids,
    groups=groups,
    k=10,
    constraints=constraints,
    parallel_dist_update=True,
    parallel_edge_creation=True,
    metric="l2",
    eps=0.1,
    time_limit=300
)

print(f"Solution: {solution}")
print(f"Diversity: {diversity:.6f}")
print(f"Runtime: {metadata['total_time']:.2f} seconds")
print(f"Iterations: {metadata['num_iterations']}")
```

#### Class-based Interface

```python
from improved_fmmds_core import FMMDSolver

# Create solver with comprehensive configuration
solver = FMMDSolver(
    k=10,
    constraints=constraints,
    eps=0.1,
    time_limit=300,
    parallel_dist_update=True,
    parallel_edge_creation=True,
    verbose=False,
    metric="l2"
)

# Solve and get detailed results
result = solver.solve(features, ids, groups)

print(f"Solution: {result.solution}")
print(f"Diversity: {result.diversity:.6f}")
print(f"Runtime: {result.runtime:.2f} seconds")
print(f"Metric: {result.metric}")
print(f"Metadata: {result.metadata}")
```

#### Using Constraint Generators

```python
from improved_fmmds_core import (
    ConstraintGenerator, 
    UniformBalancedConfig, 
    ProportionalConfig
)
import numpy as np

# Generate data
features = np.random.random((1000, 50))
ids = np.arange(1000)
groups = np.random.randint(0, 5, 1000)
unique_groups, group_counts = np.unique(groups, return_counts=True)

# Uniform balanced constraints
uniform_config = UniformBalancedConfig(minimum_total_samples=50)
constraints_obj, k = ConstraintGenerator.generate_constraints(
    uniform_config, unique_groups, group_counts
)
constraints = constraints_obj.constraints

# Proportional constraints
proportional_config = ProportionalConfig(k=100, alpha=0.2)
constraints_obj, k = ConstraintGenerator.generate_constraints(
    proportional_config, unique_groups, group_counts
)
constraints = constraints_obj.constraints
```

### Command Line Interface

The CLI uses subcommands for different constraint strategies:

```bash
# Uniform balanced sampling
fmmds-run --data dataset.npz uniform-sampling --minimum-samples 50

# Proportional sampling
fmmds-run --data dataset.npz proportional-sampling --k 50 --alpha 0.2

# Custom constraints from file
fmmds-run --data dataset.npz custom-constraints --constraints-file constraints.json --k 50

# With parallel processing and custom parameters
fmmds-run --data dataset.npz uniform-sampling --minimum-samples 100 \
    --parallel --eps 0.05 --time-limit 600 --metric l1 --output results.json
```

#### Data Format Requirements

The `--data` argument expects a `.npz` file with the following required keys:
- `features`: 2D numpy array (n × d) containing feature vectors
- `ids`: 1D numpy array (n) containing unique item identifiers  
- `groups`: 1D numpy array (n) containing group assignments

**Performance Recommendations:**
- Use contiguous arrays for optimal performance: `np.ascontiguousarray()`
- Ensure arrays are properly aligned and have consistent dtypes
- For large datasets, consider using float32 instead of float64 to reduce memory usage

**Example data preparation:**
```python
import numpy as np

# Prepare your data
features = np.ascontiguousarray(features, dtype=np.float32)
ids = np.ascontiguousarray(ids, dtype=np.int32)
groups = np.ascontiguousarray(groups, dtype=np.int32)

# Save to .npz file
np.savez('dataset.npz', features=features, ids=ids, groups=groups)
```

#### CLI Options

**Global Options:**
- `--data`: Path to .npz file containing features, ids, and groups arrays
- `--output`: Output file for results (default: results.json)
- `--eps`: Diversity relaxation factor (default: 0.1)
- `--time-limit`: Time limit for ILP solver in seconds (default: 300)
- `--metric`: Distance metric (l2, l1, angular) (default: l2)
- `--parallel`: Enable all parallel options
- `--parallel-dist-update`: Enable parallel distance updates
- `--parallel-edge-creation`: Enable parallel edge creation
- `--verbose`: Enable verbose ILP solver output
- `--quiet`: Suppress output except errors

**Subcommand-specific Options:**
- `uniform-sampling --minimum-samples`: Minimum total samples for uniform sampling
- `proportional-sampling --k`: Number of samples, `--alpha`: Tolerance parameter (default: 0.2)
- `custom-constraints --constraints-file`: Path to constraints JSON file, `--k`: Number of samples

## Constraint Strategies

The library provides three main constraint strategies, each with specific use cases:

### Uniform Balanced Sampling
Ensures roughly equal representation from each group, accounting for group size constraints. This strategy is ideal when you want fair representation across groups regardless of their original sizes.

```python
from improved_fmmds_core import UniformBalancedConfig, ConstraintGenerator
import numpy as np

# Example with group counts
unique_groups = np.array([0, 1, 2, 3, 4])
group_counts = np.array([100, 50, 200, 25, 75])  # Group sizes

config = UniformBalancedConfig(minimum_total_samples=50)
constraints_obj, k = ConstraintGenerator.generate_constraints(config, unique_groups, group_counts)
constraints = constraints_obj.constraints

print(f"Generated k={k} with uniform constraints:")
for group_id, (lb, ub) in constraints.items():
    print(f"  Group {group_id}: {lb}-{ub} samples")
```

### Proportional Sampling
Maintains proportional representation based on group sizes with a tolerance parameter. This strategy preserves the original group proportions while allowing some flexibility.

```python
from improved_fmmds_core import ProportionalConfig

config = ProportionalConfig(k=100, alpha=0.2)  # 20% tolerance
constraints_obj, k = ConstraintGenerator.generate_constraints(config, unique_groups, group_counts)
constraints = constraints_obj.constraints

print(f"Generated k={k} with proportional constraints:")
for group_id, (lb, ub) in constraints.items():
    proportion = group_counts[group_id] / group_counts.sum()
    print(f"  Group {group_id}: {lb}-{ub} samples (proportion: {proportion:.2f})")
```

### Manual Constraints
Specify exact constraints for each group. This provides maximum control over the sampling strategy.

```python
# Define constraints manually
constraints = {
    0: (5, 10),   # Group 0: 5-10 samples
    1: (2, 8),    # Group 1: 2-8 samples
    2: (3, 12),   # Group 2: 3-12 samples
    3: (1, 5),    # Group 3: 1-5 samples
    4: (4, 8)     # Group 4: 4-8 samples
}

# Validate feasibility
from improved_fmmds_core import Constraints, validate_k_feasibility
constraints_obj = Constraints(constraints)
k = 25  # Target total samples
validate_k_feasibility(k, constraints_obj)  # Raises error if not feasible
```

### Constraint Validation

The library includes comprehensive validation to ensure constraints are feasible:

```python
from improved_fmmds_core import Constraints

constraints_obj = Constraints(constraints)
print(f"Minimum possible samples: {constraints_obj.get_min_total()}")
print(f"Maximum possible samples: {constraints_obj.get_max_total()}")
print(f"Is k=25 feasible? {constraints_obj.is_k_feasible(25)}")
```

## Algorithm Overview

The FMMD-S algorithm consists of four main steps:

1. **Initial Greedy Solution**: Obtain a greedy solution with k items using the Gonzales algorithm
2. **Group-wise Coreset**: For each group, run the Gonzales algorithm to obtain a coreset and diversity threshold
3. **Coreset Graph**: Create a graph where edges represent distances below the diversity threshold
4. **ILP Solution**: Solve the Maximum Independent Set problem using Gurobi to find the final solution
5. **Threshold Relaxation**: If infeasible, decrease diversity threshold and repeat from step 2

## Performance Improvements

This implementation provides significant speedups over the original FMMD-S algorithm:

### Core Optimizations

- **13-200x speedup** depending on problem size and constraints
- **Incremental Graph Updates**: Avoids redundant distance computations by incrementally updating the coreset graph instead of rebuilding it
- **Working Data Persistence**: Reuses intermediate computations when relaxing diversity thresholds
- **Parallel Distance Computations**: Cython-compiled parallel distance updates using OpenMP
- **Parallel Edge Creation**: Cython-compiled parallel coreset graph edge creation

### Performance Features

- **Multiple Distance Metrics**: Optimized implementations for L2, L1, and angular distances
- **Memory-Efficient Operations**: Contiguous array operations and optimized data structures
- **Configurable Parallelism**: Fine-grained control over parallel operations
- **Rich Metadata**: Detailed timing information for performance analysis


## Data Format

The algorithm expects data in the following format:

- **features**: 2D numpy array (n × d) where each row is a feature vector
- **ids**: 1D numpy array (n) containing unique identifiers for each item
- **groups**: 1D numpy array (n) specifying group assignments
- **constraints**: Dictionary mapping group IDs to (lower_bound, upper_bound) tuples

### Loading Data

```python
import numpy as np

# From separate files
features = np.load('features.npy')
ids = np.load('ids.npy')
groups = np.load('groups.npy')

# From single .npz file
data = np.load('dataset.npz')
features = data['features']
ids = data['ids']
groups = data['groups']
```

## Distance Metrics

The algorithm supports three distance metrics:

- **L2 (Euclidean)**: `metric="l2"` (default)
- **L1 (Manhattan)**: `metric="l1"`
- **Angular**: `metric="angular"`

## Parallel Processing

Enable parallel processing for better performance on large datasets:

```python
# Enable all parallel options
solver = FMMDSolver(
    k=10,
    constraints=constraints,
    parallel_dist_update=True,
    parallel_edge_creation=True
)

# Or via CLI
fmmds-run --data dataset.npz uniform-sampling --minimum-samples 50 --parallel
```

## Examples

The package includes comprehensive examples in the `examples/` directory:

- `basic_example.py`: Demonstrates all three constraint strategies with synthetic data
- Shows both functional and class-based interfaces
- Includes result saving and metadata analysis

Run the examples:

```bash
cd examples
python basic_example.py
```

## Requirements

### Core Dependencies

- **Python 3.8+**
- **NumPy >= 1.20.0**: Numerical computations
- **Gurobi Optimizer >= 9.0.0**: ILP solver (academic license recommended)
- **NetworkX >= 2.5**: Graph operations
- **tqdm >= 4.60.0**: Progress bars

### Build Dependencies

- **Cython >= 0.29.0**: For parallel computations
- **C++ Compiler**: For building Cython extensions
- **OpenMP**: For parallel processing (usually included with compiler)

### Optional Dependencies

- **Pandas**: For data manipulation (if needed for your workflow)
- **Matplotlib/Seaborn**: For visualization (if needed for analysis)

## License

MIT License

## Citation

If you use this implementation, please cite the original paper:

```bibtex
@inproceedings{wang2023max,
  title={Max-Min Diversification with Fairness Constraints: Exact and Approximation Algorithms},
  author={Wang, Y. and Mathioudakis, M. and Li, J. and Fabbri, F.},
  booktitle={Proceedings of the 2023 SIAM International Conference on Data Mining (SDM)},
  pages={91--99},
  year={2023},
  organization={Society for Industrial and Applied Mathematics}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For questions and support, please open an issue on GitHub.
