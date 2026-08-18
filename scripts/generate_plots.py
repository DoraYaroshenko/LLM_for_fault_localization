import json
import os
import matplotlib.pyplot as plt
import numpy as np

def generate_plots():
    metrics_path = "results/metrics.json"
    assets_dir = "website/assets"

    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    models = [m for m in metrics.keys() if m != 'overall']
    conditions = ["A", "B", "C", "D"]
    
    # 1. Accuracy per condition for each model
    for model in models:
        top1_acc = [metrics[model][cond]["top_1_acc"] for cond in conditions]
        top3_acc = [metrics[model][cond]["top_3_acc"] for cond in conditions]
        region_acc = [metrics[model][cond]["region_acc"] for cond in conditions]

        x = np.arange(len(conditions))
        width = 0.25

        fig, ax = plt.subplots(figsize=(8, 5))
        rects1 = ax.bar(x - width, top1_acc, width, label='Top-1 Acc', color='#4C72B0')
        rects2 = ax.bar(x, top3_acc, width, label='Top-3 Acc', color='#55A868')
        rects3 = ax.bar(x + width, region_acc, width, label='Region Acc', color='#C44E52')

        ax.set_ylabel('Accuracy')
        ax.set_title(f'Accuracy by Condition for {model}')
        ax.set_xticks(x)
        ax.set_xticklabels([f"Condition {c}" for c in conditions])
        ax.legend()
        ax.set_ylim([0, 1.05])
        
        plt.tight_layout()
        plt.savefig(os.path.join(assets_dir, f"{model}_conditions.png"), dpi=300)
        plt.close()

    # 2. Overall Model Comparison
    overall_top1 = [metrics[model]["overall"]["top_1_acc"] for model in models]
    overall_top3 = [metrics[model]["overall"]["top_3_acc"] for model in models]
    overall_region = [metrics[model]["overall"]["region_acc"] for model in models]

    x = np.arange(len(models))
    width = 0.25

    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width, overall_top1, width, label='Overall Top-1', color='#4C72B0')
    rects2 = ax.bar(x, overall_top3, width, label='Overall Top-3', color='#55A868')
    rects3 = ax.bar(x + width, overall_region, width, label='Overall Region', color='#C44E52')

    ax.set_ylabel('Accuracy')
    ax.set_title('Overall Accuracy by Model')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.set_ylim([0, 1.05])
    
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "overall_models.png"), dpi=300)
    plt.close()
    
    print("Plots generated successfully in website/assets/")

if __name__ == "__main__":
    generate_plots()
