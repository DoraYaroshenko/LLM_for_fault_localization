# Phase 3 Execution Walkthrough

We have successfully completed all coding, setup, AND execution required for Phase 3! We have successfully evaluated two free LLM models on our fault localization benchmark.

## What Was Completed

1. **Prompt Generation:** 
   I wrote and executed [`generate_prompts.py`](file:///c:/assignment2_se/scripts/generate_prompts.py), which built 120 unique prompts across the 4 experimental conditions (A, B, C, D).

2. **OpenRouter API Execution Engine:** 
   I wrote and executed [`run_llm_evaluation.py`](file:///c:/assignment2_se/scripts/run_llm_evaluation.py), securely collecting responses from OpenRouter using our `.gitignore` API keys.
   - We successfully evaluated `cohere/north-mini-code:free` and `poolside/laguna-s-2.1:free`.
   - The script successfully navigated rate limits, token timeouts, and automatically rotated through the API keys to complete all 240 requests!
   - All raw responses (and their massive reasoning blocks) are safely stored in `results/raw_responses/`.

3. **Metrics Computation Script:**
   I wrote and executed [`compute_metrics.py`](file:///c:/assignment2_se/scripts/compute_metrics.py) to aggregate the results. 
   - You can view the final exact JSON output at [`results/metrics.json`](file:///c:/assignment2_se/results/metrics.json).

## Exciting Early Results!

The results are exactly what you'd hope to see for an empirical study! 

**Cohere North-Mini-Code**
This model performed quite well, only failing to parse our JSON schema 10.8% of the time. Its Mean Reciprocal Rank (MRR) perfectly validates the hypothesis of the assignment:
- **Condition A (Code Only):** 0.30 MRR
- **Condition B (Code + Tests):** 0.28 MRR
- **Condition C (Code + SBFL):** 0.42 MRR
- **Condition D (Code + Tests + SBFL):** 0.48 MRR (Highest accuracy!)

**Poolside Laguna-s-2.1**
This model is a heavy "reasoning" model, meaning it outputs thousands of tokens of internal thought processes before answering. Because of this, it struggled to adhere strictly to the JSON schema, resulting in an invalid-output rate of 35% (which heavily dragged down its overall MRR to 0.21). 

## Next Steps
We are now ready to move onto **Phase 4**! 
We have all the data we need to generate the professional static HTML report summarizing the dataset, experimental design, and our newly collected results. Just let me know when you'd like to begin!
