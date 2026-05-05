import pandas as pd
from pathlib import Path

# Get the path to the data directory
# app/services/dataset.py -> app/services -> app -> project_root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = BASE_DIR / "app" / "static" / "data" / "earthquake_data_tsunami.csv"

# Load dataset
def load() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        # Return empty DataFrame if file doesn't exist
        return pd.DataFrame()
    return pd.read_csv(DATASET_PATH)

# Decompose dataset cleaning logic and call subprocedures inside clean()
def clean(dataset: pd.DataFrame) -> pd.DataFrame:

    # This drops any rows that are completely empty
    dataset = dataset.dropna(how="all")

    # This defines the columns that we want to convert to numeric types
    columns = ['magnitude', 'cdi', 'mmi', 'sig', 'nst', 'dmin', 'gap', 'depth', 'latitude', 'longitude', 'Year', 'Month', 'tsunami']

    # This converts the specified columns to numeric, converting errors to NaN
    for col in columns:
        if col in dataset.columns:
            dataset[col] = pd.to_numeric(dataset[col], errors='coerce')

    # This drops rows that have NaN values in the specified columns
    dataset = dataset.dropna(subset=['magnitude', 'Year', 'Month'])

    # This filters the dataset to include only rows where magnitude is between 0 and 10
    dataset = dataset[(dataset['magnitude'] >= 0) & (dataset['magnitude'] <= 10)]
    # This filters the dataset to include only rows where Year is between 1900 and 2024
    dataset = dataset[(dataset['Year'] >= 1900) & (dataset['Year'] <= 2024)]
    # This filters the dataset to include only rows where Month is between 1 and 12
    dataset = dataset[(dataset['Month'] >= 1) & (dataset['Month'] <= 12)]

    return dataset # change to cleaned_dataset

def load_cleaned() -> pd.DataFrame:
    return clean(load())

if __name__ == "__main__":
    dataset = load_cleaned()
    if not dataset.empty:
        print(dataset)
    else:
        print(f"Dataset not found at {DATASET_PATH}")
