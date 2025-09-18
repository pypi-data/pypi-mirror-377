import torch
from nous.facts import BetaFactLayer, PiecewiseLinearCalibrator

def test_beta_fact_layer_forward():
    layer = BetaFactLayer(input_dim=4, num_facts=6)
    x = torch.randn(5, 4)
    y = layer(x)
    assert y.shape == (5, 6)
    assert torch.isfinite(y).all()

def test_calibrator_monotonic():
    cal = PiecewiseLinearCalibrator(num_bins=8, input_range=(-2.0, 2.0))
    x = torch.linspace(-2.0, 2.0, 21)
    y = cal(x)
    # monotonic non-decreasing
    assert torch.all(y[1:] >= y[:-1])