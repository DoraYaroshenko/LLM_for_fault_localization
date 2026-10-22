import ast
import sys
import os
import json
import tempfile
from unittest.mock import patch, mock_open

# Add the root directory to path so we can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from experiment.scripts.generate_mutants import MutantGenerator, MUTATIONS_OP as MUTATIONS, mutate_and_test, main

def test_mutations_dictionary():
    # Arrange
    expected_mutations = {
        ast.Add: ast.Sub, ast.Sub: ast.Add,
        ast.Mult: ast.FloorDiv, ast.FloorDiv: ast.Mult,
        ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
        ast.Lt: ast.LtE, ast.LtE: ast.Lt,
        ast.Gt: ast.GtE, ast.GtE: ast.Gt,
        ast.Is: ast.IsNot, ast.IsNot: ast.Is,
        ast.In: ast.NotIn, ast.NotIn: ast.In,
        ast.And: ast.Or, ast.Or: ast.And,
        ast.Mod: ast.Mult
    }
    
    # Act
    # (Checking the dictionary is more of a validation than an act, but we check it)
    mutations_count = len(MUTATIONS)
    
    # Assert
    for orig, mut in expected_mutations.items():
        assert orig in MUTATIONS, f"Missing original operator {orig} in MUTATIONS"
        assert MUTATIONS[orig] == mut, f"Expected {orig} to mutate to {mut}, got {MUTATIONS[orig]}"
    assert mutations_count == len(expected_mutations)

def test_mutant_generator_finds_binop():
    # Arrange
    code = "a = b + c"
    tree = ast.parse(code)
    finder = MutantGenerator()
    
    # Act
    finder.visit(tree)
    
    # Assert
    assert len(finder.mutations_found) == 1
    mut_info = finder.mutations_found[0]
    assert mut_info[0] == 'BinOp'
    assert isinstance(mut_info[1].op, ast.Add)

def test_mutant_generator_finds_compare():
    # Arrange
    code = "if a == b: pass"
    tree = ast.parse(code)
    finder = MutantGenerator()
    
    # Act
    finder.visit(tree)
    
    # Assert
    assert len(finder.mutations_found) == 1
    mut_info = finder.mutations_found[0]
    assert mut_info[0] == 'Compare'
    assert isinstance(mut_info[1].ops[mut_info[2]], ast.Eq)

def test_mutant_generator_finds_boolop():
    # Arrange
    code = "if a and b: pass"
    tree = ast.parse(code)
    finder = MutantGenerator()
    
    # Act
    finder.visit(tree)
    
    # Assert
    assert len(finder.mutations_found) == 1
    mut_info = finder.mutations_found[0]
    assert mut_info[0] == 'BoolOp'
    assert isinstance(mut_info[1].op, ast.And)

def test_mutate_and_test_integration():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "sample.py")
        test_file = os.path.join(tmpdir, "test_sample.py")
        
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("def add(a, b):\n    return a + b\n")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("from sample import add\ndef test_add():\n    assert add(2, 3) == 5\n")
            
        original_sys_path = sys.path.copy()
        sys.path.insert(0, tmpdir)
        
        try:
            # Act
            result = mutate_and_test(src_file, test_file)
            
            # Assert
            assert result is not None
            assert "return a - b" in result["mutated_code"]
            assert result["faulty_line"] == 2
        finally:
            sys.path = original_sys_path

def test_mutate_and_test_compare_integration():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "sample.py")
        test_file = os.path.join(tmpdir, "test_sample.py")
        
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("def eq(a, b):\n    return a == b\n")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("from sample import eq\ndef test_eq():\n    assert eq(2, 2) is True\n")
        
        original_sys_path = sys.path.copy()
        sys.path.insert(0, tmpdir)
        
        try:
            # Act
            result = mutate_and_test(src_file, test_file)
            
            # Assert
            assert result is not None
            assert "return a != b" in result["mutated_code"]
            assert result["faulty_line"] == 2
        finally:
            sys.path = original_sys_path

def test_mutate_and_test_boolop_integration():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "sample.py")
        test_file = os.path.join(tmpdir, "test_sample.py")
        
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("def both(a, b):\n    return a and b\n")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("from sample import both\ndef test_both():\n    assert both(True, False) is False\n")
        
        original_sys_path = sys.path.copy()
        sys.path.insert(0, tmpdir)
        
        try:
            # Act
            result = mutate_and_test(src_file, test_file)
            
            # Assert
            assert result is not None
            assert "return a or b" in result["mutated_code"]
            assert result["faulty_line"] == 2
        finally:
            sys.path = original_sys_path

def test_mutate_and_test_no_mutant():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "sample.py")
        test_file = os.path.join(tmpdir, "test_sample.py")
        
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("def none():\n    pass\n")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("from sample import none\ndef test_none():\n    assert none() is None\n")
            
        original_sys_path = sys.path.copy()
        sys.path.insert(0, tmpdir)
        
        try:
            # Act
            result = mutate_and_test(src_file, test_file)
            
            # Assert
            assert result is None
        finally:
            sys.path = original_sys_path

@patch('experiment.scripts.generate_mutants.mutate_and_test')
@patch('experiment.scripts.generate_mutants.os.makedirs')
@patch('experiment.scripts.generate_mutants.json.dump')
def test_main(mock_json_dump, mock_makedirs, mock_mutate_and_test):
    # Arrange
    mock_meta = '[{"safe_id": "test_1", "entry_point": "f1", "task_id": "t1"}, {"safe_id": "test_2", "entry_point": "f2", "task_id": "t2"}]'
    mock_mutate_and_test.side_effect = [
        {"mutated_code": "def f1(): pass", "faulty_line": 1, "passed": 0, "failed": 1, "total": 1, "bug_type": "unknown"},
        None
    ]
    
    with patch('builtins.open', mock_open(read_data=mock_meta)) as m_open:
        # Act
        main()
        
        # Assert
        mock_makedirs.assert_called_once_with('experiment/dataset/buggy', exist_ok=True)
        assert mock_json_dump.call_count == 3

def test_target_mutator_branches():
    # Arrange
    code = "a = b | c\nif a > b and b < c: pass\nif a is b: pass"
    tree = ast.parse(code)
    finder = MutantGenerator()
    
    # Act
    finder.visit(tree)
    
    # Assert
    # This covers unsupported BinOp (BitOr), Compare (Gt, Lt, Is), BoolOp (And)
    # The coverage is achieved implicitly by running it.
    
    # Arrange for test_mutate_and_test passing
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "sample.py")
        test_file = os.path.join(tmpdir, "test_sample.py")
        
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("def add(a, b):\n    return a + b\n")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("from sample import add\ndef test_add():\n    assert True\n")
            
        original_sys_path = sys.path.copy()
        sys.path.insert(0, tmpdir)
        try:
            # Act
            result = mutate_and_test(src_file, test_file)
            
            # Assert
            assert result is None # because test still passes
        finally:
            sys.path = original_sys_path

@patch('experiment.scripts.generate_mutants.mutate_and_test')
@patch('experiment.scripts.generate_mutants.os.makedirs')
@patch('experiment.scripts.generate_mutants.json.dump')
def test_main_break(mock_json_dump, mock_makedirs, mock_mutate_and_test):
    # Arrange
    mock_meta = json.dumps([{"safe_id": f"test_{i}", "entry_point": "f1", "task_id": "t1"} for i in range(31)])
    mock_mutate_and_test.return_value = {"mutated_code": "def f1(): pass", "faulty_line": 1, "passed": 0, "failed": 1, "total": 1, "bug_type": "unknown"}
    
    with patch('builtins.open', mock_open(read_data=mock_meta)) as m_open:
        # Act
        main()
        
        # Assert
        assert mock_mutate_and_test.call_count == 30
