import os
import json
import pytest
from experiment.scripts.run_sbfl import calculate_tarantula
from experiment.scripts.compute_metrics import extract_json_from_text
from experiment.scripts.generate_mutants import count_test_failures, get_bug_type_description
import ast

# ---------------------------------------------------------
# Test Mutation Generation (and Coverage mapping indirectly)
# ---------------------------------------------------------
def test_get_bug_type_description():
    # Arrange & Act
    desc = get_bug_type_description("BinOp", ast.Add)
    # Assert
    assert desc == "arithmetic_operator_change (Add)"

    # Arrange & Act
    desc_cmp = get_bug_type_description("Compare", ast.Lt)
    # Assert
    assert desc_cmp == "boundary_condition_change (Lt)"

def test_count_test_failures_non_existent_file():
    # Arrange & Act
    passed, failed, ret_code = count_test_failures("non_existent_test_file_for_testing.py")
    # Assert
    assert passed == 0
    assert failed == 1 # Error running pytest defaults to failed=1

# ---------------------------------------------------------
# Test SBFL Computation Code
# ---------------------------------------------------------
def test_calculate_tarantula():
    # Arrange
    coverage_data = {
        "test_1": [10, 11, 12],
        "test_2": [10, 12, 13],
        "test_3": [10, 11]
    }
    test_results = {
        "test_1": "passed",
        "test_2": "failed",
        "test_3": "passed"
    }
    
    # Act
    scores = calculate_tarantula(coverage_data, test_results)
    
    # Assert
    # total_failed = 1, total_passed = 2
    # line 10: passed = 2, failed = 1 -> ratio_failed = 1/1=1.0, ratio_passed = 2/2=1.0. score = 1.0 / (1.0 + 1.0) = 0.5
    # line 12: passed = 1, failed = 1 -> ratio_failed = 1.0, ratio_passed = 0.5. score = 1.0 / 1.5 = 0.666
    # line 13: passed = 0, failed = 1 -> ratio_failed = 1.0, ratio_passed = 0.0. score = 1.0 / 1.0 = 1.0
    # line 11: passed = 2, failed = 0 -> ratio_failed = 0.0, ratio_passed = 1.0. score = 0.0
    
    assert round(scores[10], 2) == 0.50
    assert round(scores[12], 2) == 0.67
    assert scores[13] == 1.0
    assert scores[11] == 0.0

# ---------------------------------------------------------
# Test Result Computation & Output Parsing Code
# ---------------------------------------------------------
def test_extract_json_from_text_valid_json():
    # Arrange
    text = '''Some explanation
    ```json
    {
      "top_1_line": 15,
      "top_3_lines": [15, 16],
      "faulty_region": "condition"
    }
    ```
    '''
    # Act
    result = extract_json_from_text(text)
    # Assert
    assert result is not None
    assert result["top_1_line"] == 15
    assert result["faulty_region"] == "condition"

def test_extract_json_from_text_no_markdown():
    # Arrange
    text = '{"top_1_line": 10, "top_3_lines": [10, 12]}'
    # Act
    result = extract_json_from_text(text)
    # Assert
    assert result is not None
    assert result["top_1_line"] == 10

def test_extract_json_from_text_invalid():
    # Arrange
    text = "This is just text with no json"
    # Act
    result = extract_json_from_text(text)
    # Assert
    assert result is None

# ---------------------------------------------------------
# Test Metrics-Computation Code
# ---------------------------------------------------------
def test_metrics_computation_logic():
    # Testing the rank/MRR calculation logic directly
    # Arrange
    gt_line = 42
    top_1 = 42
    top_3 = [42, 43, 44]
    
    # Act
    is_top_1 = (top_1 == gt_line)
    is_top_3 = (gt_line in top_3)
    is_region = abs(top_1 - gt_line) <= 2
    
    rank = 1 if is_top_1 else (top_3.index(gt_line) + 1 if gt_line in top_3 else 0)
    mrr = 1.0 / rank if rank > 0 else 0.0
    
    # Assert
    assert is_top_1 is True
    assert is_top_3 is True
    assert is_region is True
    assert rank == 1
    assert mrr == 1.0

# ---------------------------------------------------------
# Test HTML Generation logic
# ---------------------------------------------------------
def test_html_table_generation():
    # Arrange
    metadata = [{"task_id": "test_1", "entry_point": "func", "num_tests": 10}]
    
    # Act
    dataset_table_html = "<table>\n<tr><th>Task ID</th><th>Entry Point</th><th>Number of Tests</th></tr>\n"
    for m in metadata:
        dataset_table_html += f"<tr><td>{m['task_id']}</td><td><code>{m['entry_point']}</code></td><td>{m['num_tests']}</td></tr>\n"
    dataset_table_html += "</table>"
    
    # Assert
    assert "<td>test_1</td>" in dataset_table_html
    assert "<td>10</td>" in dataset_table_html
