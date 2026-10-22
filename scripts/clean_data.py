import pandas as pd

IN_FILE = "data/processed/filtered_prices.csv"
OUT_ROWS = "data/processed/cleaned_prices.csv"
OUT_DAILY = "data/processed/daily_state_prices.csv"

df = pd.read_csv(IN_FILE)
print("Start rows:", len(df))

# tidy column names and text
df.columns = df.columns.str.strip().str.lower()
for col in ["state", "district", "market", "commodity", "variety", "grade"]:
    df[col] = df[col].astype(str).str.strip()

# fix types
df["arrival_date"] = pd.to_datetime(df["arrival_date"], errors="coerce")
for col in ["min_price", "max_price", "modal_price"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 1. missing values
n = len(df)
df = df.dropna(subset=["arrival_date", "min_price", "max_price", "modal_price"])
print("Dropped missing:", n - len(df))

# 2. duplicates
n = len(df)
df = df.drop_duplicates()
print("Dropped duplicates:", n - len(df))

# 3. impossible prices
n = len(df)
df = df[(df["min_price"] > 0) & (df["max_price"] > 0) & (df["modal_price"] > 0)]
df = df[df["min_price"] <= df["max_price"]]
df = df[(df["modal_price"] >= df["min_price"]) & (df["modal_price"] <= df["max_price"])]
print("Dropped impossible prices:", n - len(df))

df = df.drop(columns=["commodity_code"], errors="ignore")
df = df.sort_values(["state", "commodity", "arrival_date"])
df.to_csv(OUT_ROWS, index=False)
print("Clean rows:", len(df))

# daily summary: one row per state, commodity, date (median is safer than average)
daily = (
    df.groupby(["state", "commodity", "arrival_date"])
      .agg(modal_price=("modal_price", "median"),
           min_price=("min_price", "median"),
           max_price=("max_price", "median"),
           num_records=("modal_price", "count"))
      .reset_index()
)
daily.to_csv(OUT_DAILY, index=False)

print("\nDaily summary rows:", len(daily))
print("Date range:", daily["arrival_date"].min().date(), "to", daily["arrival_date"].max().date())
print("\nDays of data per state and commodity:")
print(daily.groupby(["state", "commodity"]).size().unstack(fill_value=0))