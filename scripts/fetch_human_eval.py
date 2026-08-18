import os
import ast
import json
from human_eval.data import read_problems

def parse_asserts(test_code, entry_point):
    """
    Parses the test_code to find asserts inside the 'check' function
    and returns a list of individual test functions as strings.
    """
    tree = ast.parse(test_code)
    asserts = []
    
    class AssertVisitor(ast.NodeVisitor):
        def visit_Assert(self, node):
            # Unparse the assert node back to source code
            asserts.append(ast.unparse(node))
            self.generic_visit(node)
            
    AssertVisitor().visit(tree)
    
    test_functions = []
    for i, asrt in enumerate(asserts):
        # Replace 'candidate' with the actual entry_point name if needed, 
        # though HumanEval typically uses 'candidate(x)' in the assert.
        # We can just replace 'candidate' with the entry_point name.
        asrt_fixed = asrt.replace('candidate', entry_point)
        test_func = f"def test_{entry_point}_{i}():\n    {asrt_fixed}\n"
        test_functions.append(test_func)
        
    return test_functions

def main():
    problems = read_problems()
    
    valid_problems = []
    
    for task_id, problem in problems.items():
        prompt = problem.get("prompt", "")
        if not prompt or '\"\"\"' not in prompt and "'''" not in prompt:
            continue
            
        test_code = problem.get("test", "")
        try:
            tree = ast.parse(test_code)
            assert_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))
            if assert_count >= 10:
                valid_problems.append((task_id, problem))
        except Exception:
            pass
            
    print(f"Found {len(valid_problems)} valid problems.")
    
    selected = valid_problems
    
    # Save the selected dataset
    dataset_metadata = []
    
    os.makedirs('src', exist_ok=True)
    os.makedirs('tests', exist_ok=True)
    os.makedirs('dataset', exist_ok=True)
    
    for task_id, problem in selected:
        safe_id = task_id.replace('/', '_').lower()
        entry_point = problem['entry_point']
        
        # 1. Write src file
        src_content = problem['prompt'] + problem['canonical_solution']
        with open(f'src/{safe_id}.py', 'w', encoding='utf-8') as f:
            f.write(src_content)
            
        # 2. Write test file
        test_functions = parse_asserts(problem['test'], entry_point)
        
        test_content = f"from src.{safe_id} import {entry_point}\n\n"
        # we might need math or other imports. HumanEval tests sometimes use them.
        test_content += "import math\n" 
        test_content += "".join(test_functions)
        
        with open(f'tests/test_{safe_id}.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
            
        dataset_metadata.append({
            "task_id": task_id,
            "safe_id": safe_id,
            "entry_point": entry_point,
            "num_tests": len(test_functions)
        })
        
    with open('dataset/metadata.json', 'w', encoding='utf-8') as f:
        json.dump(dataset_metadata, f, indent=2)
        
    print(f"Saved {len(selected)} problems to src/ and tests/")

if __name__ == '__main__':
    main()
