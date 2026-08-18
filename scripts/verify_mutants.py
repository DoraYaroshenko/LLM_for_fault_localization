import os
import subprocess
import sys

def verify_mutants():
    buggy_dir = "dataset/buggy"
    if not os.path.exists(buggy_dir):
        print("Buggy directory not found.")
        return
        
    mutants = [f for f in os.listdir(buggy_dir) if f.endswith('.py')]
    if not mutants:
        print("No mutants found.")
        return
        
    passed_mutants = 0
    failed_mutants = 0
    
    for mutant in mutants:
        safe_id = mutant.replace('.py', '')
        src_path = os.path.join("src", mutant)
        buggy_path = os.path.join(buggy_dir, mutant)
        test_path = os.path.join("tests", f"test_{safe_id}.py")
        
        # Backup original
        with open(src_path, "r", encoding="utf-8") as f:
            original_code = f.read()
            
        try:
            # Copy mutant to src
            with open(buggy_path, "r", encoding="utf-8") as f:
                buggy_code = f.read()
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(buggy_code)
                
            # Run pytest
            result = subprocess.run(["venv\\Scripts\\python.exe", "-m", "pytest", test_path, "--tb=line"], capture_output=True, text=True)
            if result.returncode != 0:
                failed_mutants += 1
                print(f"--- Mutant {safe_id} FAILED tests ---")
                print(result.stdout)
            else:
                passed_mutants += 1
                print(f"Mutant {safe_id} PASSED all tests! (Should have failed)")
        finally:
            # Restore original
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(original_code)
                
    print(f"Total mutants verified: {len(mutants)}")
    print(f"Mutants that failed at least 1 test (correct): {failed_mutants}")
    print(f"Mutants that passed all tests (incorrect): {passed_mutants}")

if __name__ == "__main__":
    verify_mutants()
