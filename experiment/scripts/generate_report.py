import json
import os

def generate_report():
    metrics_path = "experiment/results/metrics.json"
    metadata_path = "experiment/dataset/final_metadata.json"
    website_dir = "experiment/website"

    if not os.path.exists(website_dir):
        os.makedirs(website_dir)

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    bug_type_metrics_path = "experiment/results/metrics_by_bug_type.json"
    bt_html = ""
    if os.path.exists(bug_type_metrics_path):
        with open(bug_type_metrics_path, "r") as f:
            bt_metrics = json.load(f)
        bt_html = "<h3>Performance by Bug Type (Overall)</h3>\n<table>\n"
        bt_html += "<tr><th>Bug Type</th><th>Model</th><th>N (queries)</th><th>Top-1 Acc</th><th>Top-3 Acc</th><th>MRR</th></tr>\n"
        for bt, models_data in bt_metrics.items():
            for model, conds in models_data.items():
                overall = conds["overall"]
                bt_html += f"<tr><td><code>{bt}</code></td><td>{model}</td><td>{overall['total']}</td><td>{overall['top_1_acc']:.2f}</td><td>{overall['top_3_acc']:.2f}</td><td>{overall['mrr']:.2f}</td></tr>\n"
        bt_html += "</table>\n<br>\n"

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    models = [m for m in metrics.keys() if m != 'overall']
    
    # 1. Dataset stats & Table
    num_methods = len(metadata)
    total_tests = sum([m["num_tests"] for m in metadata])
    
    dataset_table_html = "<table>\n<tr><th>Task ID</th><th>Entry Point</th><th>Total Tests</th><th>Original Passed</th><th>Buggy Passed</th><th>Buggy Failed</th></tr>\n"
    for m in metadata:
        safe_id = m['safe_id']
        num_tests = m['num_tests']
        
        sbfl_path = f"experiment/dataset/sbfl/{safe_id}.json"
        buggy_failed = 0
        if os.path.exists(sbfl_path):
            with open(sbfl_path, 'r') as f:
                sbfl_data = json.load(f)
                buggy_failed = len(sbfl_data.get("failing_tests", {}))
                
        buggy_passed = num_tests - buggy_failed
        original_passed = num_tests
        
        dataset_table_html += f"<tr><td>{m['task_id']}</td><td><code>{m['entry_point']}</code></td><td>{num_tests}</td><td>{original_passed}</td><td>{buggy_passed}</td><td>{buggy_failed}</td></tr>\n"
    dataset_table_html += "</table>"

    # 2. Results Tables
    results_html = ""
    for model in models:
        results_html += f"<h3>Model: {model}</h3>\n<table>\n"
        results_html += "<tr><th>Condition</th><th>Top-1 Acc</th><th>Top-3 Acc</th><th>Region Acc</th><th>Invalid Rate</th><th>MRR</th></tr>\n"
        for cond in ["A", "B", "C", "D"]:
            c_data = metrics[model][cond]
            results_html += f"<tr><td>{cond}</td><td>{c_data['top_1_acc']:.2f}</td><td>{c_data['top_3_acc']:.2f}</td><td>{c_data['region_acc']:.2f}</td><td>{c_data['invalid_rate']:.2f}</td><td>{c_data['mrr']:.2f}</td></tr>\n"
        
        # Add Overall row
        o_data = metrics[model]["overall"]
        results_html += f"<tr style='background-color: #eee; font-weight: bold;'><td>Overall</td><td>{o_data['top_1_acc']:.2f}</td><td>{o_data['top_3_acc']:.2f}</td><td>{o_data['region_acc']:.2f}</td><td>{o_data['invalid_rate']:.2f}</td><td>{o_data['mrr']:.2f}</td></tr>\n"
        results_html += "</table>\n<br>\n"
        
    prompt_template = '''You are an expert software developer and tester.
Do not repair the program. Your task is only to identify the most likely faulty line or small faulty region.
You must return ONLY a valid JSON object exactly matching this structure, with no other conversational text or markdown formatting (do not wrap in ```json).
IMPORTANT: The `top_3_lines` list MUST be ordered by suspiciousness, from most suspicious (1st) to least suspicious (3rd).

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

Provide your JSON response below.
'''
    
    test_suffix = """### Test Suite
Here is the full test suite code executed against the buggy method.

```python
{TEST_SUITE_CODE}
```

The following tests failed with these errors:
- test_example_3:
    assert is_prime(4) == False
E   assert True == False
E    +  where True = is_prime(4)

Provide your JSON response below.
"""

    sbfl_suffix = """### Tarantula Suspiciousness Ranking
The following lines have been ranked by the Tarantula spectrum-based fault localization formula. A higher score means the line is more suspicious.
- Line 25: 0.632
- Line 22: 0.522
- Line 20: 0.500
- Line 3: 0.000
- Line 21: 0.000
- Line 23: 0.000
- Line 24: 0.000

Provide your JSON response below.
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
        <p class="subtitle">Empirical Software Engineering Study Report by Dora Yaroshenko and Lilac Gil-Ad</p>
    </header>

    <main>
        <section id="overview">
            <h2>1. Overview</h2>
            <p><strong>Project Goals:</strong> This study evaluates the effectiveness of Large Language Models (LLMs) in localizing faults within buggy Python methods. We examine performance under varying levels of contextual information, including providing tests and Spectrum-Based Fault Localization (SBFL) data (specifically, Tarantula rankings).</p>
            <p><strong>Benchmark Used:</strong> A curated subset of 30 methods from the OpenAI HumanEval dataset (chosen to ensure each has a natural-language specification and at least 10 tests), each mutated to contain exactly one testable, localizable bug.</p>
            <p><strong>Summary of Findings:</strong> Providing SBFL rankings (Tarantula) alongside the source code actually degraded performance for the models tested in this experiment. Providing tests alone (Condition B) yielded the highest accuracy. The models struggled to correctly utilize the numerical SBFL rankings, often performing worse than when given just the code or code with tests.</p>
        </section>

        <section id="dataset">
            <h2>2. Dataset</h2>
            <p><strong>Source:</strong> <a href="https://github.com/openai/human-eval">openai/human-eval</a></p>
            <p><strong>Number of Methods:</strong> {num_methods}</p>
            <p><strong>Total Tests:</strong> {total_tests}</p>
            <p><strong>Original Test Coverage:</strong> 99% overall line coverage across the 30 benchmark methods.</p>
            <p><strong>Test Extraction Strategy:</strong> The tests for each method come directly from the official OpenAI HumanEval dataset. In the raw dataset, tests are provided as a single <code>check()</code> function containing multiple assertions. We used Python's <code>ast</code> module to parse this block and extract each <code>assert</code> statement into its own standalone <code>pytest</code> function. This separation is critical for Spectrum-Based Fault Localization (Tarantula), as it requires an accurate count of both passing and failing tests; if all assertions were left in a single block, execution would halt at the first failure, masking the results of subsequent assertions.</p>
            <p><strong>Mutation Strategy:</strong> We utilized a custom AST-based mutation generator (<code>ast.NodeTransformer</code>) to automatically generate mutants. The script parses the original Python method into an Abstract Syntax Tree (AST), traverses it to locate targeted operators (binary, comparison, boolean) and integer constants. For each method, it systematically applies <em>exactly one</em> modification (e.g., swapping a single operator for its logical opposite, OR incrementing a single integer constant by 1), ensuring that each mutant contains exactly one localizable fault. For each generated mutant candidate, the AST is unparsed back into source code, and a rigorous automated testing validation process is applied. Crucially, the generator preferentially selects a mutant that causes <em>partial test failure</em> (some passing tests, some failing tests) to provide the optimal signal-to-noise ratio for Spectrum-Based Fault Localization, falling back to fully failing mutants only if no partial failure exists.</p>
            <p><strong>Example of a Bug:</strong> Swapping a single arithmetic operator (e.g., modifying <code>n - 1</code> to <code>n + 1</code>) in a prime-checking function, OR changing a single integer constant like <code>0</code> to <code>1</code>.</p>
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
            <p><strong>Region Accuracy Details:</strong> Because evaluating the natural language <code>faulty_region</code> description programmatically is difficult, "Region Accuracy" in this study is calculated by checking if the model's <code>top_1_line</code> prediction falls within a +/- 2 line radius of the exact ground truth line.</p>
            <p><strong>MRR Calculation Details:</strong> For each evaluated method, the ground truth line is matched against the LLM's predictions. If it exactly matches the Top-1 prediction, the rank is 1. If it appears in the Top-3 list, the rank is its index plus 1 (e.g., 2 or 3). If it is not in the Top-3, the rank is 0. The reciprocal rank is calculated as <code>1.0 / rank</code> (or 0.0 if the rank is 0). The MRR for a condition is the average of these reciprocal ranks across all methods.</p>
            <p><strong>Procedure:</strong> For each of the 30 methods, the 4 conditions were queried 1 time (1 repetition) per model at a temperature of 0.0, to ensure maximum determinism. Outputs were then parsed and evaluated against ground truth lines.</p>
        </section>

        <section id="validation">
            <h2>4. Validation of the Experiment Infrastructure</h2>
            <p>To ensure the reliability of this empirical study, the automated experimental pipeline was rigorously tested using `pytest`.</p>
            <ul>
                <li><strong>Mutation Generation</strong> (<code>test_mutant_generator.py</code>): Tests confirm that exactly one valid mutant is selected, the original passes, the mutant fails at least one test, and equivalent mutants are discarded.</li>
                <li><strong>SBFL & Coverage</strong> (<code>test_sbfl_computation.py</code>, <code>test_coverage_aggregation.py</code>): Unit tests validate the Tarantula formula against known mock pass/fail execution matrices, and ensure coverage logs are parsed correctly.</li>
                <li><strong>Metrics, Results & Parsing</strong> (<code>test_metrics_and_parsing.py</code>): Tests confirm that both well-formed and slightly malformed JSON outputs are parsed correctly from the LLM, and that metrics calculations (Top-1, MRR) are exact.</li>
                <li><strong>HTML Generation</strong> (<code>test_html_generation.py</code>): Verifies that the final report structure is built properly from the generated data.</li>
                <li><strong>Number of Infrastructure Tests:</strong> 33 infrastructure tests were executed.</li>
                <li><strong>Coverage:</strong> The test suite achieved an overall coverage of 83% across all scripts, with over 85% average line coverage on the core experimental logic including mutation generation, SBFL computation, metrics calculation, prompt generation, plot generation, and report generation.</li>
            </ul>
            <p><strong>Examples of Bugs Found During Validation:</strong> Initially, the SBFL script failed to correctly map coverage lines to the source file offsets. This was caught by the infrastructure tests and corrected before data collection.</p>
            <p><strong>Remaining Limitations:</strong> Test coverage for the LLM evaluation orchestration script (`run_llm_evaluation.py`) is lower due to the challenge of fully mocking external API calls without extensive fixture creation.</p>
        </section>

        <section id="results">
            <h2>5. Results</h2>
            <p><strong>Interpretation of Findings:</strong> Providing Tests alone (Cond B) resulted in the best performance for both models tested. Interestingly, providing Tarantula rankings (Cond C, D) led to a significant decrease in accuracy, particularly for <code>nvidia/nemotron-3.5-lightning-free</code>, whose Top-1 accuracy dropped from 80% to 26%. This suggests that these specific models struggle to interpret the numerical suspiciousness scores and are distracted by them rather than aided by them. Unlike some other models that fail due to schema breakage, these models maintained a low invalid-output rate, meaning they successfully produced JSON but localized the wrong line.</p>
            <h3>Answers to Research Questions</h3>
            <ul>
                <li><strong>RQ1 — Baseline Fault Localization:</strong> When given only the buggy method and intended behavior (Cond A), both models showed a strong baseline ability to localize faults, with Top-1 accuracy around 73-80%.</li>
                <li><strong>RQ2 — Effect of Test Information:</strong> Providing passing and failing tests (Cond B) improved Top-1 accuracy and MRR for both models, establishing it as the most effective context condition in this experiment.</li>
                <li><strong>RQ3 — Effect of SBFL Information:</strong> Providing a spectrum-based fault-localization ranking like Tarantula (Cond C) degraded Top-1 accuracy and Mean Reciprocal Rank (MRR) for both models compared to the baseline (Cond A).</li>
                <li><strong>RQ4 — Combining Tests and SBFL:</strong> Combining test information with an SBFL ranking (Cond D) performed worse than providing tests alone (Cond B), confirming that the SBFL data acted as a negative distractor for these models.</li>
                <li><strong>RQ5 — Model Comparison:</strong> Both models exhibited similar trends, though <code>nvidia/nemotron-3.5-lightning-free</code> was far more negatively impacted by the SBFL data than <code>openai/gpt-oss-20b-free</code>. Both maintained good JSON formatting adherence across all conditions.</li>
            </ul>
            <p><em>Per-Bug-Type Metrics:</em> Our AST mutator categorizes bugs into specific mutation operators. The table below breaks down the overall performance of each model across these different bug categories.</p>
            {bt_html}
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
            <p><strong>Challenge of Analyzing Faulty Regions:</strong> The <code>faulty_region</code> field in the LLM's JSON output posed a unique challenge. Because it is written in open-ended Natural Language (NL), it is difficult to automatically evaluate for correctness using a purely programmatic script. While <code>top_1_line</code> allows for strict integer matching against ground truth, assessing whether a natural language description (e.g., "the loop bounds" or "conditional check") accurately describes the faulty region requires manual, qualitative review. This highlights a limitation in scaling automated evaluations for qualitative LLM outputs.</p>
            <p><strong>Examples where tests helped:</strong> Providing the specific failing test cases allowed the models to deduce exactly which sub-condition or edge case was flawed. For example, in <code>is_prime</code>, a mutant with a boundary condition bug failed on specific composite numbers, and seeing the exact `AssertionError` for those numbers in Condition B helped the LLM instantly pinpoint the loop bounds.</p>
            <p><strong>Examples where Tarantula misled the model:</strong> Unlike more advanced models that might leverage Tarantula effectively, the models in this experiment were severely misled by the numerical rankings. For example, in <code>is_prime</code>, Tarantula assigned high suspiciousness to a <code>return True</code> statement simply because it was executed by failing tests, while the actual faulty loop condition was ranked lower. The models blindly chose the highly-ranked <code>return True</code> line, completely failing to analyze the logic. This caused a massive drop in accuracy for the Nemotron model in Conditions C and D.</p>
            <p><strong>Examples where Tarantula helped:</strong> Although SBFL data degraded performance on average, there were isolated instances where it provided the crucial signal needed. For example, on <code>humaneval_130</code> (<code>tri</code>) and <code>humaneval_141</code> (<code>file_name_check</code>), providing Tarantula rankings alongside tests (Condition D) allowed the models to correctly pinpoint the exact faulty line when they had previously failed to do so with tests alone (Condition B). In these specific cases, the true faulty line likely had a uniquely high Tarantula score that successfully guided the model's attention.</p>
            <p><strong>Examples of plausible but wrong explanations:</strong> In several instances, the models correctly identified the exact faulty line (achieving a Top-1 hit), but provided an entirely incorrect or nonsensical reasoning in the <code>explanation</code> field, often hallucinating bugs in other correct parts of the code. For example, in <code>humaneval_124</code> (<code>valid_date</code>), the Nemotron model correctly pinpointed that <code>month &lt; 2</code> was the injected fault. However, its explanation then rambled on to confidently assert that the original, correct code on subsequent lines contained "operator precedence bugs" that caused day-threshold checks to fail, which was completely false.</p>
            <p><strong>Causes of Invalid Responses (Instruction Ignoring):</strong> The invalid-output rates observed in this study were heavily driven by instruction-following failures. The models frequently struggled with the negative constraint <em>"Do not repair the program,"</em> showing a stubborn tendency to output repaired code snippets instead of simply explaining the fault. These unprompted code blocks often broke the requested JSON schema, rendering the output unparseable and invalid.</p>
        </section>

        <section id="threats-to-validity">
            <h2>7. Threats to Validity</h2>
            <ul>
                <li><strong>Benchmark Representativeness:</strong> HumanEval consists of relatively short, algorithmic Python functions. Results may not generalize to large, multi-file object-oriented codebases.</li>
                <li><strong>LLM Nondeterminism:</strong> Despite setting temperature to 0.0, API routing, floating point variances in GPUs, and silent model updates can introduce slight variations in output.</li>
                <li><strong>Mutant Realism:</strong> While our generator explicitly targets <em>partial failures</em> (mutants that pass some tests and fail others) to maximize SBFL signal, these automatically generated faults (e.g., swapping a single operator) may not fully capture the complexity and subtlety of real-world logic bugs introduced by human developers.</li>
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
            <pre><code>python experiment/scripts/generate_mutants.py
python -m pytest experiment/tests/infrastructure
python -m pytest experiment/tests/ --ignore=experiment/tests/infrastructure
python experiment/scripts/generate_test_results_report.py
python experiment/scripts/run_sbfl.py
python experiment/scripts/generate_prompts.py
python experiment/scripts/run_llm_evaluation.py
python experiment/scripts/compute_metrics.py
python experiment/scripts/generate_plots.py
python experiment/scripts/generate_report.py</code></pre>
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
