import os
import sys
import json
import subprocess
import pytest
import coverage

class ExtractOutputPlugin:
    def __init__(self):
        self.results = {}
        self.failing_details = {}

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            name = report.nodeid.split("::")[-1]
            if report.failed:
                self.results[name] = "failed"
                self.failing_details[name] = str(report.longrepr)
            elif report.passed:
                self.results[name] = "passed"

def main():
    if len(sys.argv) != 4:
        sys.exit(1)
        
    safe_id = sys.argv[1]
    src_file = sys.argv[2]
    test_file = sys.argv[3]
    
    # Get test nodes
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", test_file],
        capture_output=True, text=True
    )
    lines = result.stdout.split('\n')
    nodes = []
    for line in lines:
        line = line.strip()
        if "::" in line and not line.startswith("warnings") and not line.startswith("=") and not line.startswith("-"):
            nodes.append(line.split(' ')[0].split("::")[-1])
    nodes = [n for n in nodes if n]
    
    if not nodes:
        with open("sbfl_runner_error.log", "w") as f:
            f.write(result.stdout)
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
            
    coverage_data = {}
    plugin = ExtractOutputPlugin()
    
    src_dir = os.path.dirname(src_file)
    
    for test_name in nodes:
        full_node = f"{test_file}::{test_name}"
        cov = coverage.Coverage(source=[src_dir])
        cov.start()
        
        pytest.main([full_node, "-q", "--tb=short"], plugins=[plugin])
        
        cov.stop()
        cov.save()
        data = cov.get_data()
        
        abs_src = os.path.abspath(src_file)
        lines = data.lines(abs_src)
        coverage_data[test_name] = list(lines) if lines else []
        
    output = {
        "results": plugin.results,
        "failing_details": plugin.failing_details,
        "coverage": coverage_data
    }
    
    with open("sbfl_runner_out.json", "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    main()
