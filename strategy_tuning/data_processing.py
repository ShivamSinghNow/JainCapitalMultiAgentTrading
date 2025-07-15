import pandas as pd
from datetime import datetime as dt
import numpy as np
import os

PAIR = "BTC/USDT"
file = os.path.join('data', f'{PAIR}.csv')
data = pd.read_csv(file, sep='|', header=None)

# setting columns, timestamp, and index
data.columns = [
                'open_ts', 'open', 'high', 'low', 'close', 'volume',
                'taker_buy_q_volume', 'taker_buy_b_volume', 'q_asset_volume', 'n_trades'
                ]

data['timestamp'] = pd.to_datetime(data['open_ts'], unit='s')
data.drop(['open_ts'], axis=1, inplace=True)
data.set_index('timestamp', inplace=True)

# using ohlc/4 for average price per ticker, calculating log return
data['ohlc'] = (data['open'] + data['close'] + data['low'] + data['high']) / 4
data['log_return'] = np.log(data['ohlc'] / data['ohlc'].shift(1))