import sys

def parse_failures(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output = []
    current_mutant = None
    failures = []

    for line in lines:
        line = line.strip()
        if line.startswith("--- Mutant"):
            if current_mutant:
                output.append(f"{current_mutant}")
                for fail in failures:
                    output.append(f"  ❌ {fail}")
                output.append("")
            
            current_mutant = line
            failures = []
        
        # In pytest --tb=line, the failure is usually an absolute path followed by line and error
        if ".py:" in line and "Error" in line or "Exception" in line or "FAILED" in line and ".py" in line:
            # We want to extract just from 'tests\' onwards
            if "tests\\" in line:
                failures.append(line[line.find("tests\\"):])
            elif "tests/" in line:
                failures.append(line[line.find("tests/"):])
            elif line.startswith("E "):
                continue # Skip the E lines as the full path line contains the same info

    if current_mutant:
        output.append(f"{current_mutant}")
        for fail in failures:
            output.append(f"  ❌ {fail}")
        output.append("")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Mutant Verification Summary: Failing Tests per Mutant\n")
        f.write("=====================================================\n\n")
        f.write("\n".join(output))

if __name__ == "__main__":
    parse_failures("results/mutants_failures.txt", "results/mutants_failures_summary.txt")
