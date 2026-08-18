# Phase 3: LLM Integration & Evaluation - Implementation Plan

This plan details the execution strategy for Phase 3, specifically focusing on building an extremely robust OpenRouter API pipeline. Since we are dealing with strict free-tier rate limits and a tight deadline, our design prioritizes **zero waste**, **checkpointing**, and **safe execution**.

## User Review Required

> [!CAUTION]
> **ChatGPT was correct:** OpenRouter's free tier has a strict limit of **50 requests per day** and **20 requests per minute**. Furthermore, any failed requests or 429 (Rate Limit) errors *still count* against this 50-request daily limit.
> 
> Because we need 240 requests (30 methods × 4 conditions × 2 models) and you only have a few days, we cannot afford to lose requests to script crashes, bad prompts, or retry loops.

### The Strategy for Limits: Automatic API Key Rotation

Since you have elected to use multiple OpenRouter accounts (Option B), we will seamlessly rotate through the 5 provided API keys to cover the 240 required calls.
- **Secure Storage:** The 5 API keys have been saved to `openrouter_keys.json`, and this file has been added to `.gitignore` so they will never be committed.
- **Automatic Rotation:** Our script will load this JSON array. It will start with the first key. When it detects that a key has hit its daily limit (after verifying it's not just a minute throttle), the script will *automatically* catch the exception, log the switch, and seamlessly rotate to the next key in the list and resume exactly where it left off. You will not need to manually swap keys or restart the script.

### OpenRouter API Format
As requested, we will use the exact header format specified by OpenRouter in our python `requests` calls:
```python
headers = {
    "Authorization": f"Bearer {current_api_key}",
    "HTTP-Referer": "https://github.com/DoraYaroshenko/LLM_for_fault_localization", # Your repo URL
    "X-Title": "LLMs for Fault Localization", # Project title
    "Content-Type": "application/json"
}
```

### Selected Models
Based on an investigation of currently available free OpenRouter models tailored for coding and programming, we will evaluate these two models:
1. `"poolside/laguna-m1:free"` - A flagship free model specifically designed for complex, agentic coding tasks.
2. `"qwen/qwen3-next-80b-a3b-instruct:free"` (or equivalent Qwen Coder variant) - Known for strong code generation and reasoning.

---

## 1. Prompt Generation & Verification (Zero Waste Strategy)

To ensure we don't waste API calls on bad prompts, we will separate prompt generation from the API execution.

- **Step 1:** Write a Python script (`generate_prompts.py`) that generates the exact prompt strings for all 240 combinations. 
  - **Required JSON Schema:** The prompt must ask the LLM to return this exact JSON structure:
    ```json
    { 
    "top_1_line": 12, 
    "top_3_lines": [12, 14, 9], 
    "faulty_region": "loop condition", 
    "explanation": "..." 
    }
    ```
  - **Mandatory Instruction:** The prompt MUST explicitly state: *"Do not repair the program. Your task is only to identify the most likely faulty line or small faulty region."*
  - **Condition Logic:** The script will build 4 versions (A, B, C, D) ensuring conditions C and D receive only the Tarantula ranking and NOT the ground truth.
- **Step 2:** Save these prompts locally as JSON files (e.g., `results/prompts/{method_id}_{condition}.txt`).
- **Step 3:** We will manually review 2-3 of these generated prompts before we make a single API call.

## 2. API Execution Engine (Checkpointing & Rate Limits)

We will build `run_llm_evaluation.py` with the following rigid safeguards:

### Execution Metadata Logging (Assignment Requirement)
- For every OpenRouter call, we must record metadata alongside the raw response. We will save a JSON object containing:
  - Exact OpenRouter model IDs
  - Date and time of execution
  - Decoding parameters (we will use `temperature=0.0` for reproducibility)
  - Number of repetitions (set to 1)
  - Any HTTP errors or rate-limit warnings encountered during the call.

### Caching to Prevent Duplicates
- **Local Storage First:** Before making an API call, the script will check if `results/raw_responses/{model}/{method}_{condition}.json` exists.
- **Skip Logic:** If the file exists, the script will skip the API call. This ensures that if the script crashes or halts, restarting it will cost **0 API calls** for already completed tasks.
- **Malformed Outputs:** Even if the LLM returns garbage (non-JSON text), we will save it to the file. We will NOT automatically retry it. Retrying burns our quota. A malformed output is simply recorded as an "Invalid" result for our metrics.

### Rate Limit Handling (20 RPM & 50/Day Distinction)
- **Sleep Timer:** We will enforce a strict `time.sleep(3.5)` between every request. This naturally keeps us under the 20 Requests Per Minute limit.
- **Distinguishing Limits:** If the script receives an HTTP 429 (Too Many Requests) error, we need to know if it's the minute limit or the daily limit:
  - We will implement a `Minute Call Counter` locally.
  - When a 429 occurs, the script will automatically pause for **60 seconds** (to completely clear any per-minute throttling) and retry the *exact same request once*.
  - If the retry *also* fails with a 429, we can confidently declare that the **50-call daily limit** has been reached.
  - At this point, the script will **automatically rotate to the next API key** from `openrouter_keys.json` and retry the request, continuing until all keys are exhausted.

## 3. Parsing & Metric Computation

Once all 240 responses are safely saved on disk, we will run a separate script (`compute_metrics.py`) to evaluate the results offline.

- **Parsing:** It will read the raw text from the saved JSON response files and extract the JSON payload.
- **Fallback Regex:** If the LLM wraps the JSON in markdown blockquotes (e.g., ````json ... ````) or adds conversational text, we will use regex to extract the JSON block.
- **Scoring:** Compute Top-1, Top-3, and Region accuracy by comparing the LLM's prediction with our dataset's ground truth.

## Proposed Changes

We will create/modify the following files during execution:

#### [NEW] `scripts/generate_prompts.py`
Builds all 240 prompts and saves them locally for manual review.

#### [NEW] `scripts/run_llm_evaluation.py`
The robust OpenRouter API runner with checkpointing, 3.5s sleep delays, and graceful handling of 429 errors.

#### [NEW] `scripts/compute_metrics.py`
Reads the local response files, parses the JSON (using regex if needed), and calculates the evaluation metrics.

## Verification Plan

### Automated Tests
- Test the prompt generation logic to ensure Tarantula scores and test results are formatted correctly.
- Test the JSON parsing logic with mocked "messy" LLM outputs (e.g., JSON wrapped in markdown) to ensure we can extract the data without needing to re-query the LLM.

### Manual Verification
- Before executing `run_llm_evaluation.py`, visually inspect the output of `generate_prompts.py`.
- Run the API script for 1 single method to ensure the OpenRouter connection is valid and the response is saved properly.
