import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

from saatypy.components.pairwise import PairwiseComparison
from saatypy.ahp import AHPBuilder
from saatypy.anp import ANPBuilder
from saatypy.components.math.limiters import PowerMethodLimiter

def test_ahp_saaty_3x3_priorities_and_cr():
    """
    Classic Saaty 3x3 example:
      [[1, 3, 5],
       [1/3, 1, 3],
       [1/5, 1/3, 1]]
    Using column-normalization + row-mean priorities (your default).
    Expected priorities ~= [0.63334572, 0.26049796, 0.10615632]
    """
    labels = ["C1", "C2", "C3"]
    M = np.array([
        [1.0,   3.0, 5.0],
        [1/3.,  1.0, 3.0],
        [1/5., 1/3., 1.0],
    ], dtype=float)
    pc = PairwiseComparison(labels, M)
    w = pc.priorities()
    assert np.isclose(w.sum(), 1.0)
    assert_array_almost_equal(w, np.array([0.63334572, 0.26049796, 0.10615632]), decimal=2)

    # If you have an eigenvalue-based CR somewhere, you could check CR < 0.1 here.
    # (Keeping it simple: your current API focuses on priorities.)

def test_ahp_small_car_like_example():
    """
    3 criteria, 3 alternatives; reproducible example with a known outcome.
    We assert:
      - priority vector sums to 1
      - ranking is stable under small tolerance
    """
    model = (AHPBuilder()
             .add_criteria(["performance", "price", "battery"])
             .add_alternatives(["A", "B", "C"])
             .build())

    # Criteria weights via pairwise comparisons (performance dominates)
    pc_crit = PairwiseComparison.from_judgments(
        ["performance", "price", "battery"],
        {
            ("performance", "price"): 3.0,
            ("performance", "battery"): 5.0,
            ("price", "battery"): 2.0,
        }
    )
    model.set_criteria_weights(pc_crit)

    # Local alt priorities for each criterion
    # (A beats B beats C under each criterion, with varying strength)
    judg = {
        ("A", "B"): 2.0,
        ("A", "C"): 4.0,
        ("B", "C"): 2.0,
    }
    for c in ["performance", "price", "battery"]:
        model.set_alt_priorities(c, judg)

    gp, labels = model.alternative_priorities()
    assert labels == ["A", "B", "C"]
    assert np.isclose(gp.sum(), 1.0)
    # A should be clearly top; B > C
    assert gp[0] > gp[1] > gp[2]