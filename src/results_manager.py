from collections import Counter
import json
from datetime import datetime
from config import RESULTS_DIR

def save_results(results, category, model):
    pos_en_counts = Counter(results["positive"]["en"])
    pos_bg_counts = Counter(results["positive"]["bg"])
    
    neg_en_counts = Counter(results["negative"]["en"])
    neg_bg_counts = Counter(results["negative"]["bg"])
    

    results_final = {
        "category": category,
        "positive":{
            "en": pos_en_counts,
            "bg": pos_bg_counts
        },
        "negative":{
            "en": neg_en_counts,
            "bg": neg_bg_counts
        }
        
    }

    file_path = "%s/%s_%s_results_%s.json" % (RESULTS_DIR, category, model, str(datetime.today().strftime('%Y-%m-%d')))


    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results_final, f, ensure_ascii=False, indent=4)
        
def save_results_raw(resultsRaw, category, model):
    file_path = "%s/%s_%s_raw-results_%s.json" % (RESULTS_DIR, category, model, str(datetime.today().strftime('%Y-%m-%d')))
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(resultsRaw, f, ensure_ascii=False, indent=4)