from env import TradingEnvironment
from agents.strat_agent import StrategySelector
import pandas as pd
import joblib as jl

bundle = jl.load('agents/regime_hmm_scaler.pkl')
model = bundle['model']
scaler = bundle['scaler']
pca = bundle['pca']
state_map = bundle['map']

class Backtester:
    def __init__(self, data):
        self.data = data # historical data to be used for backtesting
        self.env = TradingEnvironment(self) # trading environment to keep track of trades and balances
        self.selector = StrategySelector(model, pca, scaler, state_map, self.env, self) # strategy selector to choose strategies based on market regime
        self.active_strategies = [] # list of active strategies to be used in the backtest


    def run(self):
        """
        Runs the backtest by iterating through the data and executing strategies
        """
        for i in range(60, 6001):
            row = self.data.iloc[i].drop(['regime'])
            lookback_data = self.data.iloc[i-60:i]

            signals = self.selector.update(i, row)
            for strat, signal in signals:
                print(f"Strategy: {strat.__class__.__name__}, Signal: {signal}")
                strat.action(signal, lookback_data)

            self.env.update_orders(row['close'])

            print(self.active_strategies)
            print(len(self.env.orders))
            print(self.env.trade_log)
            print(f"Cash: {self.env.cash}, Inventory: {self.env.inventory}, Total Value: {self.env.cash + self.env.inventory * row['close']}")


if __name__ == '__main__':
    data = pd.read_feather('data/btc_test.feather')
    data['regime'] = 'low_vol'  # Default regime

    bt = Backtester(data)
    bt.run()
