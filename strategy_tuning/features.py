import pandas as pd
from datetime import datetime as dt
import numpy as np
import os
from numba import njit

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
data['volatility'] = data['log_return'].rolling(3*LOOKBACK).std() * np.sqrt(525600)

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

# indicators, emas, rsi, macd, stochastic, money flow, atr, adx, donchian channel, 
data[f'ema_{LOOKBACK}'] = data['ohlc'].ewm(span=LOOKBACK, min_periods=1, adjust=False).mean()
data[f'ema_{2*LOOKBACK}'] = data['ohlc'].ewm(span=2*LOOKBACK, min_periods=1, adjust=False).mean()
data[f'ema_{4*LOOKBACK}'] = data['ohlc'].ewm(span=4*LOOKBACK, min_periods=1, adjust=False).mean()
data[f'ema_{10*LOOKBACK}'] = data['ohlc'].ewm(span=10*LOOKBACK, min_periods=1, adjust=False).mean()

delta = data['ohlc'].diff()
gain = np.where(delta>0, delta, 0)
loss = np.where(delta<0, -delta, 0)
avg_gain = pd.Series(gain, index=data.index).rolling(window=14).mean()
avg_loss = pd.Series(loss, index=data.index).rolling(window=14).mean()
rs = avg_gain / avg_loss
data['rsi_14'] = 100 - (100 / (1 + rs))

ema_fast = data['close'].ewm(span=12, adjust=False).mean()
ema_slow = data['close'].ewm(span=26, adjust=False).mean()
data['macd'] = ema_fast - ema_slow
data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
data['macd_hist'] = data['macd'] - data['macd_signal']

low_14 = data['low'].rolling(14).min()
high_14 = data['high'].rolling(14).max()
data['stoch_k'] = 100 * (data['close'] - low_14) / (high_14 - low_14)
data['stoch_d'] = data['stoch_k'].rolling(3).mean()

raw_money_flow = data['ohlc'] * data['volume']
positive_flow = np.where(data['ohlc'] > data['ohlc'].shift(1), raw_money_flow, 0)
negative_flow = np.where(data['ohlc'] < data['ohlc'].shift(1), raw_money_flow, 0)
positive_mf = pd.Series(positive_flow, index=data.index).rolling(window=14).sum()
negative_mf = pd.Series(negative_flow, index=data.index).rolling(window=14).sum()
mf_ratio = positive_mf / negative_mf
data['mfi_14'] = 100 - (100 / (1 + mf_ratio))

high_low = data['high'] - data['low']
high_close = np.abs(data['high'] - data['close'].shift())
low_close = np.abs(data['low'] - data['close'].shift())
tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
data['atr_14'] = tr.rolling(window=14).mean()

plus_dm = data['high'].diff()
minus_dm = data['low'].diff()
plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)
plus_di = 100 * pd.Series(plus_dm, index=data.index).rolling(LOOKBACK).sum() / data['atr_14']
minus_di = 100 * pd.Series(minus_dm, index=data.index).rolling(LOOKBACK).sum() / data['atr_14']
dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
data['adx'] = dx.rolling(LOOKBACK).mean()

data['donchian_upper'] = data['high'].rolling(window=LOOKBACK).max()
data['donchian_lower'] = data['low'].rolling(window=LOOKBACK).min()
data['donchian_mid'] = (data['donchian_upper'] + data['donchian_lower']) / 2
data['donchian_width'] = data['donchian_upper'] - data['donchian_lower']

data.dropna(inplace=True)
print(data.tail(50))