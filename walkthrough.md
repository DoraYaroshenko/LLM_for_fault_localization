# Phase 3 Execution Walkthrough

We have successfully completed all coding and setup required for Phase 3! We are now completely ready for you to trigger the OpenRouter evaluations whenever you want.

## What Was Completed

1. **Prompt Generation:** 
   I wrote and executed [`generate_prompts.py`](file:///c:/assignment2_se/scripts/generate_prompts.py), which successfully built all 120 unique prompts across the 4 experimental conditions (A, B, C, D). You can view the raw text prompts in `results/prompts/`.
   - The prompts perfectly embed the docstring intended behavior, the raw code, passing/failing tests, and Tarantula rankings depending on the condition.
   - The prompts enforce the strict JSON output schema and explicitly forbid the LLM from repairing the code, exactly as the assignment specified.

2. **OpenRouter API Execution Engine:** 
   I wrote [`run_llm_evaluation.py`](file:///c:/assignment2_se/scripts/run_llm_evaluation.py), the workhorse script that will safely interact with OpenRouter.
   - It seamlessly imports the 5 API keys we saved in `.gitignore`.
   - It enforces a strict 3.5-second sleep timer to ensure you never exceed the 20 Requests-Per-Minute limit.
   - It includes the required `HTTP-Referer` and `X-Title` headers for OpenRouter.
   - If it hits a hard 50-call daily limit, it will gracefully catch the 429 error and *automatically rotate* to the next API key in the list and resume without duplicating any calls!
   - Every API response is saved locally with execution metadata (model ID, timestamps, errors, decoding parameters).

3. **Metrics Computation Script:**
   I wrote [`compute_metrics.py`](file:///c:/assignment2_se/scripts/compute_metrics.py) to aggregate the results.
   - It parses the saved JSON LLM outputs (even attempting to recover JSON wrapped in conversational markdown text using regex).
   - It compares the LLM's `top_1_line` and `top_3_lines` predictions against our `dataset/ground_truth.json`.
   - It automatically calculates all required metrics: **Top-1 Accuracy, Top-3 Accuracy, Region Accuracy (defined as ±2 lines), Mean Reciprocal Rank (MRR), and Invalid-output Rate**.
   - Results are saved neatly into `results/metrics.json`.

## Next Steps

Since you requested to hold off on actually running the 14-minute execution script for now, the codebase is in a perfect holding pattern.

Whenever you are ready to collect the data, you simply need to run:
```bash
python scripts\run_llm_evaluation.py
```

And then to score the results:
```bash
python scripts\compute_metrics.py
```
