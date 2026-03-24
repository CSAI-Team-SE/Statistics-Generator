import pandas as pd
from app.services.dataset import load_cleaned

# Decompose graph generation logic and call subprocedures inside generate()
def generate_image(dataset: pd.DataFrame): # -> base64 encoded image?
    return # graph

if __name__ == "__main__":
    dataset = load_cleaned()
    graph = generate_image(dataset)
