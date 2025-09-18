"""
Clean CLI interface for the Improved FMMD-S Core algorithm.

This module provides a streamlined command-line interface for running
the FMMD algorithm with various constraint strategies.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from improved_fmmds_core import (
    ConstraintGenerator,
    Constraints,
    FMMDSolver,
    ProportionalConfig,
    UniformBalancedConfig,
    validate_k_feasibility,
)


def count_groups(groups: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Count occurrences of each group and return unique groups and counts as separate arrays."""
    unique_groups, counts = np.unique(groups, return_counts=True)
    return unique_groups, counts


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def load_data(data_path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load data from .npz file"""
    data = np.load(data_path, allow_pickle=True)
    features = data['features']
    ids = data['ids']
    groups = data['groups']
    features = np.ascontiguousarray(features)
    ids = np.ascontiguousarray(ids)
    groups = np.ascontiguousarray(groups)
    print(f"Loaded data: {features.shape[0]} items, {features.shape[1]} features, {len(np.unique(groups))} groups")
    return features, ids, groups

def load_constraints_from_file(constraints_path: Path) -> Dict[int, Tuple[int, int]]:
    """Load constraints from JSON file"""
    with open(constraints_path) as f:
        data = json.load(f)
    return {int(k): tuple(v) for k, v in data.items()}

def save_results(
    solution: set,
    diversity: float,
    metadata: Dict[str, float],
    constraints: Dict[int, Tuple[int, int]],
    k: int,
    constraint_config: Dict,
    output_path: Path,
):
    """Save results to JSON file"""
    results = {
        'solution': [int(x) for x in solution],
        'diversity': float(diversity),
        'metadata': metadata,
        'solution_size': int(len(solution)),
        'constraints': {str(group_id): [int(lb), int(ub)] for group_id, (lb, ub) in constraints.items()},
        'k': int(k),
        'constraint_config': constraint_config
    }
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_path}")

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Improved FMMD-S Core Algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Uniform balanced sampling
  fmmd-solve --data dataset.npz uniform-sampling --minimum-samples 50
  
  # Proportional sampling
  fmmd-solve --data dataset.npz proportional-sampling --k 50 --alpha 0.2
  
  # Custom constraints from file
  fmmd-solve --data dataset.npz custom-constraints --constraints-file constraints.json --k 50
        """
    )
    
    # Input data
    parser.add_argument('--data', type=Path, required=True,
                       help='Path to .npz file containing features, ids, and groups arrays')
    
    # Output
    parser.add_argument('--output', type=Path, default=Path('results.json'),
                       help='Output file for results (default: results.json)')
    
    # Algorithm parameters
    parser.add_argument('--eps', type=float, default=0.1,
                       help='Diversity relaxation factor (default: 0.1)')
    parser.add_argument('--time-limit', type=int, default=300,
                       help='Time limit for ILP solver in seconds (default: 300)')
    parser.add_argument('--metric', 
                       choices=['l2', 'l1', 'angular'],
                       default='l2',
                       help='Distance metric (default: l2)')
    
    # Performance options
    parser.add_argument('--parallel-dist-update', action='store_true',
                       help='Enable parallel distance updates')
    parser.add_argument('--parallel-edge-creation', action='store_true',
                       help='Enable parallel edge creation')
    parser.add_argument('--parallel', action='store_true',
                       help='Enable all parallel options')
    
    # Output options
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose ILP solver output')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress output except errors')
    
    # Create subparsers for constraint strategies
    subparsers = parser.add_subparsers(dest='constraints', help='Constraint generation strategies')
    
    # Uniform sampling subparser
    uniform_parser = subparsers.add_parser('uniform-sampling', help='Uniform balanced sampling strategy')
    uniform_parser.add_argument('--minimum-samples', type=int, required=True,
                               help='Minimum total samples for uniform sampling')
    
    # Proportional sampling subparser
    proportional_parser = subparsers.add_parser('proportional-sampling', help='Proportional sampling strategy')
    proportional_parser.add_argument('--k', type=int, required=True,
                                    help='Number of samples for proportional sampling')
    proportional_parser.add_argument('--alpha', type=float, default=0.2,
                                     help='Alpha parameter for proportional sampling (default: 0.2)')
    
    # Custom constraints subparser
    custom_parser = subparsers.add_parser('custom-constraints', help='Custom constraints strategy')
    custom_parser.add_argument('--constraints-file', type=Path, required=True,
                              help='Path to constraints JSON file for custom constraints')
    custom_parser.add_argument('--k', type=int, required=True,
                              help='Number of samples for custom constraints')
    return parser

def validate_args(args) -> None:
    """Validate command line arguments"""
    if not args.data.exists():
        raise FileNotFoundError(f"Data file not found: {args.data}")
    
    if args.constraints is None:
        raise ValueError("Must specify a constraint strategy: uniform-sampling, proportional-sampling, or custom-constraints")
    
    if args.constraints == 'custom-constraints' and not args.constraints_file.exists():
        raise FileNotFoundError(f"Constraints file not found: {args.constraints_file}")

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        setup_logging(args.verbose)
    
    try:
        # Validate arguments
        validate_args(args)
        
        # Load data
        print(f"Loading data from {args.data}")
        features, ids, groups = load_data(args.data)
        
        # Generate constraints based on strategy
        unique_groups, group_counts = count_groups(groups)
        constraint_config = {}
        
        if args.constraints == 'uniform-sampling':
            config = UniformBalancedConfig(args.minimum_samples)
            constraints_obj, k = ConstraintGenerator.generate_constraints(config, unique_groups, group_counts)
            constraints = constraints_obj.constraints
            constraint_config = {
                'strategy': 'uniform-sampling',
                'minimum_samples': args.minimum_samples
            }
            print(f"Generated uniform sampling constraints for k={k}")
            
        elif args.constraints == 'proportional-sampling':
            config = ProportionalConfig(args.k, args.alpha)
            constraints_obj, k = ConstraintGenerator.generate_constraints(config, unique_groups, group_counts)
            constraints = constraints_obj.constraints
            constraint_config = {
                'strategy': 'proportional-sampling',
                'k': args.k,
                'alpha': args.alpha
            }
            print(f"Generated proportional sampling constraints for k={k}")
            
        elif args.constraints == 'custom-constraints':
            constraints = load_constraints_from_file(args.constraints_file)
            k = args.k
            constraints_obj = Constraints(constraints)
            validate_k_feasibility(k, constraints_obj)
            constraint_config = {
                'strategy': 'custom-constraints',
                'constraints_file': str(args.constraints_file),
                'k': args.k
            }
            print(f"Loaded custom constraints for k={k}")
        
        # Print constraint summary
        print("\nConstraint Summary:")
        for group_id, (lb, ub) in constraints.items():
            # Find the count for this group
            group_idx = np.where(unique_groups == group_id)[0]
            group_size = group_counts[group_idx[0]] if len(group_idx) > 0 else 0
            print(f"  Group {group_id}: {lb}-{ub} samples (group size: {group_size})")
        
        print(f"\nTotal samples: {k}")
        print(f"Min possible: {sum(lb for lb, ub in constraints.values())}")
        print(f"Max possible: {sum(ub for lb, ub in constraints.values())}")
        
        # Setup parallel options
        parallel_dist_update = args.parallel_dist_update or args.parallel
        parallel_edge_creation = args.parallel_edge_creation or args.parallel
        
        # Create solver
        solver = FMMDSolver(
            k=k,
            constraints=constraints,
            eps=args.eps,
            time_limit=args.time_limit,
            parallel_dist_update=parallel_dist_update,
            parallel_edge_creation=parallel_edge_creation,
            verbose=args.verbose,
            metric=args.metric
        )
        
        # Solve
        print("\nSolving FMMD problem...")
        print(f"Parameters: eps={args.eps}, metric={args.metric}")
        if parallel_dist_update or parallel_edge_creation:
            print(f"Parallel options: dist_update={parallel_dist_update}, edge_creation={parallel_edge_creation}")
        
        result = solver.solve(features, ids, groups)
        
        # Print results
        print("\nSolution found!")
        print(f"  Solution size: {len(result.solution)}")
        print(f"  Diversity: {result.diversity:.6f}")
        print(f"  Runtime: {result.runtime:.2f} seconds")
         
        # Save results
        save_results(result.solution, result.diversity, result.metadata, constraints, k, constraint_config, args.output)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
