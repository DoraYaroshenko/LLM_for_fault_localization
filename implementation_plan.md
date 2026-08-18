# Assignment 2: LLMs for Fault Localization - Implementation Plan

This plan outlines the structured approach to implementing the entire automated experimental pipeline, evaluating LLMs for fault localization, and producing the required artifacts (HTML report, reproducible repository, and data for the video).

## User Review Required

> [!IMPORTANT]
> The plan has been updated based on your feedback. We will use the official `openai/human-eval` repo, `mutmut` for mutation (with strict validation), and selected free OpenRouter models (with rate limit handling). Please review the finalized plan below. If everything looks good, we can begin execution!

---

## Proposed Implementation Phases

The plan is divided into four main phases (aligning with the assignment's suggested weekly milestones).

### Phase 1: Dataset Construction & Validation Setup (Week 1)
**Goal:** Establish the benchmark dataset, the testing framework, and the mutation logic.

1. **Project Skeleton & Tooling Setup:**
   - Initialize Git repository structure (`src/`, `tests/`, `dataset/`, `scripts/`, `results/`).
   - Setup `pytest`, `pytest-cov` for testing and coverage.
   - Define the `requirements.txt` / `pyproject.toml`.

2. **Benchmark Selection (HumanEval):**
   - Fetch at least 30 methods from the official repository: [openai/human-eval](https://github.com/openai/human-eval).
   - Ensure each method has a natural language spec and at least 10 tests. (We may need to augment HumanEval tests to reach the minimum of 10 per method).

3. **Mutant Generation Engine:**
   - Use the `mutmut` library to automatically generate mutant candidates for the selected Python methods.
   - Implement strict validation logic to ensure exactly one bug per method is kept. The validation must confirm:
     - The original method passes all tests.
     - The mutant fails $\ge 1$ test.
     - The mutant is not equivalent.
   - Record the ground-truth faulty line/region for each valid mutant.

4. **Infrastructure Testing (Part 1):**
   - Write tests for the mutant generation engine to prove it works correctly.

### Phase 2: SBFL & Core Automation (Week 2)
**Goal:** Automate test execution, collect coverage, compute Tarantula scores, and prepare for LLM queries.

1. **Test Execution & Coverage Collection:**
   - Create a script that runs `pytest` on a given buggy method.
   - Use `coverage.py` API or `pytest-cov` JSON output to map line numbers to pass/fail execution counts.

2. **Tarantula Computation Engine:**
   - Implement the Tarantula formula.
   - Script takes the coverage data and outputs a ranked list (or dictionary) of line suspiciousness scores.
   
3. **Infrastructure Testing (Part 2):**
   - Write tests verifying the Tarantula calculation logic and the coverage aggregation.

### Phase 3: LLM Integration & Evaluation (Week 3)
**Goal:** Query the LLMs under 4 conditions, parse results, and compute metrics.

1. **Prompt Template Generation:**
   - Design the fixed prompt template enforcing JSON output.
   - Implement logic to build the prompt for the 4 conditions:
     - **A:** Code Only
     - **B:** Code + Tests
     - **C:** Code + Tarantula SBFL
     - **D:** Code + Tests + Tarantula SBFL

2. **OpenRouter API Integration:**
   - Write the querying engine using `requests` or `openai` python client configured for OpenRouter.
   - **Models Selected:** We will use free coding models. Good options based on your suggestions and current availability are:
     - `"cohere/north-mini-code:free"`
     - `"qwen/qwen3-next-80b-a3b-instruct:free"` (or similar Qwen coder variants)
     - Alternative/Backup: `"poolside/laguna-m1:free"`
   - **Rate Limiting:** Free models have strict rate limits (e.g., 20 requests per minute). The engine MUST implement sleep/retry logic, handle HTTP 429 errors gracefully, and save **all** raw outputs locally to prevent data loss.

3. **Parsing & Metric Computation:**
   - Parse JSON outputs to extract `top_1_line`, `top_3_lines`, `faulty_region`.
   - Calculate metrics: Top-1 accuracy, Top-3 accuracy, Region accuracy, MRR, Invalid-output rate.

4. **Infrastructure Testing (Part 3):**
   - Write tests for the JSON parsing, OpenRouter client wrapper (mocked), and metrics calculation algorithms.

### Phase 4: Artifact Generation & HTML Report (Week 4)
**Goal:** Compile everything into a professional, static HTML website and finalize the reproducible artifact.

1. **HTML Generator Script:**
   - Use a static site generator (e.g., Jinja2 templates or simple markdown-to-html tools like MkDocs/Sphinx, or custom Python script writing HTML).
   - Generate sections: Overview, Dataset tables, Validation proof, Results (tables/plots), Qualitative Analysis, Threats to Validity, AI tools.

2. **Result Aggregation & Plotting:**
   - Use `matplotlib` or `seaborn` to generate plots for the HTML report.

3. **Reproducibility Polish:**
   - Finalize `README.md` with exact reproduction commands (e.g., `make dataset`, `make run_llm`, `make report`).
   - Document environment setup.

## Verification Plan

### Automated Tests
- `pytest tests/infrastructure/` -> Will verify our own experiment logic (mutation, SBFL, parsing, metrics).
- Coverage reports for the infrastructure code to ensure we are testing our test-runners.

### Manual Verification
- Review generated HTML site to ensure it meets all rubric requirements.
- Inspect the raw JSON outputs and parsed metrics to sanity-check the LLM evaluation.
- Review a sample of the generated mutants to confirm they are realistic and not equivalent.
