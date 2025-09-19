"""Test suite for ANP implementation."""
import pytest
import numpy as np

from saatypy.anp import ANPBuilder, ANPModel, Supermatrix
from saatypy.components.pairwise import PairwiseComparison
from saatypy.components.errors import StructureError, NormalizationError

@pytest.fixture
def market_clusters():
    """Example clusters for market share analysis."""
    return [
        ("market_factors", ["price", "quality", "advertising"]),
        ("competitors", ["comp_a", "comp_b", "comp_c"]),
    ]

@pytest.fixture
def basic_anp_model(market_clusters):
    """Basic ANP model for market analysis."""
    model = (ANPBuilder()
            .add_cluster(*market_clusters[0])
            .add_cluster(*market_clusters[1])
            .add_alternatives(["alt_a", "alt_b"], name="alternatives")
            .build())
    return model

def test_anp_builder():
    """Test ANP model builder functionality."""
    # Empty builder
    builder = ANPBuilder()
    with pytest.raises(ValueError):
        builder.build()  # No alternatives defined
    
    # Basic valid model
    model = (ANPBuilder()
             .add_cluster("criteria", ["c1", "c2"])
             .add_alternatives(["a1", "a2"])
             .build())
    assert isinstance(model, ANPModel)
    
    # Duplicate cluster names
    with pytest.raises(ValueError):
        (ANPBuilder()
         .add_cluster("same", ["n1"])
         .add_cluster("same", ["n2"]))
    
    # Duplicate node names within cluster
    with pytest.raises(ValueError):
        ANPBuilder().add_cluster("test", ["same", "same"])

def test_supermatrix_construction(basic_anp_model):
    """Test supermatrix construction from blocks."""
    # Add some blocks
    basic_anp_model.add_block_uniform("market_factors", "competitors")
    basic_anp_model.add_block(
        "competitors",
        "market_factors",
        np.array([
            [0.5, 0.3, 0.2],
            [0.3, 0.4, 0.3],
            [0.2, 0.3, 0.5]
        ])
    )
    
    # Build supermatrix
    S = basic_anp_model.build_supermatrix()
    assert isinstance(S, Supermatrix)
    
    # Convert to dense
    M = S.to_dense()
    assert M.shape == (8, 8)  # 3 + 3 + 2 nodes total
    assert np.allclose(M.sum(axis=0), 1.0)  # Column stochastic

def test_block_validation(basic_anp_model):
    """Test block input validation."""
    # Invalid shape
    with pytest.raises(ValueError):
        basic_anp_model.add_block(
            "market_factors",
            "competitors",
            np.ones((2, 2))  # Wrong shape
        )
    
    # Invalid judgments
    with pytest.raises(KeyError):
        basic_anp_model.add_block(
            "market_factors",
            "competitors",
            {"unknown_node": PairwiseComparison(["a", "b"], np.ones((2, 2)))}
        )

def test_cluster_weights(basic_anp_model):
    """Test cluster weight setting and validation."""
    # Direct weights
    weights = {
        "market_factors": 0.4,
        "competitors": 0.4,
        "alternatives": 0.2
    }
    basic_anp_model.set_cluster_weights(weights)
    
    # From pairwise comparisons
    pc = PairwiseComparison.from_judgments(
        ["market_factors", "competitors", "alternatives"],
        {
            ("market_factors", "competitors"): 2.0,
            ("market_factors", "alternatives"): 3.0,
            ("competitors", "alternatives"): 1.5
        }
    )
    basic_anp_model.set_cluster_weights(pc)
    
    # Invalid weights
    with pytest.raises(ValueError):
        basic_anp_model.set_cluster_weights({"unknown": 1.0})

def test_alternative_priorities(basic_anp_model):
    """Test alternative priority calculation in ANP."""
    # Set cluster weights
    basic_anp_model.set_cluster_weights({
        "market_factors": 0.4,
        "competitors": 0.4,
        "alternatives": 0.2
    })
    
    # Add some blocks
    basic_anp_model.add_block_uniform("market_factors", "competitors")
    basic_anp_model.add_block_uniform("competitors", "market_factors")
    basic_anp_model.add_block_uniform("alternatives", "market_factors")
    basic_anp_model.add_block_uniform("alternatives", "competitors")
    
    # Calculate priorities
    priorities, labels = basic_anp_model.alternative_priorities()
    
    # Check properties
    assert len(priorities) == 2  # Two alternatives
    assert np.sum(priorities) == pytest.approx(1.0)
    assert np.all(priorities >= 0)
    assert set(labels) == {"alt_a", "alt_b"}

def test_structure_validation(basic_anp_model):
    """Test network structure validation."""
    # Empty network (some zero columns)
    with pytest.raises(StructureError):
        basic_anp_model.check_structure()
    
    # Add minimal structure
    basic_anp_model.add_block_uniform("market_factors", "competitors")
    basic_anp_model.add_block_uniform("competitors", "market_factors")
    basic_anp_model.add_block_uniform("alternatives", "market_factors")
    # Now should be valid
    basic_anp_model.check_structure()

def test_weighted_supermatrix(basic_anp_model):
    """Test supermatrix weighting by cluster priorities."""
    # Set up model
    basic_anp_model.set_cluster_weights({
        "market_factors": 0.4,
        "competitors": 0.4,
        "alternatives": 0.2
    })
    basic_anp_model.add_block_uniform("market_factors", "competitors")
    basic_anp_model.add_block_uniform("competitors", "market_factors")
    
    # Build and weight supermatrix
    S = basic_anp_model.build_supermatrix()
    W = S.weight_by_row_clusters(basic_anp_model.cluster_weights)
    
    # Check weighted matrix properties
    M = W.to_dense()
    assert np.allclose(M.sum(axis=0), 1.0)  # Still column stochastic
    
    # Invalid weights
    with pytest.raises(NormalizationError):
        S.weight_by_row_clusters({"cluster": 0.0})  # Zero weights

def test_anp_reporting(basic_anp_model):
    """Test ANP report data generation."""
    # Setup model
    basic_anp_model.set_cluster_weights({
        "market_factors": 0.4,
        "competitors": 0.4,
        "alternatives": 0.2
    })
    basic_anp_model.add_block_uniform("market_factors", "competitors")
    basic_anp_model.add_block_uniform("competitors", "market_factors")
    basic_anp_model.add_block_uniform("alternatives", "market_factors")
    
    # Get report data
    report = basic_anp_model.to_report_data()
    
    # Check report structure
    assert "cluster_weights" in report
    assert "max_col_deviation" in report
    assert "alternatives" in report
    assert "global_priorities" in report
    assert "ranking_str" in report
    assert "blocks" in report
    
    # Check data properties
    assert len(report["global_priorities"]) == 2  # Two alternatives
    assert sum(report["global_priorities"]) == pytest.approx(1.0)
    assert len(report["cluster_weights"]) == 3  # Three clusters