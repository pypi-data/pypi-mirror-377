import pandas as pd

def load_hypertension_data():
    """
    Load the hypertension dataset from GitHub.
    Returns:
        pandas.DataFrame
    """
    url = "https://raw.githubusercontent.com/Perfect-Aimers-Enterprise/minforge/main/mindforge-ml/mindforge_ml/datasets/hypertensiondataset.csv"
    return pd.read_csv(url)
