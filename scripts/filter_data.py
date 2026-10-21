import os
import pandas as pd

RAW_FOLDER = "data/raw"
OUT_FILE = "data/processed/filtered_prices.csv"

FILES = ["2024.csv", "2025.csv", "2026.csv"]
COMMODITIES = ["Onion", "Tomato", "Potato", "Rice", "Wheat"]
STATES = ["Kerala", "Tamil Nadu", "Karnataka", "Maharashtra", "Uttar Pradesh"]

os.makedirs("data/processed", exist_ok=True)

parts = []
for name in FILES:
    path = os.path.join(RAW_FOLDER, name)
    print("Reading", path, "...")
    for chunk in pd.read_csv(path, chunksize=500_000):
        chunk = chunk[chunk["Commodity"].isin(COMMODITIES) & chunk["State"].isin(STATES)]
        parts.append(chunk)

result = pd.concat(parts, ignore_index=True)
result.to_csv(OUT_FILE, index=False)

print("\nSaved to", OUT_FILE)
print("Total rows:", len(result))
print("\nRows per commodity:")
print(result["Commodity"].value_counts())
print("\nRows per state:")
print(result["State"].value_counts())
print("\nSample dates:", result["Arrival_Date"].head(5).tolist())