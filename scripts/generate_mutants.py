import os
import ast
import json
import subprocess
import copy
import shutil
import sys

MUTATIONS = {
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

class MutantGenerator(ast.NodeTransformer):
    def __init__(self):
        self.mutations_found = []
        
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if type(node.op) in MUTATIONS:
            self.mutations_found.append(('BinOp', node))
        return node
        
    def visit_Compare(self, node):
        self.generic_visit(node)
        for i, op in enumerate(node.ops):
            if type(op) in MUTATIONS:
                self.mutations_found.append(('Compare', node, i))
        return node
        
    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if type(node.op) in MUTATIONS:
            self.mutations_found.append(('BoolOp', node))
        return node

def mutate_and_test(src_file, test_file):
    with open(src_file, 'r', encoding='utf-8') as f:
        src_code = f.read()
        
    tree = ast.parse(src_code)
    finder = MutantGenerator()
    finder.visit(tree)
    
    if not finder.mutations_found:
        return None
        
    for mut_info in finder.mutations_found:
        mutated_tree = copy.deepcopy(tree)
        node = mut_info[1]
        
        class TargetMutator(ast.NodeTransformer):
            def __init__(self, target_node, mut_type, op_idx=0):
                self.target_node = target_node
                self.mut_type = mut_type
                self.op_idx = op_idx
                self.mutated = False
                self.mutated_lineno = -1
                
            def visit_BinOp(self, n):
                self.generic_visit(n)
                if n.lineno == self.target_node.lineno and n.col_offset == self.target_node.col_offset and not self.mutated:
                    if type(n.op) in MUTATIONS:
                        n.op = MUTATIONS[type(n.op)]()
                        self.mutated = True
                        self.mutated_lineno = n.lineno
                return n
                
            def visit_Compare(self, n):
                self.generic_visit(n)
                if n.lineno == self.target_node.lineno and n.col_offset == self.target_node.col_offset and not self.mutated:
                    if type(n.ops[self.op_idx]) in MUTATIONS:
                        n.ops[self.op_idx] = MUTATIONS[type(n.ops[self.op_idx])]()
                        self.mutated = True
                        self.mutated_lineno = n.lineno
                return n
                
            def visit_BoolOp(self, n):
                self.generic_visit(n)
                if n.lineno == self.target_node.lineno and n.col_offset == self.target_node.col_offset and not self.mutated:
                    if type(n.op) in MUTATIONS:
                        n.op = MUTATIONS[type(n.op)]()
                        self.mutated = True
                        self.mutated_lineno = n.lineno
                return n

        mutator = TargetMutator(node, mut_info[0], mut_info[2] if len(mut_info) > 2 else 0)
        mutated_tree = mutator.visit(mutated_tree)
        ast.fix_missing_locations(mutated_tree)
        
        if not mutator.mutated:
            continue
            
        mutated_code = ast.unparse(mutated_tree)
        
        # Write mutated code
        with open(src_file, 'w', encoding='utf-8') as f:
            f.write(mutated_code)
            
        # Run tests
        cmd = [sys.executable, "-m", "pytest", test_file, "-q"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Restore original code
        with open(src_file, 'w', encoding='utf-8') as f:
            f.write(src_code)
            
        if result.returncode != 0:
            return {
                "mutated_code": mutated_code,
                "faulty_line": mutator.mutated_lineno
            }
            
    return None

def main():
    os.makedirs('dataset/buggy', exist_ok=True)
    ground_truth = {}
    
    with open('dataset/metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    success_count = 0
    final_metadata = []
    
    for meta in metadata:
        if success_count >= 30:
            break
            
        safe_id = meta['safe_id']
        src_file = f"src/{safe_id}.py"
        test_file = f"tests/test_{safe_id}.py"
        
        print(f"Generating mutant for {safe_id}...")
        result = mutate_and_test(src_file, test_file)
        
        if result:
            ground_truth[safe_id] = {
                "faulty_line": result["faulty_line"],
                "entry_point": meta["entry_point"],
                "task_id": meta["task_id"]
            }
            with open(f"dataset/buggy/{safe_id}.py", 'w', encoding='utf-8') as f:
                f.write(result["mutated_code"])
            final_metadata.append(meta)
            success_count += 1
            print(f"  -> Success! Fault on line {result['faulty_line']}")
        else:
            print(f"  -> Failed to find a valid killed mutant.")
            
    with open('dataset/ground_truth.json', 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, indent=2)
        
    with open('dataset/final_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(final_metadata, f, indent=2)
        
    print(f"Generated {success_count} valid mutants.")

if __name__ == "__main__":
    main()
