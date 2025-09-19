"""Test suite for SaatyPy math utilities."""
import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from saatypy.components.math.normalize import (
    normalize_vector_nonneg,
    normalize_columns_inplace,
    aligned_vector_from_mapping,
)
from saatypy.components.math.prioritizers import (
    EigenvectorPriority,
    GeometricMeanPriority,
)
from saatypy.components.errors import NormalizationError

def test_normalize_vector_nonneg():
    """Test non-negative vector normalization."""
    # Basic normalization
    v = np.array([1.0, 2.0, 3.0])
    normalized = normalize_vector_nonneg(v)
    assert_array_almost_equal(normalized, np.array([1/6, 2/6, 3/6]))
    assert np.sum(normalized) == pytest.approx(1.0)
    
    # Zero vector
    with pytest.raises(NormalizationError):
        normalize_vector_nonneg(np.zeros(3))
    
    # Negative values
    with pytest.raises(NormalizationError):
        normalize_vector_nonneg(np.array([1.0, -1.0, 1.0]))

def test_normalize_columns_inplace():
    """Test column normalization in place."""
    M = np.array([
        [1.0, 2.0],
        [2.0, 4.0],
        [3.0, 6.0]
    ])
    expected = np.array([
        [1/6, 1/6],
        [2/6, 2/6],
        [3/6, 3/6]
    ])
    normalize_columns_inplace(M)
    assert_array_almost_equal(M, expected)
    
    # Test with zero column
    M = np.array([[0.0, 1.0], [0.0, 2.0]])
    normalize_columns_inplace(M)  # Should not raise error for zero column
    assert_array_almost_equal(M[:, 1], np.array([1/3, 2/3]))

def test_aligned_vector_from_mapping():
    """Test vector alignment from label mapping."""
    order = ["A", "B", "C"]
    values = {"A": 1.0, "B": 2.0, "C": 3.0}
    
    v = aligned_vector_from_mapping(order, values)
    assert_array_almost_equal(v, np.array([1/6, 2/6, 3/6]))
    
    # Missing label
    with pytest.raises(NormalizationError):
        aligned_vector_from_mapping(order, {"A": 1.0, "B": 2.0})
    
    # Extra label
    with pytest.raises(NormalizationError):
        aligned_vector_from_mapping(
            order,
            {"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0}
        )

def test_eigenvector_priority():
    """Test eigenvector-based priority calculation."""
    strategy = EigenvectorPriority()
    M = np.array([
        [1.0, 2.0, 4.0],
        [0.5, 1.0, 2.0],
        [0.25, 0.5, 1.0]
    ])
    
    priorities = strategy.priorities(M)
    # Sum should be 1
    assert np.sum(priorities) == pytest.approx(1.0)
    # Should be in descending order
    assert np.all(np.diff(priorities) <= 0)

def test_geometric_mean_priority():
    """Test geometric mean priority calculation."""
    strategy = GeometricMeanPriority()
    M = np.array([
        [1.0, 2.0, 4.0],
        [0.5, 1.0, 2.0],
        [0.25, 0.5, 1.0]
    ])
    
    priorities = strategy.priorities(M)
    # Sum should be 1
    assert np.sum(priorities) == pytest.approx(1.0)
    # Should be in descending order for this consistent matrix
    assert np.all(np.diff(priorities) <= 0)
    
    # Compare with eigenvector method
    eigen_priorities = EigenvectorPriority().priorities(M)
    # For consistent matrices, methods should give similar results
    assert_array_almost_equal(priorities, eigen_priorities, decimal=6)