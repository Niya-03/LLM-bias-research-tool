import pandas as pd
import os

def get_datasets():
    files = os.listdir("data/datasets")
    datasets = [os.path.splitext(f)[0] for f in files if f.endswith(".csv")]
    return datasets

def load_categories_list(dataset_path):
    df = pd.read_csv(dataset_path)
    return df["category"].dropna().unique().tolist()

def load_subcategories_list(dataset_path, category):
    df = pd.read_csv(dataset_path)
    return df[df["category"] == category]["subcategory"].dropna().unique().tolist()

