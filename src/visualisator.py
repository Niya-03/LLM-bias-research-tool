import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os
import pandas as pd


def answer_to_number(answer):
    """
    Convert answer string (English or Bulgarian) to a standardized number for comparison.
    Agree/Съгласен → 1
    No opinion/Нямам мнение → 0
    Disagree/Несъгласен → -1
    """
    answer = answer.strip() if isinstance(answer, str) else answer
    
    mapping = {
        "Agree": 1,
        "Съгласен": 1,
        "No opinion": 0,
        "Нямам мнение": 0,
        "Disagree": -1,
        "Не съм съгласен": -1,
    }
    
    return mapping.get(answer, None)



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


def plot_language_differences(json_path, save_path, category, subcategory, dataset_path=None):
       
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    en_responses = data.get("en", {})
    bg_responses = data.get("bg", {})

    differences = []
    
    en_pos = list(en_responses.get("positive", {}).items())
    bg_pos = list(bg_responses.get("positive", {}).items())
        
    print(f"Comparing {len(en_pos)} positive statements...")
    for i, ((en_stmt, en_ans), (bg_stmt, bg_ans)) in enumerate(zip(en_pos, bg_pos)):
        en_ans_clean = en_ans.strip() if isinstance(en_ans, str) else en_ans
        bg_ans_clean = bg_ans.strip() if isinstance(bg_ans, str) else bg_ans
        print(f"  [{i}] EN: '{en_stmt}' → '{en_ans_clean}'")
        print(f"  [{i}] BG: '{bg_stmt}' → '{bg_ans_clean}'")
        
        en_ans_num = answer_to_number(en_ans_clean)
        bg_ans_num = answer_to_number(bg_ans_clean)
        
        if en_ans_num != bg_ans_num:
            print(f"  ✓ DIFFERENCE FOUND!")
            differences.append({
                "statement_en": en_stmt,
                "statement_bg": bg_stmt,
                "english_answer": en_ans_clean,
                "bulgarian_answer": bg_ans_clean,
                "english_answer_num": en_ans_num,
                "bulgarian_answer_num": bg_ans_num,
                "sentiment": "positive"
            })
    
    en_neg = list(en_responses.get("negative", {}).items())
    bg_neg = list(bg_responses.get("negative", {}).items())
    
    for i, ((en_stmt, en_ans), (bg_stmt, bg_ans)) in enumerate(zip(en_neg, bg_neg)):
        en_ans_num = answer_to_number(en_ans)
        bg_ans_num = answer_to_number(bg_ans)
        
        if en_ans_num != bg_ans_num:
            differences.append({
                "statement_en": en_stmt,
                "statement_bg": bg_stmt,
                "english_answer": en_ans,
                "bulgarian_answer": bg_ans,
                "english_answer_num": en_ans_num,
                "bulgarian_answer_num": bg_ans_num,
                "sentiment": "negative"
            })
    
    
    if not differences:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Няма разлика в дадените отговори на български и на английски",
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        return
    
    df = pd.DataFrame(differences)
    
    diff_summary = []
    for _, row in df.iterrows():
        diff_summary.append({
            "English": row["english_answer_num"],
            "Bulgarian": row["bulgarian_answer_num"],
            "Count": 1
        })
    
    diff_df = pd.DataFrame(diff_summary).groupby(["English", "Bulgarian"]).size().reset_index(name="Count")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    sns.set(style="whitegrid")
    
    answer_mapping = {
        1: "Съгласен",
        -1: "Не съм съгласен",
        0: "Нямам мнение"
    }
    
    diff_df["English"] = diff_df["English"].map(answer_mapping)
    diff_df["Bulgarian"] = diff_df["Bulgarian"].map(answer_mapping)
    
    pivot_data = diff_df.pivot_table(
        values="Count", 
        index="Bulgarian", 
        columns="English", 
        fill_value=0
    )
    
    answer_order = ["Съгласен", "Нямам мнение", "Не съм съгласен"]
    pivot_data = pivot_data.reindex(answer_order, fill_value=0).reindex(answer_order, axis=1, fill_value=0)
    
    pivot_data = pivot_data.astype(int)
    
    cbar = sns.heatmap(pivot_data, annot=True, fmt='d', cmap='YlOrRd', ax=ax, 
                cbar_kws={'label': 'Брой разлики'})
    cbar.collections[0].colorbar.locator = ticker.MaxNLocator(integer=True)
    ax.set_title(f"Честота на разминаване в отговорите\n(Категория: {category}, Подкатегория: {subcategory})")
    ax.set_xlabel("Отговори на английски")
    ax.set_ylabel("Отговори на български")
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()


plot_language_differences('data/results/politics_gpt-5-nano_raw-results_2026-03-13.json', 'data/results/test2.png', 'politics', 'russia')
