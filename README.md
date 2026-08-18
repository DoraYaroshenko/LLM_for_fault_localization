# LLMs for Fault Localization

This repository contains the infrastructure and data for an empirical software engineering study on using Large Language Models (LLMs) for fault localization in Python methods.

## Overview
The goal of this assignment is to compare how well LLMs can identify faulty lines in buggy Python methods under different information conditions:
- Condition A: Code Only
- Condition B: Code + Tests
- Condition C: Code + Spectrum-Based Fault Localization (Tarantula SBFL)
- Condition D: Code + Tests + SBFL

## Project Structure
- `dataset/`: Contains metadata and the generated buggy versions (mutants).
- `scripts/`: Automation scripts for dataset fetching, mutant generation, testing, and querying LLMs.
- `src/`: Original, verified HumanEval methods used as the benchmark.
- `tests/`: Pytest suites corresponding to the methods, as well as infrastructure tests for our own scripts.
- `results/`: Intermediate test results, metrics, and JSON LLM responses.
- `website/`: Static HTML site for presenting the final results.

## Setup & Reproducibility
### Requirements
- Python 3.12+
- Pytest
- Coverage.py

### Initialization
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Reproducing Phase 1 (Dataset & Mutation)
```bash
python scripts/fetch_human_eval.py
python scripts/generate_mutants.py
pytest tests/ --ignore=tests/infrastructure
```

### Reproducing Phase 2 (SBFL & Coverage)
```bash
python scripts/run_sbfl.py
```

### Reproducing Phase 3 (LLM Evaluation)
Requires `openrouter_keys.json` with valid API keys.
```bash
python scripts/generate_prompts.py
python scripts/run_llm_evaluation.py
python scripts/compute_metrics.py
```

### Reproducing Phase 4 (Artifacts & HTML Report)
```bash
python scripts/generate_plots.py
python scripts/generate_report.py
```
After running, open `website/index.html` in your browser.
