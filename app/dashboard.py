import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Food Price Early Warning", layout="wide")


@st.cache_data
def load():
    return pd.read_csv("data/processed/weekly_prices.csv", parse_dates=["week_start"])


weekly = load()
FLAG = ["Alert", "Severe"]

st.title("Food Price Anomaly Detection and Early Warning System")
st.caption("SDG 2: Zero Hunger | Data: Agmarknet mandi prices via data.gov.in | Group B7")

# ---------- sidebar filters ----------
st.sidebar.header("Filters")
states = sorted(weekly["state"].unique())
commodities = sorted(weekly["commodity"].unique())
state = st.sidebar.selectbox("State", states, index=states.index("Kerala"))
commodity = st.sidebar.selectbox("Commodity", commodities, index=commodities.index("Tomato"))

min_d = weekly["week_start"].min().date()
max_d = weekly["week_start"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start, end = pd.to_datetime(min_d), pd.to_datetime(max_d)

in_range = weekly[(weekly["week_start"] >= start) & (weekly["week_start"] <= end)]

# latest week available for every state and commodity
latest = weekly.sort_values("week_start").groupby(["state", "commodity"]).tail(1)

# ---------- headline numbers ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Series tracked", len(latest))
c2.metric("Active alerts (latest week)", int(latest["status"].isin(FLAG).sum()))
c3.metric("Severe alerts (latest week)", int((latest["status"] == "Severe").sum()))
c4.metric("Flagged weeks in selected dates", int(in_range["status"].isin(FLAG).sum()))

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Current status", "Price trend", "Alert history", "Regional risk", "How it works"]
)

# ---------- tab 1: current status ----------
with tab1:
    st.subheader("Latest week for every state and commodity")
    show = latest[["state", "commodity", "week_start", "avg_price", "pct_change", "status"]]
    show = show.sort_values("pct_change", ascending=False)
    show = show.assign(week_start=show["week_start"].dt.date)

    def colour(row):
        c = {"Severe": "#f8b4b4", "Alert": "#fde1a8",
             "Normal": "#d4f0d4", "No data": "#e5e5e5"}[row["status"]]
        return [f"background-color: {c}"] * len(row)

    st.dataframe(show.style.apply(colour, axis=1), hide_index=True)

# ---------- tab 2: price trend ----------
with tab2:
    d = in_range[(in_range["state"] == state) & (in_range["commodity"] == commodity)]
    if d.empty:
        st.warning(f"No data for {commodity} in {state}. This state does not report it in the dataset.")
    else:
        f = d[d["status"].isin(FLAG)]
        fig, ax = plt.subplots(figsize=(11, 4.5))
        ax.plot(d["week_start"], d["avg_price"], color="steelblue", label="Weekly average price")
        ax.scatter(f["week_start"], f["avg_price"], color="red", zorder=3, label="Flagged spike")
        ax.set_title(f"{commodity} price trend in {state}")
        ax.set_ylabel("Price (Rs per quintal)")
        ax.legend()
        st.pyplot(fig)
        st.write(f"{len(f)} flagged weeks in this period.")

# ---------- tab 3: alert history ----------
with tab3:
    st.subheader(f"Flagged weeks for {commodity}, all states")
    a = in_range[(in_range["commodity"] == commodity) & in_range["status"].isin(FLAG)]
    a = a.sort_values("pct_change", ascending=False)
    a = a[["state", "week_start", "prev_price", "avg_price", "pct_change", "status"]]
    a = a.assign(week_start=a["week_start"].dt.date)
    if a.empty:
        st.info("No flagged weeks for this commodity in the selected dates.")
    else:
        st.dataframe(a, hide_index=True)

# ---------- tab 4: regional risk ----------
with tab4:
    fl = in_range[in_range["status"].isin(FLAG)]
    if fl.empty:
        st.info("No flagged weeks in the selected dates.")
    else:
        st.subheader("Spike weeks by state and commodity")
        counts = fl.groupby(["state", "commodity"]).size().unstack(fill_value=0)
        counts = counts.reindex(index=states, columns=commodities, fill_value=0)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.heatmap(counts, annot=True, fmt="d", cmap="Reds", ax=ax)
        st.pyplot(fig)

        st.subheader("Spike weeks per month")
        monthly = fl.assign(month=fl["week_start"].dt.to_period("M").astype(str))
        st.bar_chart(monthly.groupby("month").size())

# ---------- tab 5: how it works ----------
with tab5:
    st.markdown("""
**Data:** daily wholesale (mandi) prices from Agmarknet, published on data.gov.in. Five staples
(onion, tomato, potato, rice, wheat) in five states, January 2024 onwards.

**Method:**
1. Clean the records (remove duplicates and impossible prices).
2. Take the median daily price per state and commodity, then the weekly average.
3. Compare each week with the previous week.
4. Flag a week as **Alert** if the price rose 15% or more, and **Severe** if it rose 25% or more.

**Why this matters for food security:** food is a large share of spending for low-income
households, so a sudden rise in a staple's price is an early sign that people in that region
may struggle to afford food.

**Limitations:** the rule catches sudden jumps but can miss slow, steady climbs.
Weeks with fewer than 3 days of data are ignored, and a few weeks with unit errors in the
source data were removed.
""")