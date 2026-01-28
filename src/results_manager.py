from collections import Counter
import json
from datetime import datetime
from config import RESULTS_DIR

def save_results(results, category, model):
    en_counts = Counter(results["en"])
    bg_counts = Counter(results["bg"])

    results_final = {
        "category": category,
        "counts" : {
            "en": en_counts,
            "bg": bg_counts
        }
    }

    file_path = "%s/%s_%s_results_%s.json" % (RESULTS_DIR, category, model, str(datetime.today().strftime('%Y-%m-%d')))


    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results_final, f, ensure_ascii=False, indent=4)