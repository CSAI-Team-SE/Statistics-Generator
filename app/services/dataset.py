import pandas as pd
from pathlib import Path

# Get the path to the data directory
# app/services/dataset.py -> app/services -> app -> project_root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = BASE_DIR / "data" / "earthquake_data_tsunami.csv"

# Load dataset
def load() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        # Return empty DataFrame if file doesn't exist
        return pd.DataFrame()
    return pd.read_csv(DATASET_PATH)

# Decompose dataset cleaning logic and call subprocedures inside clean()
def clean(dataset: pd.DataFrame) -> pd.DataFrame:
    #
    #
    #
    #
    #
    #
    return dataset # change to cleaned_dataset

def load_cleaned() -> pd.DataFrame:
    return clean(load())

if __name__ == "__main__":
    dataset = load_cleaned()
    if not dataset.empty:
        print(dataset)
    else:
        print(f"Dataset not found at {DATASET_PATH}")
