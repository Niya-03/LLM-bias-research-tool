import pandas as pd

def load_filtered(dataset_path, category, subcategory):
    df = pd.read_csv(dataset_path)
    category_filtered =  df[df["category"] == category]
    return category_filtered[category_filtered["subcategory"] == subcategory]
    

def load_categories_list(dataset_path):
    df = pd.read_csv(dataset_path)
    return df["category"].dropna().unique().tolist()

def load_subcategories_list(dataset_path, category):
    df = pd.read_csv(dataset_path)
    filtered = df[df["category"] == category]
    return filtered["subcategory"].dropna().unique().tolist()