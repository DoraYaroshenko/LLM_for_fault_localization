import json
import os
import re
import glob

GROUND_TRUTH_FILE = "experiment/dataset/ground_truth.json"
BUG_TYPES_FILE = "experiment/dataset/bug_types.json"
RESULTS_DIR = "experiment/results/raw_responses"
METRICS_OUT = "experiment/results/metrics.json"
BUG_TYPE_METRICS_OUT = "experiment/results/metrics_by_bug_type.json"

def extract_json_from_text(text):
    if not isinstance(text, str):
        return None
    
    # Try to find JSON block
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
            
    # Try to find any curly braces
    match = re.search(r'(\{.*?\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
            
    return None

def compute_metrics():
    with open(GROUND_TRUTH_FILE, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)
        
    with open(BUG_TYPES_FILE, 'r', encoding='utf-8') as f:
        bug_types = json.load(f)
        
    models = [d for d in os.listdir(RESULTS_DIR) if os.path.isdir(os.path.join(RESULTS_DIR, d))]
    
    overall_metrics = {}
    metrics_by_bug_type = {}
    
    for model in models:
        model_dir = os.path.join(RESULTS_DIR, model)
        overall_metrics[model] = {
            "A": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0},
            "B": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0},
            "C": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0},
            "D": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0},
            "overall": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0}
        }
        
        for filepath in glob.glob(os.path.join(model_dir, "*.json")):
            basename = os.path.basename(filepath)
            # humaneval_31_A.json
            parts = basename.replace(".json", "").split("_")
            cond = parts[-1]
            safe_id = "_".join(parts[:-1])
            
            gt_line = ground_truth.get(safe_id, {}).get("faulty_line")
            if not gt_line:
                continue
                
            bug_type_full = bug_types.get(safe_id, "unknown")
            bug_type = bug_type_full.split(" ")[0]
            
            if bug_type not in metrics_by_bug_type:
                metrics_by_bug_type[bug_type] = {}
            if model not in metrics_by_bug_type[bug_type]:
                metrics_by_bug_type[bug_type][model] = {
                    "A": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0},
                    "B": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0},
                    "C": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0},
                    "D": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0},
                    "overall": {"total": 0, "top_1": 0, "top_3": 0, "region": 0, "mrr_sum": 0, "invalid": 0}
                }
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            raw_response = data.get("raw_response")
            
            parsed = None
            if isinstance(raw_response, dict):
                # some models might return the json directly if openrouter parses it, but usually it's in choices[0].message.content
                if "choices" in raw_response and len(raw_response["choices"]) > 0:
                    content = raw_response["choices"][0].get("message", {}).get("content", "")
                    parsed = extract_json_from_text(content)
            elif isinstance(raw_response, str):
                parsed = extract_json_from_text(raw_response)
                
            overall_metrics[model][cond]["total"] += 1
            overall_metrics[model]["overall"]["total"] += 1
            metrics_by_bug_type[bug_type][model][cond]["total"] += 1
            metrics_by_bug_type[bug_type][model]["overall"]["total"] += 1
            
            if not parsed or "top_1_line" not in parsed:
                overall_metrics[model][cond]["invalid"] += 1
                overall_metrics[model]["overall"]["invalid"] += 1
                metrics_by_bug_type[bug_type][model][cond]["invalid"] += 1
                metrics_by_bug_type[bug_type][model]["overall"]["invalid"] += 1
                continue
                
            try:
                top_1 = int(parsed.get("top_1_line", -1))
                top_3 = parsed.get("top_3_lines", [])
                if not isinstance(top_3, list):
                    top_3 = []
                top_3 = [int(x) for x in top_3]
            except:
                overall_metrics[model][cond]["invalid"] += 1
                overall_metrics[model]["overall"]["invalid"] += 1
                metrics_by_bug_type[bug_type][model][cond]["invalid"] += 1
                metrics_by_bug_type[bug_type][model]["overall"]["invalid"] += 1
                continue
                
            # Metrics
            is_top_1 = (top_1 == gt_line)
            is_top_3 = (gt_line in top_3) or is_top_1
            is_region = abs(top_1 - gt_line) <= 2  # Define region as +/- 2 lines
            
            rank = 0
            if is_top_1:
                rank = 1
            elif gt_line in top_3:
                try:
                    rank = top_3.index(gt_line) + 1
                except:
                    pass
                    
            mrr = 1.0 / rank if rank > 0 else 0.0
            
            if is_top_1:
                overall_metrics[model][cond]["top_1"] += 1
                overall_metrics[model]["overall"]["top_1"] += 1
                metrics_by_bug_type[bug_type][model][cond]["top_1"] += 1
                metrics_by_bug_type[bug_type][model]["overall"]["top_1"] += 1
            if is_top_3:
                overall_metrics[model][cond]["top_3"] += 1
                overall_metrics[model]["overall"]["top_3"] += 1
                metrics_by_bug_type[bug_type][model][cond]["top_3"] += 1
                metrics_by_bug_type[bug_type][model]["overall"]["top_3"] += 1
            if is_region:
                overall_metrics[model][cond]["region"] += 1
                overall_metrics[model]["overall"]["region"] += 1
                metrics_by_bug_type[bug_type][model][cond]["region"] += 1
                metrics_by_bug_type[bug_type][model]["overall"]["region"] += 1
                
            overall_metrics[model][cond]["mrr_sum"] += mrr
            overall_metrics[model]["overall"]["mrr_sum"] += mrr
            metrics_by_bug_type[bug_type][model][cond]["mrr_sum"] += mrr
            metrics_by_bug_type[bug_type][model]["overall"]["mrr_sum"] += mrr
            
    # Finalize Rates
    for model, conds in overall_metrics.items():
        for cond, counts in conds.items():
            total = counts["total"]
            if total > 0:
                counts["top_1_acc"] = counts["top_1"] / total
                counts["top_3_acc"] = counts["top_3"] / total
                counts["region_acc"] = counts["region"] / total
                counts["invalid_rate"] = counts["invalid"] / total
                counts["mrr"] = counts["mrr_sum"] / total
                
    for bt, b_models in metrics_by_bug_type.items():
        for model, conds in b_models.items():
            for cond, counts in conds.items():
                total = counts["total"]
                if total > 0:
                    counts["top_1_acc"] = counts["top_1"] / total
                    counts["top_3_acc"] = counts["top_3"] / total
                    counts["region_acc"] = counts["region"] / total
                    counts["invalid_rate"] = counts["invalid"] / total
                    counts["mrr"] = counts["mrr_sum"] / total
            
    with open(METRICS_OUT, 'w', encoding='utf-8') as f:
        json.dump(overall_metrics, f, indent=2)
        
    with open(BUG_TYPE_METRICS_OUT, 'w', encoding='utf-8') as f:
        json.dump(metrics_by_bug_type, f, indent=2)
        
    print(f"Metrics computed and saved to {METRICS_OUT} and {BUG_TYPE_METRICS_OUT}")

if __name__ == "__main__":
    compute_metrics()
