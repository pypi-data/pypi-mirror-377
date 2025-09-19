"""Test suite for AHP implementation."""
import pytest
import numpy as np

from saatypy.ahp import AHPBuilder
from saatypy.components.pairwise import PairwiseComparison

@pytest.fixture
def laptop_criteria():
    """Example criteria for laptop selection."""
    return ["performance", "price", "battery"]

@pytest.fixture
def laptop_alternatives():
    """Example alternatives for laptop selection."""
    return ["laptop_a", "laptop_b", "laptop_c"]

@pytest.fixture
def basic_ahp_model(laptop_criteria, laptop_alternatives):
    """Basic AHP model for laptop selection."""
    return (AHPBuilder()
            .add_criteria(laptop_criteria)
            .add_alternatives(laptop_alternatives)
            .build())

@pytest.fixture
def hierarchical_ahp_model():
    """AHP model with criteria groups."""
    return (AHPBuilder()
            .add_criteria_groups({
                "technical": ["performance", "reliability"],
                "economic": ["price", "maintenance"],
                "user": ["battery", "portability"]
            })
            .add_alternatives(["laptop_a", "laptop_b", "laptop_c"])
            .build())

def test_ahp_builder():
    """Test AHP model builder functionality."""
    builder = AHPBuilder()
    with pytest.raises(ValueError):
        builder.build()  
    
    # Missing alternatives
    builder = AHPBuilder()
    builder.add_criteria(["c1", "c2"])
    with pytest.raises(ValueError):
        builder.build()
    
    # Missing criteria
    builder = AHPBuilder()
    builder.add_alternatives(["a1", "a2"])
    with pytest.raises(ValueError):
        builder.build()
    
    # Duplicate criteria
    with pytest.raises(ValueError):
        AHPBuilder().add_criteria(["c1", "c1"])
    
    # Duplicate alternatives
    with pytest.raises(ValueError):
        AHPBuilder().add_alternatives(["a1", "a1"])
    
    # Duplicate criteria across groups
    with pytest.raises(ValueError):
        AHPBuilder().add_criteria_groups({
            "g1": ["c1", "c2"],
            "g2": ["c2", "c3"]  # c2 appears twice
        })

def test_basic_ahp_weights(basic_ahp_model, laptop_criteria):
    """Test setting and retrieving criteria weights."""
    # Set weights directly
    weights = {"performance": 0.5, "price": 0.3, "battery": 0.2}
    basic_ahp_model.set_criteria_weights(weights)
    
    # Check via final priorities
    pc = PairwiseComparison.from_judgments(
        laptop_criteria,
        {
            ("performance", "price"): 2.0,
            ("performance", "battery"): 3.0,
            ("price", "battery"): 1.5
        }
    )
    basic_ahp_model.set_criteria_weights(pc)

def test_hierarchical_weights(hierarchical_ahp_model):
    """Test weight setting in hierarchical AHP."""
    # Set group weights
    group_weights = {
        "technical": 0.5,
        "economic": 0.3,
        "user": 0.2
    }
    hierarchical_ahp_model.set_group_weights(group_weights)
    
    # Set subcriteria weights for each group
    hierarchical_ahp_model.set_subcriteria_weights(
        "technical",
        {"performance": 0.7, "reliability": 0.3}
    )
    hierarchical_ahp_model.set_subcriteria_weights(
        "economic",
        {"price": 0.6, "maintenance": 0.4}
    )
    hierarchical_ahp_model.set_subcriteria_weights(
        "user",
        {"battery": 0.6, "portability": 0.4}
    )

def test_alternative_priorities(basic_ahp_model):
    """Test alternative priority calculation."""
    # Set criteria weights
    basic_ahp_model.set_criteria_weights({
        "performance": 0.5,
        "price": 0.3,
        "battery": 0.2
    })
    
    # Set alternative priorities for each criterion
    for criterion in ["performance", "price", "battery"]:
        basic_ahp_model.set_alt_priorities(
            criterion,
            {
                ("laptop_a", "laptop_b"): 2.0,
                ("laptop_a", "laptop_c"): 3.0,
                ("laptop_b", "laptop_c"): 1.5
            }
        )
    
    # Calculate final priorities
    priorities, labels = basic_ahp_model.alternative_priorities()
    
    # Check properties
    assert len(priorities) == len(labels) == 3
    assert np.sum(priorities) == pytest.approx(1.0)
    assert np.all(priorities >= 0)
    assert set(labels) == {"laptop_a", "laptop_b", "laptop_c"}

def test_ahp_reporting(basic_ahp_model):
    """Test AHP report data generation."""
    # Setup model
    basic_ahp_model.set_criteria_weights({
        "performance": 0.5,
        "price": 0.3,
        "battery": 0.2
    })
    
    for criterion in ["performance", "price", "battery"]:
        basic_ahp_model.set_alt_priorities(criterion, {
            ("laptop_a", "laptop_b"): 2.0,
            ("laptop_a", "laptop_c"): 3.0,
            ("laptop_b", "laptop_c"): 1.5
        })
    
    # Get report data
    report = basic_ahp_model.to_report_data()
    
    # Check report structure
    assert "criteria_weights" in report
    assert "local_alternatives" in report
    assert "alternatives" in report
    assert "global_priorities" in report
    assert "ranking_str" in report
    assert "inputs" in report
    
    # Check data properties
    assert len(report["global_priorities"]) == 3
    assert sum(report["global_priorities"]) == pytest.approx(1.0)
    assert len(report["criteria_weights"]) == 3
    assert sum(report["criteria_weights"].values()) == pytest.approx(1.0)

def test_validation_errors(basic_ahp_model):
    """Test validation and error handling."""
    # Try to get priorities without weights
    with pytest.raises(ValueError):
        basic_ahp_model.alternative_priorities()
    
    # Set criteria weights
    basic_ahp_model.set_criteria_weights({
        "performance": 0.5,
        "price": 0.3,
        "battery": 0.2
    })
    
    # Try to get priorities without alternative preferences
    with pytest.raises(ValueError):
        basic_ahp_model.alternative_priorities()
    
    # Try to set weights for unknown criterion
    with pytest.raises(KeyError):
        basic_ahp_model.set_alt_priorities(
            "unknown",
            {("laptop_a", "laptop_b"): 2.0}
        )

def test_hierarchical_validation(hierarchical_ahp_model):
    """Test validation in hierarchical AHP."""
    # Try to set flat criteria weights when using groups
    with pytest.raises(ValueError):
        hierarchical_ahp_model.set_criteria_weights({"performance": 1.0})
    
    # Missing group weights
    with pytest.raises(ValueError):
        hierarchical_ahp_model.alternative_priorities()
    
    # Set group weights but missing subcriteria
    hierarchical_ahp_model.set_group_weights({
        "technical": 0.5,
        "economic": 0.3,
        "user": 0.2
    })
    with pytest.raises(ValueError):
        hierarchical_ahp_model.alternative_priorities()
    
    # Unknown group in subcriteria weights
    with pytest.raises(KeyError):
        hierarchical_ahp_model.set_subcriteria_weights(
            "unknown",
            {"subcrit1": 0.5, "subcrit2": 0.5}
        )