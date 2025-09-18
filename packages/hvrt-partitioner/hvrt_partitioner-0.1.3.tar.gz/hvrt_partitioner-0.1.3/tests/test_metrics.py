import pytest
import numpy as np
import pandas as pd
from src.hvrt.metrics import full_report, _check_params
from src.hvrt.feature_data import FeatureReport, VarianceReport, SpanReport

@pytest.fixture
def simple_data():
    """Fixture for simple, predictable data for metric testing."""
    X = np.array([
        [1, 10], # Partition 0
        [2, 20], # Partition 0
        [10, 1], # Partition 1
        [20, 2]  # Partition 1
    ])
    labels = np.array([0, 0, 1, 1])
    return X, labels

def test_check_params_valid(simple_data):
    """Test that _check_params runs with valid inputs."""
    X, labels = simple_data
    X_df, unique_labels, counts, n_clusters = _check_params(X, labels)
    assert isinstance(X_df, pd.DataFrame)
    assert n_clusters == 2
    assert np.array_equal(unique_labels, [0, 1])
    assert np.array_equal(counts, [2, 2])

def test_check_params_insufficient_clusters():
    """Test that _check_params raises ValueError for a single cluster."""
    X = np.random.rand(10, 2)
    labels = np.zeros(10)
    with pytest.raises(ValueError, match="At least 2 leaf nodes expected."):
        _check_params(X, labels)

def test_full_report_proportions(simple_data):
    """Test the full_report function with proportions=True for both reports."""
    X, labels = simple_data
    report = full_report(X, labels, variance_proportions=True, span_proportions=True)
    
    assert isinstance(report, dict)
    assert len(report) == 2 # Two features
    
    # --- Check Feature 0 ---
    f0_report = report[0]
    assert isinstance(f0_report, FeatureReport)
    assert f0_report.name == 0
    
    # Variance Report (proportional)
    var_rep = f0_report.variance_report
    assert isinstance(var_rep, VarianceReport)
    assert var_rep.is_proportional is True
    assert np.isclose(var_rep.hhi, 0.9803, atol=1e-4)
    assert np.isclose(var_rep.min_variance, 0.0099, atol=1e-4)
    assert np.isclose(var_rep.max_variance, 0.9901, atol=1e-4)

    # Span Report (proportional)
    span_rep = f0_report.span_report
    assert isinstance(span_rep, SpanReport)
    assert span_rep.is_proportional is True
    # Manual calc: span0=[1, 10], total=11, prop=[1/11, 10/11]=[0.09, 0.91], hhi=0.09^2+0.91^2=0.8362
    assert np.isclose(span_rep.hhi, 0.8347, atol=1e-4)
    assert np.isclose(span_rep.min_span, 0.0909, atol=1e-4)
    assert np.isclose(span_rep.max_span, 0.9091, atol=1e-4)

def test_full_report_raw_values(simple_data):
    """Test the full_report function with proportions=False for both reports."""
    X, labels = simple_data
    report = full_report(X, labels, variance_proportions=False, span_proportions=False)
    
    assert isinstance(report, dict)
    
    # --- Check Feature 0 ---
    f0_report = report[0]
    
    # Variance Report (raw)
    var_rep = f0_report.variance_report
    assert var_rep.is_proportional is False
    assert np.isclose(var_rep.hhi, 0.9803, atol=1e-4) # HHI is always on proportions
    assert np.isclose(var_rep.min_variance, 0.25)
    assert np.isclose(var_rep.max_variance, 25.0)

    # Span Report (raw)
    span_rep = f0_report.span_report
    assert span_rep.is_proportional is False
    assert np.isclose(span_rep.hhi, 0.8347, atol=1e-4) # HHI is always on proportions
    assert np.isclose(span_rep.min_span, 1.0) # span([1, 2]) = 1
    assert np.isclose(span_rep.max_span, 10.0) # span([10, 20]) = 10

def test_full_report_zero_variance_and_span():
    """Test full_report handles zero variance and span correctly."""
    X = np.array([
        [5, 10], [5, 10], # Partition 0
        [5, 10], [5, 10]  # Partition 1
    ])
    labels = np.array([0, 0, 1, 1])
    
    report = full_report(X, labels)
    f0_report = report[0]

    # Both variance and span are 0, so HHI should be 0
    assert f0_report.variance_report.hhi == 0.0
    assert f0_report.variance_report.min_variance == 0.0
    assert f0_report.span_report.hhi == 0.0
    assert f0_report.span_report.min_span == 0.0