import pandas as pd

def load_category(dataset_path, category):
    df = pd.read_csv(dataset_path)
    return df[df["category"] == category]

def load_categories_list(dataset_path):
    df = pd.read_csv(dataset_path)
    return df["category"].dropna().unique().tolist()