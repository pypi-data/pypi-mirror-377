"""Test suite for supermatrix limiters."""
import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from saatypy.components.math.limiters import (
    PowerMethodLimiter,
    DampedPowerLimiter,
)
from saatypy.components.errors import NormalizationError

def test_power_method_limiter():
    """Test basic power method limiting."""
    limiter = PowerMethodLimiter()
    
    # Test with a simple column-stochastic matrix
    M = np.array([
        [0.5, 0.3],
        [0.5, 0.7]
    ])
    limit = limiter.limit(M, max_iter=1000, tol=1e-12)
    
    # Result should be column-stochastic
    assert np.allclose(limit.sum(axis=0), 1.0)
    
    # All columns should be identical (convergence)
    assert_array_almost_equal(limit[:, 0], limit[:, 1])
    
    # Test error on non-stochastic matrix
    with pytest.raises(NormalizationError):
        M_bad = np.array([[0.5, 0.3], [0.6, 0.7]])  # columns don't sum to 1
        limiter.limit(M_bad)

def test_power_method_convergence():
    """Test convergence properties of power method."""
    limiter = PowerMethodLimiter()
    
    # 3x3 column-stochastic matrix
    M = np.array([
        [0.3, 0.2, 0.5],
        [0.3, 0.5, 0.2],
        [0.4, 0.3, 0.3]
    ])
    
    # Test with different tolerances
    limit1 = limiter.limit(M, tol=1e-6)
    limit2 = limiter.limit(M, tol=1e-12)
    
    # Results should be very close
    assert_array_almost_equal(limit1, limit2, decimal=6)
    
    # Test with different max_iter
    limit3 = limiter.limit(M, max_iter=100)
    limit4 = limiter.limit(M, max_iter=1000)
    
    # Results should be identical if converged
    assert_array_almost_equal(limit3, limit4)

def test_damped_power_limiter():
    """Test damped power method limiting."""
    # Test with different damping factors
    damping_factors = [0.05, 0.15, 0.5]
    
    M = np.array([
        [0.5, 0.3],
        [0.5, 0.7]
    ])
    
    for d in damping_factors:
        limiter = DampedPowerLimiter(damping=d)
        limit = limiter.limit(M)
        
        # Result should be column-stochastic
        assert np.allclose(limit.sum(axis=0), 1.0)
        
        # All columns should be identical
        assert_array_almost_equal(limit[:, 0], limit[:, 1])

def test_damped_power_validation():
    """Test validation in DampedPowerLimiter."""
    # Invalid damping values
    with pytest.raises(ValueError):
        DampedPowerLimiter(damping=-0.1)
    with pytest.raises(ValueError):
        DampedPowerLimiter(damping=1.0)
    
    # Valid edge cases
    DampedPowerLimiter(damping=0.0)  # minimum
    DampedPowerLimiter(damping=0.99)  # close to maximum

def test_limiter_identity():
    """Test that limiters preserve steady states."""
    # Create a matrix that's already in its limit form
    v = np.array([0.3, 0.7])
    M = np.column_stack([v, v])  # Both columns identical
    
    # Both limiters should preserve this
    power_limit = PowerMethodLimiter().limit(M)
    damped_limit = DampedPowerLimiter(damping=0.05).limit(M)
    
    assert_array_almost_equal(power_limit, M)
    # Damped might be slightly different due to perturbation
    assert_array_almost_equal(damped_limit[:, 0], v, decimal=2)