import os 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# class for backtesting strategy on given pair
class Backtester:
    def _load_data(self):
        """
        Loads in raw csv data from cryptoarchive
        """
        file = os.path.join('data', f'{self.pair}.csv')

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

        return data


    def __init__(self, pair):
        """
        Initializes the class
        """
        self.pair = pair
        self.data = self._load_data()


    def signals(self):
        """
        Creates signals for strategy
        Uses simple momentum based strategy
        """
        # calculating smas
        self.data['sma_200'] = self.data['ohlc'].rolling(200).mean()
        self.data['sma_50'] = self.data['ohlc'].rolling(50).mean()

        # calculting position based on smas
        self.data['position'] = np.where(self.data['sma_50'] >= self.data['sma_200'], 1, 0)
        self.data['position'] = self.data['position'].shift(1)

        self.data.dropna(inplace=True)


    def stop_loss(self):
        """
        Creates stop loss and take profit for each trade
        """
        # setting risk-reward ratio, stop loss, and take profit
        rr = 2
        sl_tp = 0.04
        stop_loss = 1 - sl_tp
        take_profit = 1 + rr * sl_tp

        # creating trade entry indicators
        self.data['entry'] = (self.data['position'] != self.data['position'].shift(1)) & (self.data['position'] == 1)
        self.data['entry_price'] = np.where(self.data['entry'], self.data['ohlc'], np.nan)
        self.data['entry_price'] = self.data['entry_price'].ffill()

        # creating take profit indicator
        self.data['take_profit'] = take_profit * self.data['entry_price']
        self.data['take_profit_triggered'] = (self.data['position'] == 1) & (self.data['ohlc'] > self.data['take_profit'])

        # creating stop loss indicator
        self.data['stop_loss'] = stop_loss * self.data['entry_price']
        self.data['stop_loss_triggered'] = (self.data['position'] == 1) & (self.data['ohlc'] < self.data['stop_loss'])

        self.data.dropna(inplace=True)

        # creating series to loop faster
        position = self.data['position'].values.copy()
        take_triggered = self.data['take_profit_triggered'].values
        stop_triggered = self.data['stop_loss_triggered'].values
        entry = self.data['entry'].values

        # looping through series and ending trades when sl/tp are triggered
        cooldown = False
        for i in range(1, len(position)):
            if cooldown:
                position[i] = 0
                if entry[i]:
                    cooldown = False
            elif stop_triggered[i] or take_triggered[i]:
                position[i+1] = 0
                cooldown = True

        # setting new position values
        self.data['position'] = position


    def calculate_returns(self):
        """
        Calculates return metrics
        """
        self.data['strat_return'] = self.data['position'] * self.data['log_return']
        self.data['cumulative_strat_log_return'] = self.data['strat_return'].cumsum()
        self.data['cumulative_buy_hold_log_return'] = self.data['log_return'].cumsum()


    def display_metrics(self):
        """
        Calculates relevant metrics to stratgy
        """
        # isolating strategy returns
        r = self.data['strat_return']

        # calcualting sharpe ratio
        sharpe_ratio = (r.mean() / r.std()) * np.sqrt(252 * 24 * 60)

        # calculating profit factor
        gross_profit = r[r > 0].sum()
        gross_loss = -r[r < 0].sum()
        profit_factor = gross_profit / gross_loss

        # calculating hit rate
        num_wins = (r > 0).sum()
        num_trades = (r != 0).sum()
        hit_rate = hit_rate = num_wins / num_trades

        # calculating max drawdown
        cum_return = np.exp(r.cumsum())
        running_max = cum_return.cummax()
        drawdown = cum_return / running_max - 1
        max_drawdown = drawdown.min()

        # calculating information coefficient
        signal = self.data['position']
        future_return = self.data['log_return'].rolling(5).sum().shift(-5)
        ic = signal.corr(future_return)

        # displaying
        print(self.data[['ohlc', 'position', 'strat_return', 'cumulative_strat_log_return', 'cumulative_buy_hold_log_return']])
        print(f'Sharpe Ratio: {sharpe_ratio:.3f}')
        print(f'Profit Factor: {profit_factor:.3f}')
        print(f'Hit Rate: {hit_rate:.3f}')
        print(f"Max Drawdown: {max_drawdown:.3%}")
        print(f"Information Coefficient: {ic:.3f}")



    def plot_returns(self):
        """
        Plots buy/hold versus strategy
        """
        plt.figure(figsize=(12, 6))
        plt.plot(self.data.index, self.data['cumulative_strat_log_return'], label='Strategy Return')
        plt.plot(self.data.index, self.data['cumulative_buy_hold_log_return'], label='Buy & Hold')

        plt.title('Strategy vs Buy-and-Hold Cumulative Returns')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    
    def backtest(self):
        """
        Running all functions to backtest
        """
        self.signals()
        self.stop_loss()
        self.calculate_returns()

        self.display_metrics()
        self.plot_returns()


# Entry point
if __name__ == '__main__':
    pair = 'BTCUSDT'

    btc = Backtester(pair)
    btc.backtest()
