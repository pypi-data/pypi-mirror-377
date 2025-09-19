"""Test suite for core components of SaatyPy."""
import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from saatypy.components.scale import SaatyScale
from saatypy.components.pairwise import PairwiseComparison
from saatypy.components.modeling import Node, Cluster
from saatypy.components.errors import ModelError, NormalizationError

def test_saaty_scale():
    """Test Saaty scale validation and reciprocal calculation."""
    assert SaatyScale.is_valid(1.0)
    assert SaatyScale.is_valid(9.0)
    assert SaatyScale.is_valid(1/9)
    assert not SaatyScale.is_valid(0.0)
    assert not SaatyScale.is_valid(-1.0)
    
    assert SaatyScale.reciprocal(2.0) == 0.5
    assert SaatyScale.reciprocal(1.0) == 1.0
    
    with pytest.raises(ValueError):
        SaatyScale.reciprocal(0.0)
    with pytest.raises(ValueError):
        SaatyScale.reciprocal(-1.0)

def test_pairwise_comparison_from_judgments(mock_criteria):
    """Test PairwiseComparison creation from sparse judgments."""
    judgments = {
        ("price", "quality"): 2.0,
        ("price", "service"): 4.0,
        ("quality", "service"): 2.0
    }
    pc = PairwiseComparison.from_judgments(mock_criteria, judgments)
    
    # Check matrix properties
    assert pc.matrix.shape == (3, 3)
    assert np.all(pc.matrix > 0)  # Positive
    assert np.allclose(np.diag(pc.matrix), 1.0)  # Unit diagonal
    assert np.allclose(pc.matrix * pc.matrix.T, 1.0)  # Reciprocal
    
    # Check specific values
    assert pc.matrix[0, 1] == 2.0  # price vs quality
    assert pc.matrix[0, 2] == 4.0  # price vs service
    assert pc.matrix[1, 2] == 2.0  # quality vs service
    assert pc.matrix[1, 0] == 0.5  # quality vs price (reciprocal)

def test_pairwise_comparison_consistency(consistent_matrix_3x3, consistent_priorities_3x3):
    """Test consistency calculations in PairwiseComparison."""
    pc = PairwiseComparison(["A", "B", "C"], consistent_matrix_3x3)
    cr, ci, lambda_max = pc.consistency_ratio()
    
    # For a perfectly consistent matrix:
    assert cr == pytest.approx(0.0, abs=1e-6)  # CR ≈ 0
    assert ci == pytest.approx(0.0, abs=1e-6)  # CI ≈ 0
    assert lambda_max == pytest.approx(3.0, abs=1e-6)  # λmax = n
    
    # Check priorities
    assert_array_almost_equal(pc.priorities(), consistent_priorities_3x3, decimal=6)

def test_node_and_cluster():
    """Test Node and Cluster classes."""
    # Test Node creation
    node = Node("price", description="Cost in USD")
    assert node.name == "price"
    assert node.description == "Cost in USD"
    
    # Test Cluster creation
    cluster = Cluster("criteria", [
        Node("price"),
        Node("quality"),
        Node("service")
    ])
    assert cluster.name == "criteria"
    assert cluster.size == 3
    assert [n.name for n in cluster.nodes] == ["price", "quality", "service"]
    
    # Test duplicate node names
    with pytest.raises(ValueError):
        Cluster("test", [Node("price"), Node("price")])

def test_error_classes():
    """Test custom error classes."""
    assert issubclass(ModelError, Exception)
    assert issubclass(NormalizationError, ModelError)