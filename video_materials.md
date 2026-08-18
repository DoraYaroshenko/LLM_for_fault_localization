# Video Presentation Materials

This document outlines the suggested structure for the 5-10 minute project presentation video as required by the assignment rubric.

## Recommended Structure & Narration

### 1. Introduction (1 min)
- **Content:** Title slide with project name.
- **Narration:** Briefly explain the goal of the study (evaluating LLM fault localization capabilities using Code, Tests, and Tarantula SBFL).
- **Screenshot:** Show the `README.md` and repository structure (`c:\assignment2_se`).

### 2. Data Collection & Evaluation Setup (2 mins)
- **Content:** Explain HumanEval dataset and the mutation process.
- **Narration:** Describe how mutants were generated and strictly validated. Explain the 4 experimental conditions and the OpenRouter models used.
- **Screenshot:** 
  - Show `dataset/buggy/humaneval_31.py` as an example mutant.
  - Show a snippet of a test from `tests/test_humaneval_31.py`.
  - Show the SBFL output (Tarantula rankings) for that method.

### 3. Validation of Infrastructure (1-2 mins)
- **Content:** Prove that the experimental software itself is correct.
- **Narration:** Discuss the `tests/infrastructure/` suite, mentioning line coverage of the test runners.
- **Screenshot:** 
  - Show `results/infrastructure_coverage.txt` proving high coverage on the mutation and evaluation engines.

### 4. Results (2-3 mins)
- **Content:** Present the metrics.
- **Narration:** Discuss how providing tests (Cond B) and SBFL (Cond C, D) affected Top-1/Top-3 accuracy. Discuss differences between the evaluated models.
- **Screenshot:**
  - Show `website/assets/overall_models.png`.
  - Show `website/assets/cohere_north-mini-code_free_conditions.png`.
  - Show `website/index.html` Results table.

### 5. Conclusions & Limitations (1 min)
- **Content:** Summary of findings, Threats to Validity, AI Tool usage.
- **Narration:** Summarize that SBFL helps, but models struggle with complex JSON schemas when too much context is provided. Mention the use of AI tools (Antigravity IDE / Gemini 3.1 Pro) for automating the study.
- **Screenshot:**
  - The "Use of AI Tools" and "Threats to Validity" sections from `website/index.html`.

## Required Assets checklist for the Video:
- [x] Repository Structure
- [x] Example Methods & Tests (`dataset/buggy/` & `tests/`)
- [x] SBFL Reports (`results/sbfl/` or shown in prompts)
- [x] Test Coverage of Own Code (`results/infrastructure_coverage.txt`)
- [x] HTML Website (`website/index.html`)
- [x] Plots and Graphs (`website/assets/*.png`)
