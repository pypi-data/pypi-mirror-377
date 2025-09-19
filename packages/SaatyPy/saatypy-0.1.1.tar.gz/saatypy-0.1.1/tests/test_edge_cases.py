"""Test suite for error conditions and edge cases."""
import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from saatypy.components.scale import SaatyScale
from saatypy.components.pairwise import PairwiseComparison
from saatypy.components.errors import (
    StructureError,
    NormalizationError,
)
from saatypy.components.math import normalize_vector_nonneg, normalize_columns_inplace
from saatypy.ahp import AHPBuilder
from saatypy.anp import ANPBuilder
from saatypy.components.math.limiters import PowerMethodLimiter, DampedPowerLimiter

def test_scale_edge_cases():
    """Test edge cases for Saaty scale."""
    # Zero and negative values
    assert not SaatyScale.is_valid(0.0)
    assert not SaatyScale.is_valid(-1.0)
    
    # Very small and large values
    assert SaatyScale.is_valid(1e-6)
    assert SaatyScale.is_valid(1e6)
    
    # Reciprocal of very small/large values
    assert SaatyScale.reciprocal(1e-6) == 1e6
    assert SaatyScale.reciprocal(1e6) == 1e-6

def test_pairwise_comparison_edge_cases():
    """Test edge cases in pairwise comparisons."""
    # 1x1 matrix
    pc = PairwiseComparison(["A"], np.array([[1.0]]))
    assert pc.priorities()[0] == 1.0
    
    # 2x2 matrix with extreme values
    M = np.array([[1.0, 1e6], [1e-6, 1.0]])
    pc = PairwiseComparison(["A", "B"], M)
    priorities = pc.priorities()
    assert priorities[0] > 0.99  # First alternative should dominate
    
    # Almost inconsistent reciprocal
    with pytest.raises(ValueError):
        M = np.array([[1.0, 2.0], [0.49, 1.0]])  # Should be 0.5
        PairwiseComparison(["A", "B"], M)

def test_normalization_edge_cases():
    """Test edge cases in normalization functions."""
    # Zero vector
    with pytest.raises(NormalizationError):
        normalize_vector_nonneg(np.zeros(3))
    
    # Vector with negative values
    with pytest.raises(NormalizationError):
        normalize_vector_nonneg(np.array([1.0, -1.0, 1.0]))
    
    # Very small values
    v = np.array([1e-15, 2e-15, 3e-15])
    norm_v = normalize_vector_nonneg(v)
    assert_array_almost_equal(norm_v, np.array([1/6, 2/6, 3/6]))
    
    # Matrix with zero columns
    M = np.array([[0.0, 1.0], [0.0, 2.0]])
    normalize_columns_inplace(M)
    assert_array_almost_equal(M[:, 1], np.array([1/3, 2/3]))

def test_ahp_edge_cases():
    """Test edge cases in AHP model."""
    model = (AHPBuilder()
             .add_criteria(["price", "quality", "service"])
             .add_alternatives(["A", "B", "C"])
             .build())
    
    # Try to get priorities before setting weights
    with pytest.raises(ValueError):
        model.alternative_priorities()
    
    # Extreme criteria weights
    model.set_criteria_weights({"price": 1.0, "quality": 0.0, "service": 0.0})
    
    # Invalid criteria weights (missing criteria)
    with pytest.raises(NormalizationError):
        model.set_criteria_weights({"invalid": 1.0})
    
    # Set identical alternative priorities
    criteria = ["price", "quality", "service"]
    alternatives = ["A", "B", "C"]
    for c in criteria:
        model.set_alt_priorities(c, {
            (a1, a2): 1.0  # Equal importance
            for i, a1 in enumerate(alternatives)
            for a2 in alternatives[i+1:]
        })
    
    # Check that alternatives get equal priorities when all importances are equal
    priorities, labels = model.alternative_priorities()
    expected = np.ones(len(alternatives)) / len(alternatives)
    assert_array_almost_equal(priorities, expected)
    assert labels == alternatives  # Check labels order is preserved

def test_anp_edge_cases():
    """Test edge cases in ANP model."""
    # Empty cluster
    model = (ANPBuilder()
             .add_cluster("empty", [])
             .add_alternatives(["a1"])
             .build())
    
    # Single element clusters
    model = (ANPBuilder()
             .add_cluster("single", ["node1"])
             .add_alternatives(["a1"])
             .build())
    
    # Equal cluster weights
    model.set_cluster_weights({
        "single": 0.5,
        "alternatives": 0.5
    })
    
    # Test zero blocks
    model.add_block("single", "alternatives", np.zeros((1, 1)))
    model.add_block("alternatives", "single", np.zeros((1, 1)))
    
    # Should raise error due to zero columns
    with pytest.raises(StructureError):
        model.check_structure()

def test_limiter_edge_cases():
    """Test edge cases in limit matrix calculation."""
    power_limiter = PowerMethodLimiter()
    
    # Test with invalid damping value
    with pytest.raises(ValueError):
        DampedPowerLimiter(damping=-0.1)
    
    # 1x1 matrix
    M = np.array([[1.0]])
    assert power_limiter.limit(M)[0, 0] == 1.0
    
    # Identity matrix
    n = 3
    M = np.eye(n)
    limit = power_limiter.limit(M)
    assert_array_almost_equal(limit, np.eye(n))
    
    # Almost non-convergent matrix
    M = np.array([
        [0.99, 0.02],
        [0.01, 0.98]
    ])
    # Should still converge, just might take longer
    limit = power_limiter.limit(M, max_iter=10000)
    assert np.allclose(limit[:, 0], limit[:, 1])  # All columns should be equal
    
    # Test damping with extreme values
    damped_high = DampedPowerLimiter(damping=0.99)
    limit_high = damped_high.limit(M)
    assert_array_almost_equal(limit_high, np.ones_like(M) / M.shape[0], decimal=6)

    # Test damped vs power method convergence
    damped = DampedPowerLimiter(damping=0.1)
    limit_damped = damped.limit(M)
    limit_power = power_limiter.limit(M)
    assert_array_almost_equal(limit_damped, limit_power, decimal=6)

def test_invalid_model_operations():
    """Test invalid operations on models."""
    # AHP: Try to get priorities before setting weights
    model = (AHPBuilder()
             .add_criteria(["c1"])
             .add_alternatives(["a1"])
             .build())
    with pytest.raises(ValueError):
        model.alternative_priorities()
    
    # ANP: Try to build supermatrix without cluster weights
    model = (ANPBuilder()
             .add_cluster("c1", ["n1"])
             .add_alternatives(["a1"])
             .build())
    with pytest.raises(ValueError):
        model.alternative_priorities()
    
    # Try to use groups in flat AHP
    model = (AHPBuilder()
             .add_criteria(["c1"])
             .add_alternatives(["a1"])
             .build())
    with pytest.raises(ValueError):
        model.set_subcriteria_weights("group", {"c1": 1.0})

def test_numerical_stability():
    """Test numerical stability in various operations."""
    # Test with very small numbers
    pc = PairwiseComparison(["A", "B"], np.array([[1.0, 1e-15], [1e15, 1.0]]))
    priorities = pc.priorities()
    assert np.isfinite(priorities).all()
    assert np.sum(priorities) == pytest.approx(1.0)
    assert priorities.min() > 0  # All priorities should be positive

    # Test normalization stability
    huge = np.array([1e15, 2e15])
    norm = normalize_vector_nonneg(huge)
    assert np.isfinite(norm).all()
    assert np.sum(norm) == pytest.approx(1.0)
    
    # Test limit matrix stability
    M = np.array([[0.999999, 0.000001], [0.000001, 0.999999]])
    limit = PowerMethodLimiter().limit(M)
    assert np.isfinite(limit).all()