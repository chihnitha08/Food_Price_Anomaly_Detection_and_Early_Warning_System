import sys
import pandas as pd
import mysql.connector

sys.path.append("database")
import config

THRESHOLD = 15   # % rise over previous week that counts as an Alert
SEVERE = 25      # % rise that counts as Severe
MIN_DAYS = 3     # a week needs at least this many days of data

# 1. read from MySQL using a cursor
conn = mysql.connector.connect(host=config.DB_HOST, user=config.DB_USER,
                               password=config.DB_PASSWORD, database=config.DB_NAME)
cursor = conn.cursor()
cursor.execute("SELECT state, commodity, price_date, modal_price FROM daily_prices")
df = pd.DataFrame(cursor.fetchall(), columns=["state", "commodity", "price_date", "modal_price"])
cursor.close()
conn.close()

df["price_date"] = pd.to_datetime(df["price_date"])
df["modal_price"] = df["modal_price"].astype(float)

# 2. weekly average per state and commodity (weeks start on Monday)
df["week_start"] = df["price_date"].dt.to_period("W-SUN").dt.start_time
weekly = (
    df.groupby(["state", "commodity", "week_start"])
      .agg(avg_price=("modal_price", "mean"), days=("modal_price", "count"))
      .reset_index()
)
weekly = weekly[weekly["days"] >= MIN_DAYS]

# 3. drop weeks with unit errors (e.g. price per kg mixed with price per quintal)
median = weekly.groupby(["state", "commodity"])["avg_price"].transform("median")
bad = (weekly["avg_price"] < median * 0.2) | (weekly["avg_price"] > median * 5)
print("Dropped suspicious weeks (likely unit errors):", int(bad.sum()))
print(weekly[bad][["state", "commodity", "week_start", "avg_price"]].to_string(index=False))
weekly = weekly[~bad]

# 4. week-over-week % change (only between consecutive weeks)
weekly = weekly.sort_values(["state", "commodity", "week_start"])
grp = weekly.groupby(["state", "commodity"])
weekly["prev_price"] = grp["avg_price"].shift(1)
weekly["prev_week"] = grp["week_start"].shift(1)
weekly["pct_change"] = (weekly["avg_price"] - weekly["prev_price"]) / weekly["prev_price"] * 100
gap_days = (weekly["week_start"] - weekly["prev_week"]).dt.days
weekly.loc[gap_days != 7, "pct_change"] = None

# 5. flag spikes
def level(p):
    if pd.isna(p):
        return "No data"
    if p >= SEVERE:
        return "Severe"
    if p >= THRESHOLD:
        return "Alert"
    return "Normal"

weekly["status"] = weekly["pct_change"].apply(level)
weekly = weekly.drop(columns=["prev_week"])
num_cols = ["avg_price", "prev_price", "pct_change"]
weekly[num_cols] = weekly[num_cols].round(2)

weekly.to_csv("data/processed/weekly_prices.csv", index=False)
alerts = weekly[weekly["status"].isin(["Alert", "Severe"])]
alerts.to_csv("data/processed/alerts.csv", index=False)

# 6. summary
cols = ["state", "commodity", "week_start", "prev_price", "avg_price", "pct_change"]
print("\nWeekly rows:", len(weekly))
print("\nStatus counts:")
print(weekly["status"].value_counts())
print("\nTop 10 biggest weekly spikes:")
print(alerts.sort_values("pct_change", ascending=False).head(10)[cols].to_string(index=False))