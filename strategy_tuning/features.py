import pandas as pd
from datetime import datetime as dt
import numpy as np
import os

PAIR = "BTCUSDT"
LOOKBACK = 20

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

# volume metrics
data['taker_sell_q_volume'] = data['q_asset_volume'] - data['taker_buy_q_volume']
data['taker_sell_b_volume'] = data['volume'] - data['taker_buy_b_volume']

data['buy_ratio_q'] = data['taker_buy_q_volume'] / data['q_asset_volume']
data['sell_ratio_q'] = data['taker_sell_q_volume'] / data['q_asset_volume']
data['buy_pressure'] = data['taker_buy_q_volume'] - data['taker_sell_q_volume']
data[f'buy_ratio_q_sma_{LOOKBACK}'] = data['buy_ratio_q'].rolling(LOOKBACK).mean()
data[f'sell_ratio_q_sma_{LOOKBACK}'] = data['sell_ratio_q'].rolling(LOOKBACK).mean()
data[f'buy_pressure_sma_{LOOKBACK}'] = data['buy_pressure'].rolling(LOOKBACK).mean()

data['avg_trade_size'] = data['volume'] / data['n_trades']
data['avg_quote_per_trade'] = data['q_asset_volume'] / data['n_trades']

data[f'volume_spike_{LOOKBACK}'] = data['volume'] / data['volume'].rolling(LOOKBACK).mean()

data[f'vwap_{LOOKBACK}'] = (data['ohlc'] * data['volume']).rolling(20).sum() / data['volume'].rolling(20).sum()
data['vwap_distance'] = data['close'] - data[f'vwap_{LOOKBACK}']
data['vwap_distance_z'] = (data['vwap_distance'] - data['vwap_distance'].rolling(20).mean())/ data['vwap_distance'].rolling(20).std()

# indicators, rsi, macd, emas, stochastic, money flow, atr


print(data.tail(5))