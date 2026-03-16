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


def plot_language_differences(json_path, save_path, category, subcategory):
       
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    en_responses = data.get("en", {})
    bg_responses = data.get("bg", {})

    differences = []
    
    en_pos = list(en_responses.get("positive", {}).items())
    bg_pos = list(bg_responses.get("positive", {}).items())
        
    for i, ((en_stmt, en_ans), (bg_stmt, bg_ans)) in enumerate(zip(en_pos, bg_pos)):
        en_ans_clean = en_ans.strip() if isinstance(en_ans, str) else en_ans
        bg_ans_clean = bg_ans.strip() if isinstance(bg_ans, str) else bg_ans

        en_ans_num = answer_to_number(en_ans_clean)
        bg_ans_num = answer_to_number(bg_ans_clean)
        
        if en_ans_num != bg_ans_num:
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


def plot_distribution_stacked(json_path, save_path, category, subcategory):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    
    counts = {
        "EN-Positive": {"Agree": 0, "No opinion": 0, "Disagree": 0},
        "EN-Negative": {"Agree": 0, "No opinion": 0, "Disagree": 0},
        "BG-Positive": {"Agree": 0, "No opinion": 0, "Disagree": 0},
        "BG-Negative": {"Agree": 0, "No opinion": 0, "Disagree": 0}
    }
    
    en_responses = data.get("en", {})
    for answer in en_responses.get("positive", {}).values():
        answer_text = answer.strip() if isinstance(answer, str) else answer
        answer_num = answer_to_number(answer_text)
        answer_text = ["Disagree", "No opinion", "Agree"][answer_num + 1]
        counts["EN-Positive"][answer_text] += 1
    
    for answer in en_responses.get("negative", {}).values():
        answer_text = answer.strip() if isinstance(answer, str) else answer
        answer_num = answer_to_number(answer_text)
        answer_text = ["Disagree", "No opinion", "Agree"][answer_num + 1]
        counts["EN-Negative"][answer_text] += 1
    
    bg_responses = data.get("bg", {})
    for answer in bg_responses.get("positive", {}).values():
        answer_text = answer.strip() if isinstance(answer, str) else answer
        answer_num = answer_to_number(answer_text)
        answer_text = ["Disagree", "No opinion", "Agree"][answer_num + 1]
        counts["BG-Positive"][answer_text] += 1
    
    for answer in bg_responses.get("negative", {}).values():
        answer_text = answer.strip() if isinstance(answer, str) else answer
        answer_num = answer_to_number(answer_text)
        answer_text = ["Disagree", "No opinion", "Agree"][answer_num + 1]
        counts["BG-Negative"][answer_text] += 1
    
    categories = ["EN-Positive", "EN-Negative", "BG-Positive", "BG-Negative"]
    agree = [counts[cat]["Agree"] for cat in categories]
    no_opinion = [counts[cat]["No opinion"] for cat in categories]
    disagree = [counts[cat]["Disagree"] for cat in categories]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x_pos = range(len(categories))
    bar_width = 0.6
    
    p1 = ax.bar(x_pos, agree, bar_width, label="Съгласен", color="#2ecc71")
    p2 = ax.bar(x_pos, no_opinion, bar_width, bottom=agree, label="Нямам мнение", color="#f39c12")
    p3 = ax.bar(x_pos, disagree, bar_width, bottom=[agree[i] + no_opinion[i] for i in range(len(agree))], 
                label="Не съм съгласен", color="#e74c3c")
    # extra space
    totals = [agree[i] + no_opinion[i] + disagree[i] for i in range(len(agree))]
    ax.set_ylim(0, max(totals) * 1.2)
    
    ax.set_xlabel("Език - Полярност", fontsize=12, fontweight="bold")
    ax.set_ylabel("Брой", fontsize=12, fontweight="bold")
    ax.set_title(f"Дистрибуция на отговорите\nКатегория: {category}, Подкатегория: {subcategory}", 
                 fontsize=14, fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories)
       
    
    ax.legend(loc="best", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    
    for i, cat in enumerate(categories):
        y_offset = 0
        
        if agree[i] > 0:
            ax.text(i, y_offset + agree[i]/2, str(agree[i]), ha="center", va="center", 
                   fontweight="bold", color="white", fontsize=9)
            y_offset += agree[i]
        
        if no_opinion[i] > 0:
            ax.text(i, y_offset + no_opinion[i]/2, str(no_opinion[i]), ha="center", va="center", 
                   fontweight="bold", color="white", fontsize=9)
            y_offset += no_opinion[i]
        
        if disagree[i] > 0:
            ax.text(i, y_offset + disagree[i]/2, str(disagree[i]), ha="center", va="center", 
                   fontweight="bold", color="white", fontsize=9)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches="tight")
    plt.close()
    
def plot_polarity_consistency(json_path, save_path, category, subcategory):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = {
        "EN": [],
        "BG": []
    }

    def score(answer):
        answer_num = answer_to_number(answer)
        return answer_num  

    en_pos = list(data.get("en", {}).get("positive", {}).values())
    en_neg = list(data.get("en", {}).get("negative", {}).values())

    for pos, neg in zip(en_pos, en_neg):
        pos_score = score(pos)
        neg_score = score(neg)
        consistency = pos_score + neg_score
        results["EN"].append(consistency)

    bg_pos = list(data.get("bg", {}).get("positive", {}).values())
    bg_neg = list(data.get("bg", {}).get("negative", {}).values())

    for pos, neg in zip(bg_pos, bg_neg):
        pos_score = score(pos)
        neg_score = score(neg)
        consistency = pos_score + neg_score
        results["BG"].append(consistency)

    labels = list(data["bg"]["positive"].keys())

    y_pos = range(len(labels))

    fig, ax = plt.subplots(figsize=(12, 6))
    
    #######
    # plt.subplots_adjust(bottom=0.25)

#     description = (
#         "Описание:\n\n"
#         "Резултат = 0 → логически консистентен\n"
#         "Резултат = ±1 → не напълно консистентен\n"
#         "Резултат = ±2 → противоречие\n\n"
#         "Резултатът се смята по следния начин:\n"
#         "консистентност = позитивен резултат + негативен резултат.\n\n"
#         "Резултатът показва дали моделът отговаря\n"
#         "логически, когато се смени полярността на твърдението."
#     )

#     fig.text(
#     0.1, 0.2,                 
#     description,
#     fontsize=10,
#     va="top",
#     ha="center",
#     bbox=dict(facecolor="white", edgecolor="gray", boxstyle="round,pad=0.5")
# )
    ######

    ax.barh(
        [y - 0.2 for y in y_pos],
        results["EN"],
        height=0.4,
        label="Английски",
        color="#3498db"
    )

    ax.barh(
        [y + 0.2 for y in y_pos],
        results["BG"],
        height=0.4,
        label="Български",
        color="#9b59b6"
    )

    ax.axvline(0, color="black", linewidth=1)

    ax.set_xlim(-2.5, 2.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)

    ax.set_xlabel("Резултат на консистентност в полярността", fontweight="bold")
    ax.set_title(
        f"Консистентност на отговорите в двете полярности\nКатегория: {category}, Подкатегория: {subcategory}",
        fontweight="bold"
    )

    ax.legend()
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches="tight")
    plt.close()
    
# plot_language_differences('data/results/politics_gpt-5-nano_raw-results_2026-03-13.json', 'data/results/test2.png', 'politics', 'russia')
# plot_distribution_stacked('data/results/politics_gpt-5-nano_raw-results_2026-03-13.json', 'data/results/novo20.png', 'politics', 'russia')
#plot_polarity_consistency('data/results/politics_gpt-5-nano_raw-results_2026-03-13.json', 'data/results/novo30.png', 'politics', 'russia')
