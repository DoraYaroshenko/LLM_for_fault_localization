import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from scripts.run_sbfl import calculate_tarantula, run_sbfl_for_method

def test_calculate_tarantula():
    # Setup dummy coverage data
    # Test 1 (passed): covered lines [1, 2, 3]
    # Test 2 (failed): covered lines [1, 2, 4]
    # Test 3 (passed): covered lines [1, 3]
    
    coverage_data = {
        "test1": [1, 2, 3],
        "test2": [1, 2, 4],
        "test3": [1, 3]
    }
    
    test_results = {
        "test1": "passed",
        "test2": "failed",
        "test3": "passed"
    }
    
    scores = calculate_tarantula(coverage_data, test_results)
    
    # Total failed = 1, Total passed = 2
    # Line 1: passed_s = 2, failed_s = 1. ratio_failed = 1/1 = 1.0, ratio_passed = 2/2 = 1.0. Suspiciousness = 1.0 / (1.0 + 1.0) = 0.5
    # Line 2: passed_s = 1, failed_s = 1. ratio_failed = 1.0, ratio_passed = 1/2 = 0.5. Suspiciousness = 1.0 / (1.0 + 0.5) = 0.666...
    # Line 3: passed_s = 2, failed_s = 0. ratio_failed = 0.0, ratio_passed = 1.0. Suspiciousness = 0.0
    # Line 4: passed_s = 0, failed_s = 1. ratio_failed = 1.0, ratio_passed = 0.0. Suspiciousness = 1.0
    
    assert scores[1] == 0.5
    assert abs(scores[2] - 0.6666) < 0.001
    assert scores[3] == 0.0
    assert scores[4] == 1.0

def test_calculate_tarantula_no_failed():
    coverage_data = {"test1": [1, 2]}
    test_results = {"test1": "passed"}
    scores = calculate_tarantula(coverage_data, test_results)
    assert scores[1] == 0.0
    assert scores[2] == 0.0

def test_calculate_tarantula_zero_denominator():
    # Edge case where line wasn't executed by pass or fail, shouldn't happen based on code logic since all_lines is union, but good to test
    # Actually just pass empty dict
    scores = calculate_tarantula({}, {})
    assert len(scores) == 0

def test_run_sbfl_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock structure
        src_dir = os.path.join(tmpdir, "src")
        tests_dir = os.path.join(tmpdir, "tests")
        dataset_dir = os.path.join(tmpdir, "dataset")
        dataset_buggy_dir = os.path.join(dataset_dir, "buggy")
        
        os.makedirs(src_dir)
        os.makedirs(tests_dir)
        os.makedirs(dataset_buggy_dir)
        
        safe_id = "test_method"
        
        # Original src
        with open(os.path.join(src_dir, f"{safe_id}.py"), "w") as f:
            f.write("def add(a, b):\n    return a + b\n")
            
        # Buggy
        with open(os.path.join(dataset_buggy_dir, f"{safe_id}.py"), "w") as f:
            f.write("def add(a, b):\n    if a == 1:\n        return a - b\n    return a + b\n")
            
        # Test
        with open(os.path.join(tests_dir, f"test_{safe_id}.py"), "w") as f:
            f.write("import sys\nimport os\nsys.path.insert(0, '" + tmpdir.replace("\\", "\\\\") + "')\n")
            f.write(f"from src.{safe_id} import add\n")
            f.write("def test_add_1():\n    assert add(2, 3) == 5\n") # Pass
            f.write("def test_add_2():\n    assert add(1, 1) == 2\n") # Fail, covers line 3
            f.write("def test_add_3():\n    assert add(0, 0) == 0\n") # Pass
            
        # Add tmpdir to path temporarily
        original_path = sys.path.copy()
        sys.path.insert(0, tmpdir)
        try:
            output_data = run_sbfl_for_method(safe_id, src_dir=src_dir, tests_dir=tests_dir, dataset_dir=dataset_dir)
        finally:
            sys.path = original_path
            
        print("OUTPUT:", output_data)
        assert output_data is not None
        
        scores = output_data["tarantula"]
        failing = output_data["failing_tests"]
        
        # line 2 (if a == 1) should be executed by all. Score = 0.5
        # line 3 (return a - b) executed by test 2. ratio_failed=1.0, ratio_passed=0.0 -> Score 1.0
        # line 4 (return a + b) executed by test 1 and 3. ratio_failed=0.0, ratio_passed=1.0 -> Score 0.0
        
        assert scores[str(3)] == 1.0
        assert scores[str(4)] == 0.0
        
        assert "test_add_2" in failing
        assert "assert 0 == 2" in failing["test_add_2"]
