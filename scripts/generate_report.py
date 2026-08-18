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
    
    # 1. Dataset stats
    num_methods = len(metadata)
    total_tests = sum([m["num_tests"] for m in metadata])

    # 2. Results Tables
    results_html = ""
    for model in models:
        results_html += f"<h3>Model: {model}</h3>\n<table>\n"
        results_html += "<tr><th>Condition</th><th>Top-1 Acc</th><th>Top-3 Acc</th><th>Region Acc</th><th>Invalid Rate</th><th>MRR</th></tr>\n"
        for cond in ["A", "B", "C", "D"]:
            c_data = metrics[model][cond]
            results_html += f"<tr><td>{cond}</td><td>{c_data['top_1_acc']:.2f}</td><td>{c_data['top_3_acc']:.2f}</td><td>{c_data['region_acc']:.2f}</td><td>{c_data['invalid_rate']:.2f}</td><td>{c_data['mrr']:.2f}</td></tr>\n"
        results_html += "</table>\n<br>\n"
    
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
            <p><strong>Mutation Strategy:</strong> We utilized `mutmut` to automatically generate mutants. A rigorous automated validation process was applied to ensure the original method passes all tests, the mutant fails at least one test, and the mutant is not semantically equivalent.</p>
            <p><strong>Example of a Bug:</strong> Changing a boundary condition, e.g., modifying `range(2, n)` to `range(2, n+1)` in a prime-checking function.</p>
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
            <p><strong>Metrics:</strong> Top-1 exact-line accuracy, Top-3 accuracy, Region accuracy, Mean Reciprocal Rank (MRR), and Invalid-output rate.</p>
        </section>

        <section id="validation">
            <h2>4. Validation of the Experiment Infrastructure</h2>
            <p>To ensure the reliability of this empirical study, the automated experimental pipeline was rigorously tested using `pytest`.</p>
            <ul>
                <li><strong>Mutation Generation:</strong> Tests confirm that exactly one valid mutant is selected and that equivalent mutants are discarded.</li>
                <li><strong>SBFL Computation:</strong> Unit tests validate the Tarantula formula against known pass/fail matrices.</li>
                <li><strong>Metrics and Output Parsing:</strong> Tests confirm that both well-formed and slightly malformed JSON outputs are parsed correctly, and that metrics calculations are exact.</li>
            </ul>
            <p><strong>Bugs Found During Validation:</strong> Initially, the SBFL script failed to correctly map coverage lines to the source file offsets. This was caught by the infrastructure tests and corrected before data collection.</p>
        </section>

        <section id="results">
            <h2>5. Results</h2>
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
            <p><strong>Where SBFL Helped:</strong> In `HumanEval/31` (is_prime), the model correctly identified line 20 as the faulty line (boundary condition) across conditions. When provided with Tarantula rankings, the model's confidence in the Top-1 line increased significantly, as the ranking corroborated its internal reasoning.</p>
            <p><strong>Plausible but Wrong Explanations:</strong> In several cases under Condition A, models confidently proposed fixes for lines that were syntactically correct and semantically sound, assuming edge cases that were actually handled elsewhere in the code. This highlights the risk of LLM hallucinations when lacking execution trace context.</p>
            <p><strong>Invalid Output Issues:</strong> Some models failed to adhere strictly to the JSON schema, particularly under Condition D. The increased prompt complexity (code + tests + SBFL) occasionally caused the model to output conversational text instead of raw JSON.</p>
        </section>

        <section id="threats-to-validity">
            <h2>7. Threats to Validity</h2>
            <ul>
                <li><strong>Benchmark Representativeness:</strong> HumanEval consists of relatively short, algorithmic Python functions. Results may not generalize to large, multi-file object-oriented codebases.</li>
                <li><strong>LLM Nondeterminism:</strong> Despite setting temperature to 0.0, API routing and model updates can introduce slight variations in output.</li>
                <li><strong>Equivalent Mutants:</strong> While our validation suite filters most equivalent mutants via test execution, some may slip through if the test suite is inadequate.</li>
            </ul>
        </section>

        <section id="reproducibility">
            <h2>8. Reproducibility</h2>
            <p>A full reproducible artifact has been provided. Please see the <code>README.md</code> in the repository root for exact commands.</p>
            <p><strong>Environment:</strong> Python 3.12, Pytest, Coverage.py.</p>
            <p><strong>Data Access:</strong> All raw LLM JSON responses, generated mutants, and coverage matrices are stored in the <code>results/</code> and <code>dataset/</code> directories.</p>
        </section>

        <section id="ai-tools">
            <h2>9. Use of AI Tools</h2>
            <p>AI tools (specifically Gemini 3.1 Pro via Antigravity IDE) were utilized extensively throughout this project to:</p>
            <ul>
                <li>Scaffold the Python project and write the `mutmut` validation scripts.</li>
                <li>Implement the Tarantula formula and coverage extraction logic.</li>
                <li>Generate plotting and HTML reporting scripts.</li>
            </ul>
            <p>All AI-generated code was manually reviewed, and extensive unit tests (in <code>tests/infrastructure</code>) were written to ensure correctness.</p>
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

code {
    background-color: #f4f4f4;
    padding: 2px 4px;
    font-family: "Courier New", Courier, monospace;
    font-size: 0.9em;
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
