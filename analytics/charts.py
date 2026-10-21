import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("screenshots", exist_ok=True)
sns.set_theme(style="whitegrid")

weekly = pd.read_csv("data/processed/weekly_prices.csv", parse_dates=["week_start"])
flagged = weekly[weekly["status"].isin(["Alert", "Severe"])]


# Chart 1: price trend for one state and commodity, flagged weeks in red
def trend_chart(state, commodity):
    d = weekly[(weekly["state"] == state) & (weekly["commodity"] == commodity)]
    f = d[d["status"].isin(["Alert", "Severe"])]
    plt.figure(figsize=(11, 5))
    plt.plot(d["week_start"], d["avg_price"], color="steelblue", label="Weekly average price")
    plt.scatter(f["week_start"], f["avg_price"], color="red", zorder=3, label="Flagged spike")
    plt.title(f"{commodity} price trend in {state}")
    plt.xlabel("Week")
    plt.ylabel("Price (Rs per quintal)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"screenshots/trend_{state}_{commodity}.png", dpi=150)
    plt.close()


trend_chart("Kerala", "Tomato")
trend_chart("Karnataka", "Tomato")

# Chart 2: heatmap of how many spike weeks each state and commodity had
counts = flagged.groupby(["state", "commodity"]).size().unstack(fill_value=0)
counts = counts.reindex(index=sorted(weekly["state"].unique()),
                        columns=sorted(weekly["commodity"].unique()), fill_value=0)
plt.figure(figsize=(8, 5))
sns.heatmap(counts, annot=True, fmt="d", cmap="Reds")
plt.title("Number of price spike weeks (Jan 2024 to Apr 2026)")
plt.xlabel("Commodity")
plt.ylabel("State")
plt.tight_layout()
plt.savefig("screenshots/volatility_heatmap.png", dpi=150)
plt.close()

# Chart 3: spike weeks per month across all states and commodities
monthly = flagged.assign(month=flagged["week_start"].dt.to_period("M").astype(str))
monthly = monthly.groupby("month").size()
plt.figure(figsize=(12, 5))
plt.bar(monthly.index, monthly.values, color="indianred")
plt.xticks(rotation=90)
plt.title("When do price spikes happen? Flagged weeks per month")
plt.xlabel("Month")
plt.ylabel("Flagged state-commodity weeks")
plt.tight_layout()
plt.savefig("screenshots/spikes_per_month.png", dpi=150)
plt.close()

print("Saved 4 charts in the screenshots folder")