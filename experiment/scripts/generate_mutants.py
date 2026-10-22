import os
import ast
import json
import subprocess
import copy
import sys

MUTATIONS_OP = {
    ast.Add: ast.Sub,
    ast.Sub: ast.Add,
    ast.Mult: ast.FloorDiv,
    ast.FloorDiv: ast.Mult,
    ast.Mod: ast.Mult,
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
}

def get_bug_type_description(node_type, old_op_type):
    if node_type == 'BinOp':
        return f"arithmetic_operator_change ({old_op_type.__name__})"
    elif node_type == 'Compare':
        if old_op_type in (ast.Lt, ast.LtE, ast.Gt, ast.GtE):
            return f"boundary_condition_change ({old_op_type.__name__})"
        return f"comparison_operator_change ({old_op_type.__name__})"
    elif node_type == 'BoolOp':
        return f"boolean_operator_change ({old_op_type.__name__})"
    elif node_type == 'Constant':
        return "constant_change"
    return "unknown_mutation"

class MutantGenerator(ast.NodeTransformer):
    def __init__(self):
        self.mutations_found = []
        
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if type(node.op) in MUTATIONS_OP:
            self.mutations_found.append(('BinOp', node, type(node.op)))
        return node
        
    def visit_Compare(self, node):
        self.generic_visit(node)
        for i, op in enumerate(node.ops):
            if type(op) in MUTATIONS_OP:
                self.mutations_found.append(('Compare', node, i, type(op)))
        return node
        
    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if type(node.op) in MUTATIONS_OP:
            self.mutations_found.append(('BoolOp', node, type(node.op)))
        return node

    def visit_Constant(self, node):
        self.generic_visit(node)
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            self.mutations_found.append(('Constant', node, node.value))
        return node

def count_test_failures(test_file):
    # Run pytest and count passed/failed tests
    # We use pytest with --tb=no and quiet mode, then parse the summary
    cmd = [sys.executable, "-B", "-m", "pytest", test_file, "-q", "--tb=no"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        # If it times out, treat it as failing all tests or just a failure we can't use easily
        # Returning an error code ensures it's marked as broken/failed
        return 0, 1, 1
    
    passed = 0
    failed = 0
    # Parse pytest output like "1 failed, 10 passed in 0.05s"
    # or "11 passed in 0.03s"
    output = result.stdout
    lines = output.strip().split('\n')
    if not lines:
        return 0, 0, result.returncode
        
    summary_line = ""
    for line in reversed(lines):
        if "passed" in line or "failed" in line or "error" in line:
            summary_line = line
            break
            
    if not summary_line:
        # Fallback if pytest fails completely (syntax error etc)
        return 0, 1, result.returncode
        
    parts = summary_line.replace('=', '').strip().split(',')
    for part in parts:
        part = part.strip()
        if "failed" in part:
            try:
                failed = int(part.split()[0])
            except: pass
        elif "passed" in part:
            try:
                passed = int(part.split()[0])
            except: pass
            
    # if it's completely broken (e.g. syntax error in mutant), failed might be 1 error, passed 0
    if result.returncode != 0 and failed == 0:
        failed = 1
        
    return passed, failed, result.returncode

def mutate_and_test(src_file, test_file):
    with open(src_file, 'r', encoding='utf-8') as f:
        src_code = f.read()
        
    tree = ast.parse(src_code)
    finder = MutantGenerator()
    finder.visit(tree)
    
    if not finder.mutations_found:
        return None
        
    valid_mutants = []
    
    for mut_info in finder.mutations_found:
        mutated_tree = copy.deepcopy(tree)
        mut_type = mut_info[0]
        target_node = mut_info[1]
        
        class TargetMutator(ast.NodeTransformer):
            def __init__(self, target_node, mut_type, mut_info):
                self.target_node = target_node
                self.mut_type = mut_type
                self.mut_info = mut_info
                self.mutated = False
                self.mutated_lineno = -1
                self.mutated_node = None
                
            def visit_BinOp(self, n):
                self.generic_visit(n)
                if self.mut_type == 'BinOp' and n.lineno == self.target_node.lineno and n.col_offset == self.target_node.col_offset and not self.mutated:
                    if type(n.op) in MUTATIONS_OP:
                        n.op = MUTATIONS_OP[type(n.op)]()
                        self.mutated = True
                        self.mutated_lineno = n.lineno
                        self.mutated_node = n
                return n
                
            def visit_Compare(self, n):
                self.generic_visit(n)
                if self.mut_type == 'Compare' and n.lineno == self.target_node.lineno and n.col_offset == self.target_node.col_offset and not self.mutated:
                    op_idx = self.mut_info[2]
                    if type(n.ops[op_idx]) in MUTATIONS_OP:
                        n.ops[op_idx] = MUTATIONS_OP[type(n.ops[op_idx])]()
                        self.mutated = True
                        self.mutated_lineno = n.lineno
                        self.mutated_node = n
                return n
                
            def visit_BoolOp(self, n):
                self.generic_visit(n)
                if self.mut_type == 'BoolOp' and n.lineno == self.target_node.lineno and n.col_offset == self.target_node.col_offset and not self.mutated:
                    if type(n.op) in MUTATIONS_OP:
                        n.op = MUTATIONS_OP[type(n.op)]()
                        self.mutated = True
                        self.mutated_lineno = n.lineno
                        self.mutated_node = n
                return n

            def visit_Constant(self, n):
                self.generic_visit(n)
                if self.mut_type == 'Constant' and n.lineno == self.target_node.lineno and n.col_offset == self.target_node.col_offset and not self.mutated:
                    if isinstance(n.value, int):
                        n.value = n.value + 1 # off by one / constant change
                        self.mutated = True
                        self.mutated_lineno = n.lineno
                        self.mutated_node = n
                return n

        mutator = TargetMutator(target_node, mut_type, mut_info)
        try:
            mutated_tree = mutator.visit(mutated_tree)
            ast.fix_missing_locations(mutated_tree)
            
            if not mutator.mutated:
                continue
                
            # Do textual replacement to preserve exactly all original formatting
            replacement_code = ast.unparse(mutator.mutated_node)
            lines = src_code.split('\n')
            
            start_line = target_node.lineno - 1
            start_col = target_node.col_offset
            end_line = target_node.end_lineno - 1
            end_col = target_node.end_col_offset
            
            prefix = lines[start_line][:start_col]
            suffix = lines[end_line][end_col:]
            
            if start_line == end_line:
                lines[start_line] = prefix + replacement_code + suffix
            else:
                lines = lines[:start_line] + [prefix + replacement_code + suffix] + lines[end_line+1:]
                
            mutated_code = '\n'.join(lines)
            
            # Check for exact equivalent code just in case
            if mutated_code == src_code:
                continue
                
            actual_faulty_line = mutator.mutated_lineno
                    
        except Exception:
            # AST manipulation failed
            continue
            
        # Write mutated code
        with open(src_file, 'w', encoding='utf-8') as f:
            f.write(mutated_code)
            
        # Run tests
        passed, failed, ret_code = count_test_failures(test_file)
        
        # Restore original code
        with open(src_file, 'w', encoding='utf-8') as f:
            f.write(src_code)
            
        if failed > 0:
            bug_desc = ""
            if mut_type in ('BinOp', 'BoolOp'):
                bug_desc = get_bug_type_description(mut_type, mut_info[2])
            elif mut_type == 'Compare':
                bug_desc = get_bug_type_description(mut_type, mut_info[3])
            else:
                bug_desc = get_bug_type_description(mut_type, None)
                
            valid_mutants.append({
                "mutated_code": mutated_code,
                "faulty_line": actual_faulty_line,
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "bug_type": bug_desc
            })

    if not valid_mutants:
        return None

    # Prefer mutants where passed > 0 and failed > 0
    partial_fail = [m for m in valid_mutants if m["passed"] > 0 and m["failed"] > 0]
    
    if partial_fail:
        # Sort to pick the one with most passing tests if multiple (or just pick first)
        partial_fail.sort(key=lambda x: x["passed"], reverse=True)
        return partial_fail[0]
        
    # Fallback to failing all tests (passed == 0)
    all_fail = [m for m in valid_mutants if m["passed"] == 0]
    if all_fail:
        return all_fail[0]
        
    return None

def main():
    os.makedirs('experiment/dataset/buggy', exist_ok=True)
    ground_truth = {}
    bug_types = {}
    
    with open('experiment/dataset/metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    success_count = 0
    final_metadata = []
    
    all_failing_count = 0
    
    for meta in metadata:
        if success_count >= 30:
            break
            
        safe_id = meta['safe_id']
        src_file = f"experiment/src/{safe_id}.py"
        test_file = f"experiment/tests/humaneval/test_{safe_id}.py"
        
        print(f"Generating mutant for {safe_id}...")
        result = mutate_and_test(src_file, test_file)
        
        if result:
            ground_truth[safe_id] = {
                "faulty_line": result["faulty_line"],
                "entry_point": meta["entry_point"],
                "task_id": meta["task_id"]
            }
            bug_types[safe_id] = result["bug_type"]
            
            with open(f"experiment/dataset/buggy/{safe_id}.py", 'w', encoding='utf-8') as f:
                f.write(result["mutated_code"])
            final_metadata.append(meta)
            success_count += 1
            
            if result["passed"] == 0:
                print(f"  -> Success! (WARNING: Failed ALL {result['total']} tests) Fault on line {result['faulty_line']} [{result['bug_type']}]")
                all_failing_count += 1
            else:
                print(f"  -> Success! (Passed {result['passed']}, Failed {result['failed']}) Fault on line {result['faulty_line']} [{result['bug_type']}]")
        else:
            print(f"  -> Failed to find a valid killed mutant.")
            
    with open('experiment/dataset/ground_truth.json', 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, indent=2)
        
    with open('experiment/dataset/final_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(final_metadata, f, indent=2)
        
    with open('experiment/dataset/bug_types.json', 'w', encoding='utf-8') as f:
        json.dump(bug_types, f, indent=2)
        
    print(f"\\nGenerated {success_count} valid mutants.")
    print(f"Number of mutants failing ALL tests: {all_failing_count}")

if __name__ == "__main__":
    main()
