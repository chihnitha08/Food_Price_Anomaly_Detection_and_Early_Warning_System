import os
import pandas as pd

DATA_FOLDER = "data/raw"

# list every file and its size
for root, dirs, files in os.walk(DATA_FOLDER):
    for f in files:
        path = os.path.join(root, f)
        print(path, round(os.path.getsize(path) / 1e6, 1), "MB")

# peek at the first csv you find
for root, dirs, files in os.walk(DATA_FOLDER):
    for f in files:
        if f.endswith(".csv"):
            df = pd.read_csv(os.path.join(root, f), nrows=5)
            print("\nFile:", f)
            print(df.columns.tolist())
            print(df.head())
            raise SystemExit
print("No csv found, check the file list above")