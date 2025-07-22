import os
import time
import zipfile
import requests
import pandas as pd
from datetime import timedelta, datetime as dt
from tqdm import tqdm

# Settings
script_dir = os.path.dirname(os.path.abspath(__file__))
data_root = os.path.join(script_dir)

symbol = 'BTCUSDT'
interval = '1s'
save_dir = os.path.join(data_root, "binance_1s_data")
csv_dir = os.path.join(save_dir, 'csvs')
feather_path = os.path.join(data_root, "btc_1s_dev.feather")
rate_limit = 0.6

# Creating directories
os.makedirs(save_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

# Determining start date
if os.path.exists(feather_path):
    existing_df = pd.read_feather(feather_path, columns=["open_time"])
    latest_timestamp = existing_df["open_time"].max()
    start_date = dt.fromtimestamp(latest_timestamp / 1000000).date() + timedelta(days=1)
    print(f'using existing data, starting from {start_date}')
else:
    start_date = dt.now().date() - timedelta(days=100)
    print(f'no existing data found, starting at {start_date}')

end_date = dt.now().date() - timedelta(days=1)

# Downloading new files
base_url = f'https://data.binance.vision/data/spot/daily/klines/{symbol}/{interval}/'

if start_date > end_date:
    print(f"no new dates, latest: {start_date - timedelta(days=1)}, end: {end_date}")
else:
    for date in tqdm(pd.date_range(start=start_date, end=end_date)):
        date_str = date.strftime('%Y-%m-%d')
        zip_filename = f'{symbol}-{interval}-{date_str}.zip'
        url = base_url + zip_filename
        zip_path = os.path.join(save_dir, zip_filename)

        if os.path.exists(zip_path):
            continue

        try:
            r = requests.get(url=url, timeout=10)
            if r.status_code == 200:
                with open(zip_path, 'wb') as f:
                    f.write(r.content)
                print(f'ddownloaded {zip_filename}')
            else:
                print(f'{date_str} not available, error: {r.status_code}')
        
        except Exception as e:
            print(f'Error fethcing {date_str}, error: {e}')

        time.sleep(rate_limit)

# Extracting data
new_rows = []

existing_dates = set()
if os.path.exists(feather_path):
    try:
        existing_df = pd.read_feather(feather_path)
        existing_df["date"] = pd.to_datetime(existing_df["open_time"], unit="us").dt.date
        existing_dates = set(existing_df["date"].unique())
    except Exception as e:
        print(f"error: {e}")
        existing_dates = set()

for filename in sorted(os.listdir(save_dir)):
    if filename.endswith('.zip'):
        zip_path = os.path.join(save_dir, filename)
        date_str = filename.replace(f"{symbol}-{interval}-", "").replace(".zip", "")
        try:
            date_obj = dt.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"⚠️ Skipping file with bad date format: {filename}")
            continue

        if date_obj in existing_dates:
            continue

        with zipfile.ZipFile(zip_path, 'r') as z:
            for name in z.namelist():
                z.extract(name, csv_dir)
                full_path = os.path.join(csv_dir, name)
                df = pd.read_csv(full_path, header=None)
                new_rows.append(df)

if new_rows:
    combined = pd.concat(new_rows)
    combined.columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ]
    combined.drop(columns=["ignore"], inplace=True)

    if os.path.exists(feather_path):
        existing_df.drop(columns=["date"], errors="ignore", inplace=True)
        final_df = pd.concat([existing_df, combined], ignore_index=True)
    else:
        final_df = combined
    
    final_df.reset_index(drop=True, inplace=True)
    final_df.to_feather(feather_path)
    print(f'appended {len(combined)} rows to {feather_path}')

else:
    print('no new rows')
