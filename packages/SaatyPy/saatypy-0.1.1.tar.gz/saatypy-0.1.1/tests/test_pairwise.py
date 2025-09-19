"""Additional tests for pairwise comparisons and consistency checking."""
import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from saatypy.components.pairwise import PairwiseComparison

def test_pairwise_matrix_validation():
    """Test matrix validation in PairwiseComparison."""
    labels = ["A", "B"]
    
    # Test non-positive entries
    with pytest.raises(ValueError, match="All comparison values must be positive"):
        M = np.array([[1.0, -2.0], [-0.5, 1.0]])
        PairwiseComparison(labels, M)
    
    # Test non-unit diagonal
    with pytest.raises(ValueError, match="Diagonal must be 1.0"):
        M = np.array([[2.0, 2.0], [0.5, 1.0]])
        PairwiseComparison(labels, M)
    
    # Test non-reciprocal matrix
    with pytest.raises(ValueError, match="Matrix must be reciprocal"):
        M = np.array([[1.0, 2.0], [0.6, 1.0]])  # 0.6 ≠ 1/2
        PairwiseComparison(labels, M)
    
    # Test shape mismatch
    with pytest.raises(ValueError, match="Matrix shape must match labels length"):
        M = np.array([[1.0, 2.0, 3.0], [0.5, 1.0, 2.0], [0.33, 0.5, 1.0]])
        PairwiseComparison(labels, M)  # 3x3 matrix but only 2 labels

def test_pairwise_from_invalid_judgments(mock_criteria):
    """Test error cases in from_judgments constructor."""
    # Unknown label
    with pytest.raises(KeyError, match="Unknown label"):
        PairwiseComparison.from_judgments(
            mock_criteria,
            {("price", "unknown"): 2.0}
        )
    
    # Invalid ratio
    with pytest.raises(ValueError, match="Invalid ratio"):
        PairwiseComparison.from_judgments(
            mock_criteria,
            {("price", "quality"): -1.0}
        )

def test_pairwise_principal_eigen(consistent_matrix_3x3, consistent_priorities_3x3):
    """Test principal eigenvector calculation."""
    pc = PairwiseComparison(["A", "B", "C"], consistent_matrix_3x3)
    
    # Test eigenvalue calculation
    lambda_max, evec = pc.principal_eigen()
    assert lambda_max == pytest.approx(3.0, abs=1e-6)
    assert_array_almost_equal(evec, consistent_priorities_3x3, decimal=6)
    
    # Test priorities (should match principal eigenvector)
    assert_array_almost_equal(pc.priorities(), consistent_priorities_3x3, decimal=6)
    
    # Test caching
    # Second call should use cached values
    lambda_max2, evec2 = pc.principal_eigen()
    assert lambda_max2 is not None
    assert evec2 is not None
    assert_array_almost_equal(evec2, evec, decimal=10)

def test_pairwise_comparisons_normalized(mock_alternatives):
    """Test that priorities are always normalized."""
    pc = PairwiseComparison.from_judgments(
        mock_alternatives,
        {
            ("A", "B"): 2.0,
            ("A", "C"): 4.0,
            ("B", "C"): 2.0
        }
    )
    priorities = pc.priorities()
    
    # Sum should be 1.0
    assert np.sum(priorities) == pytest.approx(1.0, abs=1e-6)
    
    # All values should be positive
    assert np.all(priorities > 0)

def test_pairwise_comparison_string_repr():
    """Test string representation of PairwiseComparison."""
    labels = ["A", "B"]
    M = np.array([[1.0, 2.0], [0.5, 1.0]])
    pc = PairwiseComparison(labels, M)
    
    # Basic representation should include shape
    assert str(pc).startswith("PairwiseComparison")