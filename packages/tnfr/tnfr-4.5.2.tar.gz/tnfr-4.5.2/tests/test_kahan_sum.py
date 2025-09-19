import math

import pytest

from tnfr.helpers.numeric import kahan_sum_nd


def test_kahan_sum_nd_compensates_cancellation_1d():
    xs = [1e16, 1.0, -1e16]
    assert sum(xs) == 0.0
    (res_x,) = kahan_sum_nd(((x,) for x in xs), dims=1)
    assert res_x == pytest.approx(math.fsum(xs))


def test_kahan_sum_nd_compensates_cancellation_2d():
    pairs = [(1e16, 1e16), (1.0, 1.0), (-1e16, -1e16)]
    res_x, res_y = kahan_sum_nd(pairs, dims=2)
    exp_x = math.fsum(p[0] for p in pairs)
    exp_y = math.fsum(p[1] for p in pairs)
    assert res_x == pytest.approx(exp_x)
    assert res_y == pytest.approx(exp_y)


def test_kahan_sum_nd_requires_positive_dims():
    with pytest.raises(ValueError):
        kahan_sum_nd([], dims=0)
