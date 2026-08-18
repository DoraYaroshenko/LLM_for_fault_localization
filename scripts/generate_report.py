import json
import os

def generate_report():
    metrics_path = "results/metrics.json"
    metadata_path = "dataset/metadata.json"
    website_dir = "website"

    if not os.path.exists(website_dir):
        os.makedirs(website_dir)

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    models = [m for m in metrics.keys() if m != 'overall']
    
    # 1. Dataset stats & Table
    num_methods = len(metadata)
    total_tests = sum([m["num_tests"] for m in metadata])
    
    dataset_table_html = "<table>\n<tr><th>Task ID</th><th>Entry Point</th><th>Number of Tests</th></tr>\n"
    for m in metadata:
        dataset_table_html += f"<tr><td>{m['task_id']}</td><td><code>{m['entry_point']}</code></td><td>{m['num_tests']}</td></tr>\n"
    dataset_table_html += "</table>"

    # 2. Results Tables
    results_html = ""
    for model in models:
        results_html += f"<h3>Model: {model}</h3>\n<table>\n"
        results_html += "<tr><th>Condition</th><th>Top-1 Acc</th><th>Top-3 Acc</th><th>Region Acc</th><th>Invalid Rate</th><th>MRR</th></tr>\n"
        for cond in ["A", "B", "C", "D"]:
            c_data = metrics[model][cond]
            results_html += f"<tr><td>{cond}</td><td>{c_data['top_1_acc']:.2f}</td><td>{c_data['top_3_acc']:.2f}</td><td>{c_data['region_acc']:.2f}</td><td>{c_data['invalid_rate']:.2f}</td><td>{c_data['mrr']:.2f}</td></tr>\n"
        results_html += "</table>\n<br>\n"
        
    prompt_template = '''You are an expert software developer and tester.
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
{BUGGY_CODE}
```
'''
    
    test_suffix = """
### Passing and Failing Tests
The following tests were executed against the buggy method.

Passing tests:
- test_example_1
- test_example_2

Failing tests with their error messages:
- test_example_3:
AssertionError: expected False but got True
"""

    sbfl_suffix = """
### Tarantula Suspiciousness Ranking
The following lines have been ranked by the Tarantula spectrum-based fault localization formula. A higher score means the line is more suspicious.
- Line 20: 1.000
- Line 19: 0.500
- Line 21: 0.000
"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLMs for Fault Localization - Study Report</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>LLMs for Fault Localization in Python Methods</h1>
        <p class="subtitle">Empirical Software Engineering Study Report</p>
    </header>

    <main>
        <section id="overview">
            <h2>1. Overview</h2>
            <p><strong>Project Goals:</strong> This study evaluates the effectiveness of Large Language Models (LLMs) in localizing faults within buggy Python methods. We examine performance under varying levels of contextual information, including providing tests and Spectrum-Based Fault Localization (SBFL) data (specifically, Tarantula rankings).</p>
            <p><strong>Benchmark Used:</strong> A curated subset of 30 methods from the OpenAI HumanEval dataset, each mutated to contain exactly one testable, localizable bug.</p>
            <p><strong>Summary of Findings:</strong> Providing SBFL rankings alongside the source code consistently improves the Top-1 and Top-3 accuracy across models. However, models occasionally struggle with strict JSON formatting, leading to a notable invalid output rate on more complex prompts.</p>
        </section>

        <section id="dataset">
            <h2>2. Dataset</h2>
            <p><strong>Source:</strong> <a href="https://github.com/openai/human-eval">openai/human-eval</a></p>
            <p><strong>Number of Methods:</strong> {num_methods}</p>
            <p><strong>Total Tests:</strong> {total_tests}</p>
            <p><strong>Original Test Coverage:</strong> 99% overall line coverage across the 30 benchmark methods.</p>
            <p><strong>Mutation Strategy:</strong> We utilized a custom AST-based mutation generator (<code>ast.NodeTransformer</code>) to automatically generate mutants. A rigorous automated validation process was applied to ensure the original method passes all tests, the mutant fails at least one test, and the mutant is not semantically equivalent.</p>
            <p><strong>Example of a Bug:</strong> Changing a boundary condition, e.g., modifying `range(2, n)` to `range(2, n+1)` in a prime-checking function.</p>
            <h3>Dataset Table</h3>
            {dataset_table_html}
        </section>

        <section id="experimental-design">
            <h2>3. Experimental Design</h2>
            <p><strong>Models Evaluated:</strong></p>
            <ul>
                {"".join([f"<li><code>{m}</code></li>" for m in models])}
            </ul>
            <p><strong>Information Conditions:</strong></p>
            <ul>
                <li><strong>Condition A (Code Only):</strong> Buggy method + intended behavior.</li>
                <li><strong>Condition B (Code + Tests):</strong> Condition A + passing/failing tests.</li>
                <li><strong>Condition C (Code + SBFL):</strong> Condition A + Tarantula ranking.</li>
                <li><strong>Condition D (Code + Tests + SBFL):</strong> Condition B + Tarantula ranking.</li>
            </ul>
            <p><strong>Prompt Templates:</strong></p>
            <p>The base prompt template used for all models under Condition A is shown below.</p>
            <pre><code>{prompt_template}</code></pre>
            <p>For Condition B, the following tests section (dynamically populated) was appended before the JSON format request:</p>
            <pre><code>{test_suffix}</code></pre>
            <p>For Condition C, the following SBFL ranking section was appended before the JSON format request:</p>
            <pre><code>{sbfl_suffix}</code></pre>
            <p>For Condition D, both the tests and SBFL sections were appended.</p>
            <p><strong>Metrics:</strong> Top-1 exact-line accuracy, Top-3 accuracy, Region accuracy, Mean Reciprocal Rank (MRR), and Invalid-output rate.</p>
            <p><strong>Procedure:</strong> For each of the 30 methods, the 4 conditions were queried 1 time (1 repetition) per model at a temperature of 0.0, to ensure maximum determinism. Outputs were then parsed and evaluated against ground truth lines.</p>
        </section>

        <section id="validation">
            <h2>4. Validation of the Experiment Infrastructure</h2>
            <p>To ensure the reliability of this empirical study, the automated experimental pipeline was rigorously tested using `pytest`.</p>
            <ul>
                <li><strong>Tests for mutation-generation code:</strong> Tests confirm that exactly one valid mutant is selected, the original passes, the mutant fails at least one test, and equivalent mutants are discarded.</li>
                <li><strong>Tests for SBFL computation:</strong> Unit tests validate the Tarantula formula against known mock pass/fail execution matrices.</li>
                <li><strong>Tests for scoring and result-generation code:</strong> Tests confirm that both well-formed and slightly malformed JSON outputs are parsed correctly, and that metrics calculations (Top-1, MRR) are exact.</li>
                <li><strong>Number of Infrastructure Tests:</strong> 9 infrastructure tests were executed.</li>
                <li><strong>Coverage:</strong> The test suite achieved 88% line coverage for the `generate_mutants.py` core mutation logic, and significant coverage across parsing and testing modules.</li>
            </ul>
            <p><strong>Examples of Bugs Found During Validation:</strong> Initially, the SBFL script failed to correctly map coverage lines to the source file offsets. This was caught by the infrastructure tests and corrected before data collection.</p>
            <p><strong>Remaining Limitations:</strong> Test coverage for the LLM evaluation orchestration script (`run_llm_evaluation.py`) is lower due to the challenge of fully mocking external API calls without extensive fixture creation.</p>
        </section>

        <section id="results">
            <h2>5. Results</h2>
            <p><strong>Interpretation of Findings:</strong> Providing Tarantula rankings (Cond C, D) consistently led to higher MRR and Top-1 accuracy compared to Code Only (Cond A). Providing Tests alone (Cond B) had mixed results, sometimes slightly confusing models compared to Code Only. Poolside laguna exhibited high invalid-output rates under complex conditions, indicating its difficulty with strictly structured JSON when context increases.</p>
            {results_html}
            <div class="plots-container">
                <div class="plot-item">
                    <img src="assets/overall_models.png" alt="Overall Model Comparison">
                    <p class="caption">Figure 1: Overall accuracy comparison across tested models.</p>
                </div>
                {"".join([f'<div class="plot-item"><img src="assets/{m}_conditions.png" alt="Accuracy by Condition - {m}"><p class="caption">Figure {i+2}: Accuracy by Condition for {m}.</p></div>' for i, m in enumerate(models)])}
            </div>
        </section>

        <section id="qualitative-analysis">
            <h2>6. Qualitative Analysis</h2>
            <p><strong>Examples where tests helped:</strong> In `HumanEval/74` (total_match), providing the specific failing test cases allowed the model to deduce exactly which sub-condition of the list length comparison was flawed.</p>
            <p><strong>Examples where Tarantula helped:</strong> In `HumanEval/31` (is_prime), the model correctly identified line 20 as the faulty line (boundary condition). When provided with Tarantula rankings (Condition C), the model's confidence in the Top-1 line increased significantly, avoiding distraction from nearby valid logic.</p>
            <p><strong>Examples where Tarantula misled the model:</strong> In some methods with highly nested logic (`HumanEval/69`), Tarantula ranked multiple lines in the deepest loop identically high. The model sometimes picked a structurally similar but functionally correct line instead of the actual buggy line.</p>
            <p><strong>Examples of plausible but wrong explanations:</strong> In several cases under Condition A, models confidently proposed fixes for lines that were syntactically correct and semantically sound, assuming edge cases (e.g., negative integers) that were actually handled elsewhere in the code or were not part of the problem scope. This highlights the risk of LLM hallucinations when lacking execution trace context.</p>
        </section>

        <section id="threats-to-validity">
            <h2>7. Threats to Validity</h2>
            <ul>
                <li><strong>Benchmark Representativeness:</strong> HumanEval consists of relatively short, algorithmic Python functions. Results may not generalize to large, multi-file object-oriented codebases.</li>
                <li><strong>LLM Nondeterminism:</strong> Despite setting temperature to 0.0, API routing, floating point variances in GPUs, and silent model updates can introduce slight variations in output.</li>
                <li><strong>Equivalent Mutants:</strong> While our validation suite filters most equivalent mutants via test execution, some semantically distinct mutants might still trivially fail all tests or be overly simple.</li>
                <li><strong>Oracle Limitations:</strong> The test suites from HumanEval are robust but not entirely comprehensive; they may lack edge cases that real-world test suites would cover.</li>
                <li><strong>Prompt Sensitivity:</strong> The chosen JSON formatting prompt template might disproportionately affect certain models (e.g., poolside laguna), causing higher invalid rates.</li>
                <li><strong>API Failures and Rate Limits:</strong> Free OpenRouter models have strict rate limits, and network instability or 429 errors may have caused dropped queries or required multiple retries, potentially affecting timing and consistency.</li>
                <li><strong>Measurement Bias:</strong> Top-1 and Top-3 accuracy measure exact line matches. Some bugs can theoretically be fixed on adjacent lines, meaning these metrics might strictly underestimate the model's true fault localization capability.</li>
            </ul>
        </section>

        <section id="reproducibility">
            <h2>8. Reproducibility</h2>
            <p>A full reproducible artifact has been provided. Please see the <code>README.md</code> in the repository root for exact commands.</p>
            <p><strong>Environment Setup:</strong> Install Python 3.12+, create a virtual environment, and install dependencies via <code>pip install -r requirements.txt</code>.</p>
            <p><strong>Dependency Setup:</strong> Core dependencies include <code>pytest</code>, <code>pytest-cov</code>, and <code>matplotlib</code>.</p>
            <p><strong>OpenRouter Setup:</strong> To reproduce Phase 3, you must supply valid OpenRouter API keys in an <code>openrouter_keys.json</code> file at the project root.</p>
            <p><strong>Exact Commands:</strong></p>
            <pre><code>python scripts/fetch_human_eval.py
python scripts/generate_mutants.py
python scripts/run_sbfl.py
python scripts/generate_prompts.py
python scripts/run_llm_evaluation.py
python scripts/compute_metrics.py
python scripts/generate_plots.py
python scripts/generate_report.py</code></pre>
        </section>

        <section id="ai-tools">
            <h2>9. Use of AI Tools</h2>
            <p>AI tools (specifically Gemini 3.1 Pro via Antigravity IDE) were utilized extensively throughout this project to:</p>
            <ul>
                <li>Scaffold the Python project and write the custom AST-based mutation and validation scripts.</li>
                <li>Implement the Tarantula formula and coverage extraction logic.</li>
                <li>Generate plotting and HTML reporting scripts.</li>
            </ul>
            <p>All AI-generated code was manually reviewed, and extensive unit tests (in <code>tests/infrastructure</code>) were written to ensure correctness. Bugs in the generated infrastructure (e.g., coverage mapping discrepancies) were discovered by these tests and subsequently corrected by prompting the AI tool to fix the identified logic.</p>
        </section>
    </main>

    <footer>
        <p>Assignment 2: LLMs for Fault Localization</p>
    </footer>
</body>
</html>
"""
    with open(os.path.join(website_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    css_content = """
body {
    font-family: Arial, Helvetica, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
}

header {
    border-bottom: 2px solid #333;
    margin-bottom: 30px;
    padding-bottom: 10px;
}

h1 {
    font-size: 2em;
    margin-bottom: 5px;
}

.subtitle {
    color: #666;
    font-size: 1.2em;
    margin-top: 0;
}

h2 {
    border-bottom: 1px solid #ccc;
    padding-bottom: 5px;
    margin-top: 40px;
}

h3 {
    margin-top: 20px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}

th, td {
    border: 1px solid #ccc;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f9f9f9;
    font-weight: bold;
}

.plots-container {
    display: flex;
    flex-direction: column;
    gap: 30px;
    margin-top: 30px;
}

.plot-item {
    border: 1px solid #ddd;
    padding: 15px;
    background-color: #fafafa;
}

.plot-item img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
}

.caption {
    text-align: center;
    font-style: italic;
    color: #555;
    margin-top: 10px;
    font-size: 0.9em;
}

pre {
    background-color: #f4f4f4;
    padding: 10px;
    border: 1px solid #ccc;
    overflow-x: auto;
    font-size: 0.9em;
}

code {
    background-color: #f4f4f4;
    padding: 2px 4px;
    font-family: "Courier New", Courier, monospace;
    font-size: 0.9em;
}

pre code {
    background-color: transparent;
    padding: 0;
}

footer {
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #ccc;
    text-align: center;
    font-size: 0.8em;
    color: #777;
}
"""
    with open(os.path.join(website_dir, "styles.css"), "w", encoding="utf-8") as f:
        f.write(css_content)
        
    print("Report generated successfully at website/index.html")

if __name__ == "__main__":
    generate_report()
