import os
import sys

# Ensure we can import from experiment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from experiment.scripts.generate_mutants import count_test_failures

def generate_report():
    buggy_dir = "experiment/dataset/buggy"
    original_dir = "experiment/src"
    
    mutants = [f for f in os.listdir(buggy_dir) if f.endswith('.py')]
    mutants.sort(key=lambda x: int(x.split('_')[1].split('.')[0])) # sort by number
    
    report_lines = [
        "# Test Results Report: Originals vs Mutants",
        "",
        "| Task ID | Original Passed | Original Failed | Mutant Passed | Mutant Failed |",
        "|---------|-----------------|-----------------|---------------|---------------|"
    ]
    
    for mutant in mutants:
        safe_id = mutant.replace('.py', '')
        src_path = os.path.join("src", mutant)
        buggy_path = os.path.join(buggy_dir, mutant)
        original_path = os.path.join(original_dir, mutant)
        test_path = os.path.join("tests", f"test_{safe_id}.py")
        
        # Read files
        with open(original_path, "r", encoding="utf-8") as f:
            original_code = f.read()
        with open(buggy_path, "r", encoding="utf-8") as f:
            buggy_code = f.read()
            
        try:
            # 1. Test original
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(original_code)
            orig_passed, orig_failed, _ = count_test_failures(test_path)
            
            # 2. Test mutant
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(buggy_code)
            mut_passed, mut_failed, _ = count_test_failures(test_path)
            
            task_id = f"HumanEval/{safe_id.split('_')[1]}"
            report_lines.append(f"| {task_id} | {orig_passed} | {orig_failed} | {mut_passed} | {mut_failed} |")
            print(f"Processed {task_id}")
            
        finally:
            # Restore original
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(original_code)
                
    with open("experiment/test_results_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
        
if __name__ == "__main__":
    generate_report()
