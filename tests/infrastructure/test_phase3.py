import os
import json
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))

import generate_prompts
import compute_metrics
import run_llm_evaluation

def test_extract_tests_from_file(tmp_path):
    test_file = tmp_path / "test_dummy.py"
    test_file.write_text("def test_one():\n    pass\n\ndef test_two():\n    pass\n")
    tests = generate_prompts.extract_tests_from_file(str(test_file))
    assert tests == ["test_one", "test_two"]

def test_extract_json_from_text():
    # Valid json directly
    text1 = '{"top_1_line": 10}'
    assert compute_metrics.extract_json_from_text(text1) == {"top_1_line": 10}
    
    # Wrapped in markdown
    text2 = 'Here is the result:\n```json\n{"top_1_line": 12}\n```\nExplanation'
    assert compute_metrics.extract_json_from_text(text2) == {"top_1_line": 12}
    
    # Missing json keyword
    text3 = '```\n{"top_1_line": 15}\n```'
    assert compute_metrics.extract_json_from_text(text3) == {"top_1_line": 15}
    
    # Just conversational but has curly braces
    text4 = 'The answer is {"top_1_line": 20}.'
    assert compute_metrics.extract_json_from_text(text4) == {"top_1_line": 20}
    
    # Invalid json
    text5 = '{"top_1_line": 20' # missing closing
    assert compute_metrics.extract_json_from_text(text5) is None

def test_compute_metrics_logic(tmp_path):
    ground_truth = {
        "dummy_1": {"faulty_line": 10}
    }
    gt_file = tmp_path / "ground_truth.json"
    gt_file.write_text(json.dumps(ground_truth))
    
    results_dir = tmp_path / "results" / "raw_responses"
    model_dir = results_dir / "model_A"
    model_dir.mkdir(parents=True)
    
    # Condition A: correct top 1
    resp_A = {
        "raw_response": '{"top_1_line": 10, "top_3_lines": [10, 11, 12]}'
    }
    (model_dir / "dummy_1_A.json").write_text(json.dumps(resp_A))
    
    # Condition B: correct top 3
    resp_B = {
        "raw_response": '{"top_1_line": 11, "top_3_lines": [11, 10, 12]}'
    }
    (model_dir / "dummy_1_B.json").write_text(json.dumps(resp_B))
    
    # Condition C: region correct (off by 2)
    resp_C = {
        "raw_response": '{"top_1_line": 12, "top_3_lines": [12, 13, 14]}'
    }
    (model_dir / "dummy_1_C.json").write_text(json.dumps(resp_C))
    
    # Condition D: invalid
    resp_D = {
        "raw_response": 'Not a json'
    }
    (model_dir / "dummy_1_D.json").write_text(json.dumps(resp_D))
    
    metrics_out = tmp_path / "metrics.json"
    
    with patch.object(compute_metrics, 'GROUND_TRUTH_FILE', str(gt_file)), \
         patch.object(compute_metrics, 'RESULTS_DIR', str(results_dir)), \
         patch.object(compute_metrics, 'METRICS_OUT', str(metrics_out)):
        
        compute_metrics.compute_metrics()
        
    assert metrics_out.exists()
    metrics = json.loads(metrics_out.read_text())
    
    assert "model_A" in metrics
    model_A_metrics = metrics["model_A"]
    
    assert model_A_metrics["A"]["top_1"] == 1
    assert model_A_metrics["A"]["top_3"] == 1
    assert model_A_metrics["A"]["region"] == 1
    
    assert model_A_metrics["B"]["top_1"] == 0
    assert model_A_metrics["B"]["top_3"] == 1
    assert model_A_metrics["B"]["region"] == 1
    
    assert model_A_metrics["C"]["top_1"] == 0
    assert model_A_metrics["C"]["top_3"] == 0
    assert model_A_metrics["C"]["region"] == 1
    
    assert model_A_metrics["D"]["invalid"] == 1

def test_run_evaluation_logic(tmp_path):
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps(["key1", "key2"]))
    
    meta_file = tmp_path / "meta.json"
    meta_file.write_text(json.dumps([
        {"safe_id": "dummy_1"}
    ]))
    
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    for c in ["A", "B", "C", "D"]:
        (prompts_dir / f"dummy_1_{c}.txt").write_text("prompt")
        
    results_dir = tmp_path / "results"
    
    with patch.object(run_llm_evaluation, 'KEYS_FILE', str(keys_file)), \
         patch.object(run_llm_evaluation, 'DATASET_META', str(meta_file)), \
         patch.object(run_llm_evaluation, 'PROMPTS_DIR', str(prompts_dir)), \
         patch.object(run_llm_evaluation, 'RESULTS_DIR', str(results_dir)), \
         patch.object(run_llm_evaluation, 'MODELS', ["model1"]), \
         patch('time.sleep', return_value=None):
         
         # Mock requests.post
         mock_response_success = MagicMock()
         mock_response_success.status_code = 200
         mock_response_success.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
         
         mock_response_429 = MagicMock()
         mock_response_429.status_code = 429
         mock_response_429.text = "Too many requests"
         
         with patch('requests.post') as mock_post:
             # Condition A: 200 OK
             # Condition B: 429, then 200 OK (minute throttle)
             # Condition C: 429, then 429, then 200 OK (daily limit rotation)
             # Condition D: 500 error
             
             mock_post.side_effect = [
                 mock_response_success, # A
                 
                 mock_response_429, mock_response_success, # B
                 
                 mock_response_429, mock_response_429, mock_response_success, # C
                 
                 MagicMock(status_code=500, text="Internal Server Error") # D
             ]
             
             run_llm_evaluation.run_evaluation()
             
             # Assert results exist
             model_dir = results_dir / "model1"
             assert (model_dir / "dummy_1_A.json").exists()
             assert (model_dir / "dummy_1_B.json").exists()
             assert (model_dir / "dummy_1_C.json").exists()
             assert (model_dir / "dummy_1_D.json").exists()
             
             data_b = json.loads((model_dir / "dummy_1_B.json").read_text())
             assert "429 Too Many Requests (First occurrence)" in data_b["errors"]
             
             data_d = json.loads((model_dir / "dummy_1_D.json").read_text())
             assert "HTTP 500: Internal Server Error" in data_d["errors"]
