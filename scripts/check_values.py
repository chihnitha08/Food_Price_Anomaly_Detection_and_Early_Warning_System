import pandas as pd
from collections import Counter

FILE = "data/raw/2025.csv"

all_india = Counter()
kerala = Counter()
states = set()

for chunk in pd.read_csv(FILE, chunksize=500_000, usecols=["State", "Commodity"]):
    states.update(chunk["State"].dropna().unique())
    all_india.update(chunk["Commodity"].value_counts().to_dict())
    kerala.update(chunk[chunk["State"] == "Kerala"]["Commodity"].value_counts().to_dict())

print("STATES:", sorted(states))

print("\nTOP 40 COMMODITIES, ALL INDIA:")
for name, n in all_india.most_common(40):
    print(name, n)

print("\nTOP 25 COMMODITIES IN KERALA:")
for name, n in kerala.most_common(25):
    print(name, n)