import pandas as pd
import numpy as np
import os
import shutil

# Assuming tests are run from the project root and the package is installed in editable mode
from src.hvrt import HVRTPartitioner, PartitionProfiler

def test_profiler_output_generation_for_manual_review():
    """
    Tests that the PartitionProfiler correctly creates output files and directories.
    This test saves artifacts to a permanent directory for manual inspection.
    It is recommended to add 'test_outputs/' to your .gitignore file.
    """
    # 1. Define a permanent output directory
    output_dir = "test_outputs/profiler_output"

    # 2. Ensure a clean state before the test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # 3. Create synthetic data
    data_size = 1000
    X = pd.DataFrame({
        'feature_A': np.random.randn(data_size) * 10,
        'feature_B': np.random.rand(data_size) * 5,
        'feature_C': np.random.gamma(2, 2, data_size),
    })

    # 4. Create partitions (using the corrected method calls)
    partitioner = HVRTPartitioner(max_leaf_nodes=51)
    partitioner.fit(X)
    labels = partitioner.get_partitions(X)

    # 5. Run the PartitionProfiler with the output_path
    profiler = PartitionProfiler(
        data=X, 
        partition_labels=pd.Series(labels, index=X.index), 
        output_path=output_dir
    )
    profiler.run_profiling()

    # 6. Assert that files and directories were created
    print(f"\nVerifying output in: {os.path.abspath(output_dir)}")
    assert os.path.exists(output_dir)
    assert os.path.isfile(os.path.join(output_dir, "feature_summary.csv"))
    assert os.path.isfile(os.path.join(output_dir, "partition_size_distribution.png"))

    # Check for a feature-specific subdirectory and its contents
    feature_a_dir = os.path.join(output_dir, "feature_A")
    assert os.path.isdir(feature_a_dir)
    assert os.path.isfile(os.path.join(feature_a_dir, "feature_distribution_trend.png"))
    
    # Check that at least one of the data csvs exists
    variance_files = [f for f in os.listdir(feature_a_dir) if f.endswith("_variance_distribution.csv")]
    assert len(variance_files) > 0, "Variance distribution CSV not found."

    span_files = [f for f in os.listdir(feature_a_dir) if f.endswith("_span_distribution.csv")]
    assert len(span_files) > 0, "Span distribution CSV not found."
    
    print("Assertions passed. Artifacts are available for manual review.")