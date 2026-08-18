import ast
import sys
import os

# Add the root directory to path so we can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from scripts.generate_mutants import MutantGenerator, MUTATIONS

def test_mutations_dictionary():
    # Exhaustively test all mapped mutation pairs
    expected_mutations = {
        ast.Add: ast.Sub,
        ast.Sub: ast.Add,
        ast.Mult: ast.FloorDiv,
        ast.FloorDiv: ast.Mult,
        ast.Eq: ast.NotEq,
        ast.NotEq: ast.Eq,
        ast.Lt: ast.LtE,
        ast.LtE: ast.Lt,
        ast.Gt: ast.GtE,
        ast.GtE: ast.Gt,
        ast.Is: ast.IsNot,
        ast.IsNot: ast.Is,
        ast.In: ast.NotIn,
        ast.NotIn: ast.In,
        ast.And: ast.Or,
        ast.Or: ast.And,
        ast.Mod: ast.Mult
    }
    
    # Check that all expected mutations exist and are correct
    for orig, mut in expected_mutations.items():
        assert orig in MUTATIONS, f"Missing original operator {orig} in MUTATIONS"
        assert MUTATIONS[orig] == mut, f"Expected {orig} to mutate to {mut}, got {MUTATIONS[orig]}"
        
    # Ensure there are no unexpected extra mutations
    assert len(MUTATIONS) == len(expected_mutations)

def test_mutant_generator_finds_binop():
    code = "a = b + c"
    tree = ast.parse(code)
    finder = MutantGenerator()
    finder.visit(tree)
    
    assert len(finder.mutations_found) == 1
    mut_info = finder.mutations_found[0]
    assert mut_info[0] == 'BinOp'
    assert isinstance(mut_info[1].op, ast.Add)

def test_mutant_generator_finds_compare():
    code = "if a == b: pass"
    tree = ast.parse(code)
    finder = MutantGenerator()
    finder.visit(tree)
    
    assert len(finder.mutations_found) == 1
    mut_info = finder.mutations_found[0]
    assert mut_info[0] == 'Compare'
    assert isinstance(mut_info[1].ops[mut_info[2]], ast.Eq)

def test_mutant_generator_finds_boolop():
    code = "if a and b: pass"
    tree = ast.parse(code)
    finder = MutantGenerator()
    finder.visit(tree)
    
    assert len(finder.mutations_found) == 1
    mut_info = finder.mutations_found[0]
    assert mut_info[0] == 'BoolOp'
    assert isinstance(mut_info[1].op, ast.And)

import tempfile

def test_mutate_and_test_integration():
    from scripts.generate_mutants import mutate_and_test
    
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
            result = mutate_and_test(src_file, test_file)
            assert result is not None
            assert "return a - b" in result["mutated_code"]
            assert result["faulty_line"] == 2
        finally:
            sys.path = original_sys_path

def test_mutate_and_test_compare_integration():
    from scripts.generate_mutants import mutate_and_test
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
            result = mutate_and_test(src_file, test_file)
            assert result is not None
            assert "return a != b" in result["mutated_code"]
            assert result["faulty_line"] == 2
        finally:
            sys.path = original_sys_path

def test_mutate_and_test_boolop_integration():
    from scripts.generate_mutants import mutate_and_test
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
            result = mutate_and_test(src_file, test_file)
            assert result is not None
            assert "return a or b" in result["mutated_code"]
            assert result["faulty_line"] == 2
        finally:
            sys.path = original_sys_path

def test_mutate_and_test_no_mutant():
    from scripts.generate_mutants import mutate_and_test
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "sample.py")
        test_file = os.path.join(tmpdir, "test_sample.py")
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("def none():\n    return 0\n")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("from sample import none\ndef test_none():\n    assert none() == 0\n")
            
        original_sys_path = sys.path.copy()
        sys.path.insert(0, tmpdir)
        try:
            result = mutate_and_test(src_file, test_file)
            assert result is None
        finally:
            sys.path = original_sys_path

from unittest.mock import patch, mock_open

@patch('scripts.generate_mutants.mutate_and_test')
@patch('scripts.generate_mutants.os.makedirs')
@patch('scripts.generate_mutants.json.dump')
def test_main(mock_json_dump, mock_makedirs, mock_mutate_and_test):
    from scripts.generate_mutants import main
    mock_meta = '[{"safe_id": "test_1", "entry_point": "f1", "task_id": "t1"}, {"safe_id": "test_2", "entry_point": "f2", "task_id": "t2"}]'
    
    with patch('builtins.open', mock_open(read_data=mock_meta)) as m_open:
        mock_mutate_and_test.side_effect = [
            {"mutated_code": "def f1(): pass", "faulty_line": 1},
            None
        ]
        main()
        
        mock_makedirs.assert_called_once_with('dataset/buggy', exist_ok=True)
        assert mock_json_dump.call_count == 2
