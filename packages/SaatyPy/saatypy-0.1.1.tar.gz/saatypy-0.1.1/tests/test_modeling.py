"""Test suite for model component classes."""
import pytest
from saatypy.components.modeling import Node, Cluster

def test_node_creation():
    """Test Node creation and properties."""
    # Basic node
    node = Node("test")
    assert node.name == "test"
    assert node.description == ""
    
    # Node with description
    node = Node("test", "Test description")
    assert node.name == "test"
    assert node.description == "Test description"

def test_cluster_creation():
    """Test Cluster creation and properties."""
    nodes = [
        Node("A", "First node"),
        Node("B", "Second node"),
        Node("C", "Third node")
    ]
    
    cluster = Cluster("test_cluster", nodes)
    assert cluster.name == "test_cluster"
    assert cluster.size == 3
    assert cluster.weight is None
    
    # Check node preservation
    assert [n.name for n in cluster.nodes] == ["A", "B", "C"]
    assert cluster.nodes[0].description == "First node"

def test_cluster_validation():
    """Test Cluster validation rules."""
    # Duplicate node names
    with pytest.raises(ValueError, match="Duplicate node names"):
        Cluster("test", [
            Node("A", "First"),
            Node("A", "Second")  # Duplicate name
        ])
    
    # Empty cluster is allowed
    cluster = Cluster("empty", [])
    assert cluster.size == 0
    
    # Weight assignment
    cluster = Cluster("weighted", [Node("A")])
    cluster.weight = 0.5
    assert cluster.weight == 0.5

def test_cluster_post_init():
    """Test Cluster's __post_init__ validation."""
    # This should work
    Cluster("test", [Node("A"), Node("B")])
    
    # These should fail
    with pytest.raises(ValueError):
        Cluster("test", [Node("same"), Node("same")])
        
    # Even with different descriptions
    with pytest.raises(ValueError):
        Cluster("test", [
            Node("same", "desc1"),
            Node("same", "desc2")
        ])

def test_dataclass_immutability():
    """Test immutability of Node and mutability of Cluster."""
    node = Node("test")
    
    # Node should be frozen (immutable)
    with pytest.raises(AttributeError):
        node.name = "new_name"
    with pytest.raises(AttributeError):
        node.description = "new_description"
    
    # Cluster should be mutable
    cluster = Cluster("test", [node])
    cluster.weight = 0.5  # This should work
    assert cluster.weight == 0.5