import json
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_results(json_path, save_path):
    # Ensure output folder exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Load JSON results
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    counts = data["counts"]

    # Categories / answers
    answers = ["Agree", "No opinion", "Disagree"]
    languages = ["en", "bg"]

    # Prepare data for Seaborn
    plot_data = []
    for lang in languages:
        for ans in answers:
            plot_data.append({"Language": lang.upper(), "Answer": ans, "Count": counts[lang][ans]})

    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(plot_data)

    # Set Seaborn style
    sns.set(style="whitegrid")

    # Plot grouped bar chart
    plt.figure(figsize=(8,6))
    ax = sns.barplot(x="Answer", y="Count", hue="Language", data=df, palette="muted")

    # Titles and labels
    plt.title(f"Results for category {data['category'].capitalize()} ")
    plt.ylabel("Number of responses")
    plt.xlabel("Answer")
    plt.ylim(0, max(max(counts["en"].values()), max(counts["bg"].values())) + 1)

    # Add counts on top of bars
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f"{int(height)}",
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='bottom', fontsize=10)

    # Save figure
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
