import json
import os
import re

DATASET_META = "dataset/final_metadata.json"
BUGGY_DIR = "dataset/buggy"
SBFL_DIR = "dataset/sbfl"
TESTS_DIR = "tests"
PROMPTS_DIR = "results/prompts"

PROMPT_PREFIX = """You are an expert software developer and tester.
Do not repair the program. Your task is only to identify the most likely faulty line or small faulty region.
You must return ONLY a valid JSON object exactly matching this structure, with no other conversational text or markdown formatting (do not wrap in ```json).
{
  "top_1_line": 12,
  "top_3_lines": [12, 14, 9],
  "faulty_region": "loop condition",
  "explanation": "The loop condition may terminate before the last candidate is checked."
}

Here is the buggy Python method. The docstring describes its intended behavior.
Lines are numbered for your reference.

```python
"""

def extract_tests_from_file(filepath):
    test_names = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('def test_'):
                    name = line.split('(')[0].replace('def ', '').strip()
                    test_names.append(name)
    return test_names

def generate_prompts():
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    
    with open(DATASET_META, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
        
    for task in tasks:
        safe_id = task['safe_id']
        buggy_file = os.path.join(BUGGY_DIR, f"{safe_id}.py")
        sbfl_file = os.path.join(SBFL_DIR, f"{safe_id}.json")
        test_file = os.path.join(TESTS_DIR, f"test_{safe_id}.py")
        
        # 1. Read Buggy Code
        with open(buggy_file, 'r', encoding='utf-8') as f:
            code_lines = f.readlines()
            
        numbered_code = ""
        for i, line in enumerate(code_lines, 1):
            numbered_code += f"{i:2d}: {line}"
            
        # 2. Read SBFL and Failing Tests
        with open(sbfl_file, 'r', encoding='utf-8') as f:
            sbfl_data = json.load(f)
            
        tarantula_scores = sbfl_data.get('tarantula', {})
        failing_tests = sbfl_data.get('failing_tests', {})
        
        # 3. Get All Tests and determine Passing Tests
        all_tests = extract_tests_from_file(test_file)
        passing_tests = [t for t in all_tests if t not in failing_tests]
        
        # Format Tests Section
        tests_section = "\n### Passing and Failing Tests\nThe following tests were executed against the buggy method.\n\n"
        if passing_tests:
            tests_section += "Passing tests:\n"
            for pt in passing_tests:
                tests_section += f"- {pt}\n"
            tests_section += "\n"
            
        if failing_tests:
            tests_section += "Failing tests with their error messages:\n"
            for ft_name, ft_error in failing_tests.items():
                # Clean up error message to be shorter (last few lines usually contain the assert error)
                lines = ft_error.strip().split('\n')
                err_summary = "\n".join(lines[-3:]) if len(lines) >= 3 else ft_error
                tests_section += f"- {ft_name}:\n{err_summary}\n\n"
                
        # Format SBFL Section
        sbfl_section = "\n### Tarantula Suspiciousness Ranking\nThe following lines have been ranked by the Tarantula spectrum-based fault localization formula. A higher score means the line is more suspicious.\n"
        # Sort by score descending
        sorted_scores = sorted(tarantula_scores.items(), key=lambda item: float(item[1]), reverse=True)
        for line_str, score in sorted_scores:
            sbfl_section += f"- Line {line_str}: {score:.3f}\n"
            
        # 4. Generate the 4 Prompts
        suffix = "\nProvide your JSON response below.\n"
        
        # Condition A
        prompt_A = PROMPT_PREFIX + numbered_code + "```\n" + suffix
        # Condition B
        prompt_B = PROMPT_PREFIX + numbered_code + "```\n" + tests_section + suffix
        # Condition C
        prompt_C = PROMPT_PREFIX + numbered_code + "```\n" + sbfl_section + suffix
        # Condition D
        prompt_D = PROMPT_PREFIX + numbered_code + "```\n" + tests_section + sbfl_section + suffix
        
        # Save Prompts
        for cond, prompt_text in zip(["A", "B", "C", "D"], [prompt_A, prompt_B, prompt_C, prompt_D]):
            filepath = os.path.join(PROMPTS_DIR, f"{safe_id}_{cond}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(prompt_text)
                
    print(f"Successfully generated {len(tasks) * 4} prompts in {PROMPTS_DIR}")

if __name__ == "__main__":
    generate_prompts()
