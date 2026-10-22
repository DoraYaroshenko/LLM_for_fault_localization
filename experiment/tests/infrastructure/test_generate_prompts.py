import pytest
import os
import json

import experiment.scripts.generate_prompts as gen_prompts

def test_extract_full_test_code_exists(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding='utf-8')
    assert gen_prompts.extract_full_test_code(str(test_file)) == "print('hello')"

def test_extract_full_test_code_not_exists(tmp_path):
    test_file = tmp_path / "not_exists.py"
    assert gen_prompts.extract_full_test_code(str(test_file)) == ""

def test_generate_prompts(monkeypatch, tmp_path):
    # Set up temporary directories
    dataset_dir = tmp_path / "dataset"
    buggy_dir = tmp_path / "dataset" / "buggy"
    sbfl_dir = tmp_path / "dataset" / "sbfl"
    tests_dir = tmp_path / "tests"
    prompts_dir = tmp_path / "prompts"
    
    dataset_dir.mkdir(parents=True)
    buggy_dir.mkdir(parents=True)
    sbfl_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)
    
    meta_file = dataset_dir / "final_metadata.json"
    
    # Mock data
    meta_data = [{"safe_id": "test_1"}]
    meta_file.write_text(json.dumps(meta_data), encoding='utf-8')
    
    buggy_file = buggy_dir / "test_1.py"
    buggy_file.write_text("def foo():\n    pass\n", encoding='utf-8')
    
    sbfl_file = sbfl_dir / "test_1.json"
    sbfl_data = {
        "tarantula": {"1": 0.5, "2": 1.0},
        "failing_tests": {"test_foo": "AssertionError: \n  x != y"}
    }
    sbfl_file.write_text(json.dumps(sbfl_data), encoding='utf-8')
    
    test_file = tests_dir / "test_test_1.py"
    test_file.write_text("def test_foo():\n    assert False", encoding='utf-8')
    
    monkeypatch.setattr(gen_prompts, "DATASET_META", str(meta_file))
    monkeypatch.setattr(gen_prompts, "BUGGY_DIR", str(buggy_dir))
    monkeypatch.setattr(gen_prompts, "SBFL_DIR", str(sbfl_dir))
    monkeypatch.setattr(gen_prompts, "TESTS_DIR", str(tests_dir))
    monkeypatch.setattr(gen_prompts, "PROMPTS_DIR", str(prompts_dir))
    
    gen_prompts.generate_prompts()
    
    assert prompts_dir.exists()
    assert (prompts_dir / "test_1_A.txt").exists()
    assert (prompts_dir / "test_1_B.txt").exists()
    assert (prompts_dir / "test_1_C.txt").exists()
    assert (prompts_dir / "test_1_D.txt").exists()
    
    # Check content of one prompt
    prompt_D = (prompts_dir / "test_1_D.txt").read_text(encoding='utf-8')
    assert "1: def foo()" in prompt_D
    assert "2:     pass" in prompt_D
    assert "def test_foo():" in prompt_D
    assert "AssertionError:" in prompt_D
    assert "Line 2: 1.000" in prompt_D
    assert "Line 1: 0.500" in prompt_D

def test_generate_prompts_no_failing_tests(monkeypatch, tmp_path):
    # Set up temporary directories
    dataset_dir = tmp_path / "dataset"
    buggy_dir = tmp_path / "dataset" / "buggy"
    sbfl_dir = tmp_path / "dataset" / "sbfl"
    tests_dir = tmp_path / "tests"
    prompts_dir = tmp_path / "prompts"
    
    dataset_dir.mkdir(parents=True)
    buggy_dir.mkdir(parents=True)
    sbfl_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)
    
    meta_file = dataset_dir / "final_metadata.json"
    
    # Mock data
    meta_data = [{"safe_id": "test_2"}]
    meta_file.write_text(json.dumps(meta_data), encoding='utf-8')
    
    buggy_file = buggy_dir / "test_2.py"
    buggy_file.write_text("def foo():\n    pass\n", encoding='utf-8')
    
    sbfl_file = sbfl_dir / "test_2.json"
    sbfl_data = {
        "tarantula": {"1": 0.5},
        "failing_tests": {}
    }
    sbfl_file.write_text(json.dumps(sbfl_data), encoding='utf-8')
    
    test_file = tests_dir / "test_test_2.py"
    test_file.write_text("def test_foo():\n    assert True", encoding='utf-8')
    
    monkeypatch.setattr(gen_prompts, "DATASET_META", str(meta_file))
    monkeypatch.setattr(gen_prompts, "BUGGY_DIR", str(buggy_dir))
    monkeypatch.setattr(gen_prompts, "SBFL_DIR", str(sbfl_dir))
    monkeypatch.setattr(gen_prompts, "TESTS_DIR", str(tests_dir))
    monkeypatch.setattr(gen_prompts, "PROMPTS_DIR", str(prompts_dir))
    
    gen_prompts.generate_prompts()
    
    prompt_D = (prompts_dir / "test_2_D.txt").read_text(encoding='utf-8')
    assert "The following tests failed with these errors:" not in prompt_D
