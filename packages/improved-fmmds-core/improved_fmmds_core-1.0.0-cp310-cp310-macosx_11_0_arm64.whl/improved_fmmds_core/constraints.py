import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Tuple

import numpy as np

logger = logging.getLogger(__name__)

class Constraints:
    """Pure constraints specification without k dependency"""
    def __init__(self, constraints: Dict[int, Tuple[int, int]]):
        self.constraints = constraints
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {str(k): [int(v[0]), int(v[1])] for k, v in self.constraints.items()}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Constraints':
        """Create from dictionary (for JSON deserialization)"""
        constraints = {int(k): tuple(v) for k, v in data.items()}
        return cls(constraints)
    
    def get_min_total(self) -> int:
        """Get minimum total samples across all groups"""
        return sum(lb for lb, ub in self.constraints.values())
    
    def get_max_total(self) -> int:
        """Get maximum total samples across all groups"""
        return sum(ub for lb, ub in self.constraints.values())
    
    def is_k_feasible(self, k: int) -> bool:
        """Check if k is feasible given these constraints"""
        return self.get_min_total() <= k <= self.get_max_total()

class ConstraintStrategy(Enum):
    """Enum for different constraint generation strategies"""
    UNIFORM_BALANCED = 'uniform_balanced'
    PROPORTIONAL = 'proportional'
    MANUAL = 'manual'

class StrategyConfig(ABC):
    """Abstract base class for strategy-specific configurations"""
    @abstractmethod
    def to_dict(self) -> Dict:
        pass
    
    @abstractmethod
    def get_strategy(self) -> ConstraintStrategy:
        pass

class UniformBalancedConfig(StrategyConfig):
    """Configuration for uniform balanced strategy"""
    def __init__(self, minimum_total_samples: int):
        self.minimum_total_samples = minimum_total_samples
    
    def to_dict(self) -> Dict:
        return {
            'strategy': self.get_strategy().value,
            'minimum_total_samples': int(self.minimum_total_samples)
        }
    
    def get_strategy(self) -> ConstraintStrategy:
        return ConstraintStrategy.UNIFORM_BALANCED
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UniformBalancedConfig':
        return cls(data['minimum_total_samples'])

class ProportionalConfig(StrategyConfig):
    """Configuration for proportional strategy"""
    def __init__(self, k: int, alpha: float = 0.2):
        self.k = k
        self.alpha = alpha
    
    def to_dict(self) -> Dict:
        return {
            'strategy': self.get_strategy().value,
            'k': int(self.k),
            'alpha': float(self.alpha)
        }
    
    def get_strategy(self) -> ConstraintStrategy:
        return ConstraintStrategy.PROPORTIONAL
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProportionalConfig':
        return cls(data['k'], data.get('alpha', 0.2))

class ManualConfig(StrategyConfig):
    """Configuration for manual strategy"""
    def __init__(self, constraints_file: str, k: int):
        self.constraints_file = constraints_file
        self.k = k
    
    def to_dict(self) -> Dict:
        return {
            'strategy': self.get_strategy().value,
            'constraints_file': self.constraints_file,
            'k': int(self.k)
        }
    
    def get_strategy(self) -> ConstraintStrategy:
        return ConstraintStrategy.MANUAL
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ManualConfig':
        return cls(data['constraints_file'], data['k'])

class ConstraintGenerator:
    """Generator for different types of constraints"""
    @staticmethod
    def generate_constraints(config: StrategyConfig, unique_groups: np.ndarray, group_counts: np.ndarray) -> Tuple[Constraints, int]:
        """Generate constraints based on the given configuration
        
        Returns:
            Tuple of (Constraints object, k value)
        """
        if isinstance(config, UniformBalancedConfig):
            constraints, k = uniform_balanced_constraints(unique_groups, group_counts, config.minimum_total_samples)
            constraints_obj = Constraints(constraints)
            validate_k_feasibility(k, constraints_obj)
            return constraints_obj, k
        elif isinstance(config, ProportionalConfig):
            constraints = proportional_constraints(unique_groups, group_counts, config.k, config.alpha)
            constraints_obj = Constraints(constraints)
            validate_k_feasibility(config.k, constraints_obj)
            return constraints_obj, config.k
        else:
            raise ValueError(f"Unsupported strategy config: {type(config)}")

def validate_k_feasibility(k: int, constraints: Constraints) -> None:
    """Validate that k is feasible given constraints
    
    Args:
        k: The k value to validate
        constraints: The constraints to check against
        
    Raises:
        ValueError: If k is not feasible
    """
    if not constraints.is_k_feasible(k):
        min_total = constraints.get_min_total()
        max_total = constraints.get_max_total()
        raise ValueError(
            f"k={k} is not feasible with given constraints. "
            f"Constraints require total samples between {min_total} and {max_total}"
        )

def find_num_samples_per_group(unique_groups: np.ndarray, group_counts: np.ndarray, num_samples: int) -> Tuple[int, int]:
    """Finds the number of samples from each group for uniform sampling. Accounts for group size variance."""
    def get_num_samples(groups: np.ndarray, counts: np.ndarray, num_samples_per_group: int) -> int:
        val1 = counts[counts <= num_samples_per_group].sum()
        val2 = num_samples_per_group * (counts > num_samples_per_group).sum()
        return val1 + val2
    num_samples_per_group = 0
    while True:
        total_number_of_samples = get_num_samples(unique_groups, group_counts, num_samples_per_group)
        if total_number_of_samples >= num_samples:
            break
        else:
            num_samples_per_group += 1
    return num_samples_per_group, int(total_number_of_samples)

def uniform_balanced_constraints(unique_groups: np.ndarray, group_counts: np.ndarray, num_samples: int) -> Tuple[Dict[int, Tuple[int, int]], int]:
    """Generate uniform balanced constraints as in the current implementation."""
    num_samples_per_group, total_number_of_samples = find_num_samples_per_group(unique_groups, group_counts, num_samples)
    logger.info(f"Total number of samples: {total_number_of_samples} and maximum {num_samples_per_group} from each group")
    constraints = {}
    for group, count in zip(unique_groups, group_counts):
        if count < num_samples_per_group:
            lb = count
            ub = count
        else:
            lb = num_samples_per_group
            ub = num_samples_per_group
        constraints[group] = (lb, ub)
    return constraints, total_number_of_samples

def proportional_constraints(unique_groups: np.ndarray, group_counts: np.ndarray, k: int, alpha: float = 0.2) -> Dict[int, Tuple[int, int]]:
    """Generate proportional constraints as per the referenced paper."""
    n = group_counts.sum()
    constraints = {}
    for group, size in zip(unique_groups, group_counts):
        lower = max(1, int(np.floor((1 - alpha) * k * size / n)))
        upper = int(np.ceil((1 + alpha) * k * size / n))
        upper = min(upper, size)  # Optionally cap upper at group size
        constraints[group] = (lower, upper)
    return constraints
