import os
import sys
import tempfile
import json
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from experiment.scripts.run_sbfl import calculate_tarantula, run_sbfl_for_method

def test_calculate_tarantula():
    # Arrange
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
    
    # Act
    scores = calculate_tarantula(coverage_data, test_results)
    
    # Assert
    assert scores[1] == 0.5
    assert abs(scores[2] - 0.6666) < 0.001
    assert scores[3] == 0.0
    assert scores[4] == 1.0

def test_calculate_tarantula_no_failed():
    # Arrange
    coverage_data = {"test1": [1, 2]}
    test_results = {"test1": "passed"}
    
    # Act
    scores = calculate_tarantula(coverage_data, test_results)
    
    # Assert
    assert scores[1] == 0.0
    assert scores[2] == 0.0

def test_calculate_tarantula_zero_denominator():
    # Arrange
    coverage_data = {}
    test_results = {}
    
    # Act
    scores = calculate_tarantula(coverage_data, test_results)
    
    # Assert
    assert len(scores) == 0

def test_run_sbfl_integration():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, "src")
        tests_dir = os.path.join(tmpdir, "tests")
        dataset_dir = os.path.join(tmpdir, "dataset")
        dataset_buggy_dir = os.path.join(dataset_dir, "buggy")
        
        os.makedirs(src_dir)
        os.makedirs(tests_dir)
        os.makedirs(dataset_buggy_dir)
        
        safe_id = "test_method"
        
        with open(os.path.join(src_dir, f"{safe_id}.py"), "w") as f:
            f.write("def add(a, b):\n    return a + b\n")
            
        with open(os.path.join(dataset_buggy_dir, f"{safe_id}.py"), "w") as f:
            f.write("def add(a, b):\n    if a == 1:\n        return a - b\n    return a + b\n")
            
        with open(os.path.join(tests_dir, f"test_{safe_id}.py"), "w") as f:
            f.write("import sys\nimport os\nsys.path.insert(0, '" + tmpdir.replace("\\", "\\\\") + "')\n")
            f.write(f"from src.{safe_id} import add\n")
            f.write("def test_add_1():\n    assert add(2, 3) == 5\n") 
            f.write("def test_add_2():\n    assert add(1, 1) == 2\n") 
            f.write("def test_add_3():\n    assert add(0, 0) == 0\n") 
            
        original_path = sys.path.copy()
        sys.path.insert(0, tmpdir)
        
        try:
            # Act
            output_data = run_sbfl_for_method(safe_id, src_dir=src_dir, tests_dir=tests_dir, dataset_dir=dataset_dir)
        finally:
            sys.path = original_path
            
        # Assert
        assert output_data is not None
        scores = output_data["tarantula"]
        failing = output_data["failing_tests"]
        
        assert scores[str(3)] == 1.0
        assert scores[str(4)] == 0.0
        assert "test_add_2" in failing
        assert "assert 0 == 2" in failing["test_add_2"]

def test_run_sbfl_for_method_missing_files():
    # Arrange / Act
    result = run_sbfl_for_method("non_existent")
    
    # Assert
    assert result is None

@patch('experiment.scripts.run_sbfl.run_sbfl_for_method')
@patch('experiment.scripts.run_sbfl.os.makedirs')
def test_main(mock_makedirs, mock_run):
    from experiment.scripts.run_sbfl import main
    # Arrange
    mock_meta = json.dumps([{"safe_id": "test_1"}])
    
    with patch('experiment.scripts.run_sbfl.os.path.exists', return_value=False):
        # Act
        main()
        # Assert
        # nothing to assert, should return early
        
    with patch('experiment.scripts.run_sbfl.os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=mock_meta)) as m_open:
            # Arrange
            mock_run.return_value = {"tarantula": {}}
            
            # Act
            main()
            
            # Assert
            assert mock_run.call_count == 1
