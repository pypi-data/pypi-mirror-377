import pytest
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer

from src.hvrt.partitioner import HVRTPartitioner

sample_data = np.random.rand(100, 10)

def test_partitioner_init():
    """Test the initialization of the HVRTPartitioner."""
    partitioner = HVRTPartitioner(max_leaf_nodes=50, random_state=123)
    assert partitioner.max_leaf_nodes == 50
    assert partitioner.tree_ is None
    assert partitioner.scaler_ is None
    assert partitioner.tree_kwargs["random_state"] == 123

def test_fit_and_get_partitions():
    """Test the fit and get_partitions methods."""
    partitioner = HVRTPartitioner(max_leaf_nodes=20)
    partitioner.fit(sample_data)
    
    assert partitioner.tree_ is not None
    assert partitioner.scaler_ is not None
    
    partitions = partitioner.get_partitions(sample_data)
    assert isinstance(partitions, np.ndarray)
    assert partitions.shape == (100,)
    assert len(np.unique(partitions)) <= 20

def test_get_partitions_before_fit():
    """Test that get_partitions raises an error if called before fit."""
    partitioner = HVRTPartitioner()
    with pytest.raises(RuntimeError, match="The partitioner has not been fitted yet"):
        partitioner.get_partitions(sample_data)

def test_invalid_input_type():
    """Test that fit raises a ValueError for invalid input types."""
    partitioner = HVRTPartitioner()
    with pytest.raises(ValueError, match="Input data X must be a pandas DataFrame or a numpy array"):
        partitioner.fit([1, 2, 3])

def test_max_leaf_nodes_constraint():
    """Test that the number of partitions respects max_leaf_nodes."""
    max_leaves = 10
    partitioner = HVRTPartitioner(max_leaf_nodes=max_leaves)
    partitioner.fit(sample_data)
    partitions = partitioner.get_partitions(sample_data)
    assert len(np.unique(partitions)) <= max_leaves

def test_weights_influence_partitioning():
    """
    Test that weights correctly influence the partitioning outcome.
    
    We create a dataset with two distinct groups. Without weights, the partitioner
    should split them based on overall variance. With a high weight on a specific
    feature, the partitioner should prioritize splitting based on that feature.
    """
    # Create a dataset where feature 0 is the clearest separator
    X = np.zeros((100, 2))
    X[:50, 0] = 10  # Group 1, feature 0
    X[50:, 0] = -10 # Group 2, feature 0
    X[:, 1] = np.random.uniform(-1, 1, 100) # Add some noise to feature 1

    # Case 1: No weights
    partitioner_unweighted = HVRTPartitioner(max_leaf_nodes=2)
    partitioner_unweighted.fit(X)
    partitions_unweighted = partitioner_unweighted.get_partitions(X)
    
    # Expect two distinct partitions for the two groups
    assert len(np.unique(partitions_unweighted)) == 2
    # All members of group 1 should be in one partition, and all of group 2 in the other
    assert len(np.unique(partitions_unweighted[:50])) == 1
    assert len(np.unique(partitions_unweighted[50:])) == 1
    assert partitions_unweighted[0] != partitions_unweighted[50]

    # Case 2: Heavy weight on the noisy feature (feature 1)
    # This should force the partitioner to split based on the noise, ignoring the clear separator.
    partitioner_weighted = HVRTPartitioner(max_leaf_nodes=2, weights={1: 1000.0})
    partitioner_weighted.fit(X)
    partitions_weighted = partitioner_weighted.get_partitions(X)
    
    # The partitions should now be different from the unweighted case
    # and likely mixed due to the focus on the noisy feature.
    assert not np.array_equal(partitions_unweighted, partitions_weighted)
    
    # It's hard to predict the exact split, but it's highly unlikely that
    # the original clean separation will be preserved.
    # We can check if the original groups are now mixed across partitions.
    assert len(np.unique(partitions_weighted[:50])) > 1 or len(np.unique(partitions_weighted[50:])) > 1

def test_pandas_dataframe_input():
    """Test that the partitioner works correctly with a pandas DataFrame."""
    df = pd.DataFrame(sample_data, columns=[f'col_{i}' for i in range(10)])
    partitioner = HVRTPartitioner(max_leaf_nodes=15)
    partitioner.fit(df)
    partitions = partitioner.get_partitions(df)
    assert isinstance(partitions, np.ndarray)
    assert partitions.shape == (100,)
    assert len(np.unique(partitions)) <= 15


@pytest.fixture
def mixed_type_data():
    """Fixture for a DataFrame with mixed continuous and categorical data."""
    data = {
        'cont_1': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        'cont_2': [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
        'cat_1': ['A', 'B', 'A', 'B', 'C', 'C'],
        'cat_2': ['X', 'X', 'Y', 'Y', 'Z', 'Z']
    }
    return pd.DataFrame(data)


def test_partitioner_with_mixed_types(mixed_type_data):
    """Test that the partitioner handles mixed data types correctly with scikit-learn."""
    partitioner = HVRTPartitioner(max_leaf_nodes=3)
    partitioner.fit(mixed_type_data)

    # Check that a ColumnTransformer was created
    assert partitioner.encoder_ is not None
    assert isinstance(partitioner.encoder_, ColumnTransformer)

    # Check that partitions are generated
    partitions = partitioner.get_partitions(mixed_type_data)
    assert isinstance(partitions, np.ndarray)
    assert partitions.shape == (6,)
    assert len(np.unique(partitions)) <= 3

    # Test with unseen category
    new_data = mixed_type_data.copy()
    new_data.loc[4, 'cat_1'] = 'D'  # 'D' is unseen

    # scikit-learn's TargetEncoder handles unseen categories by encoding them as the target mean
    new_partitions = partitioner.get_partitions(new_data)
    assert isinstance(new_partitions, np.ndarray)
    assert new_partitions.shape == (6,)
