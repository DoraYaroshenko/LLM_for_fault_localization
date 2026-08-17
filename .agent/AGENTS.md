# Project Rules: Assignment 2 - LLMs for Fault Localization

This file stores project-specific rules that I will remember across all our chats in this workspace. 

## Context
We are working on an empirical software engineering study on the use of LLMs for fault localization in Python methods, focusing on HumanEval, Tarantula SBFL, and OpenRouter API (comparing at least 2 models).

## Behavior Guidelines
1. **Testing First**: All Python code must be tested using `pytest` or `unittest`. Follow Arrange-Act-Assert.
2. **Quality & Validation**: Our own experimental infrastructure (mutation, SBFL, prompt generation, metric computation) must be covered by tests.
3. **Artifact Construction**: We are building a reproducible artifact. All steps should be automated and executable via clear commands.
4. **Data Handling**: Raw LLM outputs (even malformed) must be saved for metrics.
5. **No AI Cheating**: The focus is analyzing LLM fault localization capabilities. Ensure the prompt explicitly instructs the LLM *not* to repair the program, only to identify the faulty line/region.

(You can add more rules here as we progress!)

## Step-by-Step Implementation Rules

### Phase 1: Dataset Construction
- **Method Selection**: Select at least 30 Python methods (e.g., from HumanEval), ensuring each has a natural-language specification and at least 10 tests.
- **Mutation Requirements**: Generate exactly 1 buggy version per method. The original must pass all tests, and the mutant must fail at least one test. The bug must be localizable, not equivalent, and the ground-truth faulty line/region must be known.
- **Validation**: Validate that the tests correctly identify the failure and the original code passes.

### Phase 2: Test Execution & SBFL (Tarantula)
- **Coverage & Tests**: Automate the execution of tests on the buggy methods to identify passing and failing tests, and collect code coverage.
- **SBFL Calculation**: Implement the Tarantula formula (`suspiciousness(s)`) correctly using the execution counts of passing and failing tests.
- **Infrastructure Testing**: Write fast, independent tests to validate your mutation code, SBFL calculation, and coverage aggregation.

### Phase 3: LLM Evaluation & Automation
- **API Setup**: Use the OpenRouter API to query at least two different LLM models. Record exact models, parameters, and prompts.
- **Experimental Conditions**: Run queries for 4 conditions: A (Code Only), B (Code + Tests), C (Code + SBFL), D (Code + Tests + SBFL). Do NOT provide the ground truth to the LLM.
- **Prompt Engineering**: Use a fixed template requesting JSON output (`top_1_line`, `top_3_lines`, `faulty_region`, `explanation`). Explicitly instruct the LLM: *"Do not repair the program. Your task is only to identify the most likely faulty line or small faulty region."*
- **Data Collection**: Save all raw outputs (even if malformed) and automate the parsing and scoring (Top-1, Top-3, Region, MRR, Invalid-output rate).

### Phase 4: Final Artifacts & Reporting
- **HTML Report**: Automate the generation of a professional static HTML website containing all required sections (Overview, Dataset, Experimental Design, Validation, Results, Qualitative Analysis, Threats to Validity, Reproducibility, AI Tools).
- **Reproducibility**: Provide exact commands, environment setup details, and a clean repository.
- **Video Materials**: Ensure the repository/data contains everything needed (plots, screenshots, validation evidence) to create the 5-10 minute presentation video.
