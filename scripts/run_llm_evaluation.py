import json
import os
import time
import requests
from datetime import datetime, timezone

MODELS = [
    "cohere/north-mini-code:free",
    "poolside/laguna-s-2.1:free"
]

DATASET_META = "dataset/final_metadata.json"
PROMPTS_DIR = "results/prompts"
RESULTS_DIR = "results/raw_responses"
KEYS_FILE = "openrouter_keys.json"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        print(f"Error: {KEYS_FILE} not found.")
        exit(1)
    with open(KEYS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_evaluation():
    api_keys = load_keys()
    if not api_keys:
        print("Error: No API keys found in the keys file.")
        exit(1)
        
    current_key_idx = 0
    
    with open(DATASET_META, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
        
    for model_id in MODELS:
        model_safe_name = model_id.replace("/", "_").replace(":", "_")
        model_results_dir = os.path.join(RESULTS_DIR, model_safe_name)
        os.makedirs(model_results_dir, exist_ok=True)
        
        for task in tasks:
            safe_id = task['safe_id']
            
            for cond in ["A", "B", "C", "D"]:
                result_filepath = os.path.join(model_results_dir, f"{safe_id}_{cond}.json")
                
                # Checkpointing: Skip if already done
                if os.path.exists(result_filepath):
                    print(f"Skipping {model_safe_name} - {safe_id} - Condition {cond} (Already exists)")
                    continue
                    
                prompt_filepath = os.path.join(PROMPTS_DIR, f"{safe_id}_{cond}.txt")
                with open(prompt_filepath, 'r', encoding='utf-8') as f:
                    prompt_text = f.read()
                    
                print(f"Running {model_id} for {safe_id} Condition {cond}...")
                
                # Rate limit handling loop
                while True:
                    current_key = api_keys[current_key_idx]
                    
                    headers = {
                        "Authorization": f"Bearer {current_key}",
                        "HTTP-Referer": "https://github.com/DoraYaroshenko/LLM_for_fault_localization",
                        "X-Title": "LLMs for Fault Localization",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": model_id,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt_text
                            }
                        ],
                        "temperature": 0.0
                    }
                    
                    response_metadata = {
                        "model_id": model_id,
                        "execution_time": datetime.now(timezone.utc).isoformat() + "Z",
                        "decoding_parameters": {"temperature": 0.0},
                        "prompt_format": f"Condition {cond}",
                        "repetitions": 1,
                        "errors": [],
                        "raw_response": None
                    }
                    
                    time.sleep(3.5) # Hard limit of ~17 requests per minute
                    
                    try:
                        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
                        
                        if response.status_code == 429:
                            print("Received 429 Too Many Requests. Waiting 60 seconds to clear minute throttle...")
                            response_metadata["errors"].append("429 Too Many Requests (First occurrence)")
                            time.sleep(60)
                            
                            # Retry exact same request
                            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
                            
                            if response.status_code == 429:
                                print(f"Received 429 again. Daily limit reached for key index {current_key_idx}.")
                                current_key_idx += 1
                                if current_key_idx >= len(api_keys):
                                    print("FATAL ERROR: All API keys have been exhausted!")
                                    exit(1)
                                print(f"Rotating to API key index {current_key_idx} and retrying...")
                                continue # Retry the while loop with new key
                                
                        if response.status_code != 200:
                            print(f"API Error {response.status_code}: {response.text}")
                            response_metadata["errors"].append(f"HTTP {response.status_code}: {response.text}")
                            response_metadata["raw_response"] = response.text
                        else:
                            resp_json = response.json()
                            response_metadata["raw_response"] = resp_json
                            
                    except Exception as e:
                        print(f"Request exception: {str(e)}")
                        response_metadata["errors"].append(str(e))
                        response_metadata["raw_response"] = str(e)
                    
                    # Save response (even if malformed or errored, unless it's a 429 that rotated the key)
                    with open(result_filepath, 'w', encoding='utf-8') as f:
                        json.dump(response_metadata, f, indent=2)
                        
                    break # Break out of rate limit loop on success or non-429 error

if __name__ == "__main__":
    run_evaluation()
