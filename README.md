# Food Price Anomaly Detection and Early Warning System for Regional Food Security

**Group B7** | End-semester Python project | **SDG 2: Zero Hunger**

## What it does

A sudden rise in the price of a staple food is an early sign that low-income households in that region may struggle to afford food. This project takes daily wholesale (mandi) prices from Agmarknet, the government's market price system, and does four things:

1. Cleans the price records and stores them in a MySQL database.
2. Converts them into weekly average prices for each state and commodity.
3. Flags weeks where the price rose sharply compared with the previous week: **Alert** for a rise of 15% or more, **Severe** for 25% or more.
4. Shows the results in an interactive Streamlit dashboard.

The threshold rule is plain arithmetic, so no machine learning is used.

## Data

- **Source:** Kaggle dataset [Daily Market Prices of Commodity India (2001-2026)](https://www.kaggle.com/datasets/khandelwalmanas/daily-commodity-prices-india), a mirror of the Agmarknet data published on data.gov.in.
- **Scope used:** onion, tomato, potato, rice and wheat in Kerala, Tamil Nadu, Karnataka, Maharashtra and Uttar Pradesh, from January 2024 to 20 April 2026.
- **Unit:** prices are in Rs per quintal (1 quintal = 100 kg).
- The raw data (about 8 GB) is not included in this repository.

## Results

| Stage | Number |
|---|---|
| Records after filtering | 927,614 |
| Duplicates removed | 177 |
| Impossible prices removed | 378 |
| Clean records | 927,059 |
| Daily rows (one per state, commodity, day) | 16,440 |
| Weekly rows analysed | 2,452 |
| Flagged weeks | 132 (71 Alert, 61 Severe) |

- Tomato is the most volatile commodity. Karnataka (25 spike weeks) and Maharashtra (18) have the most spikes.
- Spikes cluster in certain months, such as June and September 2024, June 2025 and December 2025.
- In the latest week of data, tomato prices were Severe in Kerala, Tamil Nadu, Karnataka and Maharashtra at the same time.

## Data quality issues found

- **Unit error:** nine Tamil Nadu weeks (17 June to 1 July 2024) have onion, potato and tomato prices recorded per kg instead of per quintal. They looked like spikes of over 10,000%. The pipeline removes any week whose price is below 20% or above 5 times the median for that state and commodity.
- **Missing combinations:** Kerala and Tamil Nadu do not report wheat, and Tamil Nadu does not report rice.
- **Spelling variants:** the source data contains inconsistent state names (for example Chattisgarh, Uttrakhand).

## Project structure

```
B7/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                     (Kaggle files, not in the repository)
│   └── processed/
│       ├── daily_state_prices.csv
│       ├── weekly_prices.csv
│       └── alerts.csv
├── scripts/
│   ├── explore.py               look at the raw files
│   ├── check_values.py          list state and commodity names
│   ├── filter_data.py           keep our states, commodities and dates
│   └── clean_data.py            clean and build the daily summary
├── database/
│   ├── schema.sql               MySQL table
│   ├── load_to_mysql.py         insert the daily rows
│   └── config_example.py        template for config.py
├── analytics/
│   ├── anomaly_detection.py     weekly averages and spike flags
│   └── charts.py                matplotlib and seaborn charts
├── app/
│   └── dashboard.py             Streamlit dashboard
├── report/
└── screenshots/
```

## Setup

1. Install Python 3.10 or newer.
2. Install the packages:

```
pip install -r requirements.txt
```

## Run the dashboard only

The repository includes the processed weekly file, so the dashboard runs without MySQL or the raw data. From the project folder:

```
python -m streamlit run app/dashboard.py
```

It opens in your browser at http://localhost:8501.

## Rebuild everything from the raw data

You need the raw Kaggle files in data/raw/ and MySQL installed. Copy database/config_example.py to database/config.py and enter your MySQL password. Then run these from the project folder, in order:

```
python scripts/filter_data.py
python scripts/clean_data.py
python database/load_to_mysql.py
python analytics/anomaly_detection.py
python analytics/charts.py
python -m streamlit run app/dashboard.py
```

| Step | Script | Output |
|---|---|---|
| 1 | filter_data.py | Keeps only our states, commodities and dates |
| 2 | clean_data.py | Removes duplicates and impossible prices, builds daily_state_prices.csv |
| 3 | load_to_mysql.py | Creates the database and loads the daily rows (safe to rerun) |
| 4 | anomaly_detection.py | Reads MySQL, writes weekly_prices.csv and alerts.csv |
| 5 | charts.py | Saves charts to the screenshots folder |
| 6 | dashboard.py | Interactive dashboard |

## How the detection works

1. Take the median modal price for each state, commodity and day.
2. Average it by week (Monday to Sunday). Weeks with fewer than 3 days of data are ignored.
3. Remove weeks with unit errors (see above).
4. Calculate the percentage change from the previous week.
5. Flag: 15% or more is an Alert, 25% or more is Severe. Only rises are flagged, because rising food prices are what threaten food security.

## Dashboard

Five tabs: current status of every state and commodity, price trend with flagged weeks, alert history, a regional risk heatmap with spikes per month, and an explanation of the method. Filters for state, commodity and date range are in the sidebar.

## Limitations

- The weekly rule catches sudden jumps but can miss slow, steady climbs.
- The data ends on 20 April 2026, and the system does not update itself.
- Prices are wholesale mandi prices, not retail prices paid by consumers.
- The 15% and 25% thresholds are fixed rules, not tuned values.

## Tech stack

Python, Pandas, NumPy, MySQL (mysql-connector-python), Matplotlib, Seaborn, Streamlit.
