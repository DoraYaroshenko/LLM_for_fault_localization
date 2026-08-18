import os
import shutil
import json
import subprocess
import sys

def calculate_tarantula(coverage_data, test_results):
    total_passed = sum(1 for res in test_results.values() if res == 'passed')
    total_failed = sum(1 for res in test_results.values() if res == 'failed')
    
    line_passed = {}
    line_failed = {}
    
    for test, lines in coverage_data.items():
        res = test_results.get(test)
        if res not in ('passed', 'failed'):
            continue
        if lines is None:
            lines = []
        for line in lines:
            if res == 'passed':
                line_passed[line] = line_passed.get(line, 0) + 1
            else:
                line_failed[line] = line_failed.get(line, 0) + 1
                
    all_lines = set(line_passed.keys()).union(set(line_failed.keys()))
    
    scores = {}
    for line in all_lines:
        passed_s = line_passed.get(line, 0)
        failed_s = line_failed.get(line, 0)
        
        if total_failed == 0:
            scores[line] = 0.0
            continue
            
        ratio_failed = failed_s / total_failed
        ratio_passed = passed_s / total_passed if total_passed > 0 else 0
        
        denominator = ratio_passed + ratio_failed
        if denominator == 0:
            scores[line] = 0.0
        else:
            scores[line] = ratio_failed / denominator
            
    return scores

def run_sbfl_for_method(safe_id, src_dir="src", tests_dir="tests", dataset_dir="dataset"):
    src_file = os.path.join(src_dir, f"{safe_id}.py")
    buggy_file = os.path.join(dataset_dir, "buggy", f"{safe_id}.py")
    test_file = os.path.join(tests_dir, f"test_{safe_id}.py")
    
    if not os.path.exists(buggy_file) or not os.path.exists(test_file):
        return None
        
    backup_file = src_file + ".bak"
    if os.path.exists(src_file):
        shutil.copy(src_file, backup_file)
    
    output_data = None
    try:
        shutil.copy(buggy_file, src_file)
        
        runner_script = os.path.join("scripts", "sbfl_runner.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.abspath(src_dir))
        
        subprocess.run(
            [sys.executable, runner_script, safe_id, src_file, test_file],
            env=env
        )
        
        if os.path.exists("sbfl_runner_out.json"):
            with open("sbfl_runner_out.json", "r") as f:
                runner_out = json.load(f)
                
            test_results = runner_out.get("results", {})
            failing_details = runner_out.get("failing_details", {})
            coverage_data = runner_out.get("coverage", {})
            
            tarantula = calculate_tarantula(coverage_data, test_results)
            str_tarantula = {str(k): v for k, v in sorted(tarantula.items(), key=lambda x: x[1], reverse=True)}
            
            output_data = {
                "tarantula": str_tarantula,
                "failing_tests": failing_details
            }
            
    finally:
        if os.path.exists(backup_file):
            shutil.copy(backup_file, src_file)
            os.remove(backup_file)
        if os.path.exists("sbfl_runner_out.json"):
            os.remove("sbfl_runner_out.json")
        if os.path.exists(".coverage"):
            os.remove(".coverage")
        
    return output_data

def main():
    metadata_path = os.path.join("dataset", "final_metadata.json")
    if not os.path.exists(metadata_path):
        print(f"File {metadata_path} not found.")
        return
        
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        
    sbfl_dir = os.path.join("dataset", "sbfl")
    os.makedirs(sbfl_dir, exist_ok=True)
    
    for item in metadata:
        safe_id = item["safe_id"]
        print(f"Running SBFL for {safe_id}...")
        output_data = run_sbfl_for_method(safe_id)
        if output_data is not None:
            with open(os.path.join(sbfl_dir, f"{safe_id}.json"), "w") as f:
                json.dump(output_data, f, indent=2)
                
    print("SBFL generation completed.")

if __name__ == "__main__":
    main()
