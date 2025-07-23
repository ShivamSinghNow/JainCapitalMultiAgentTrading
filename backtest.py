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
        self.data = data
        self.env = TradingEnvironment()
        self.selector = StrategySelector(model, pca, scaler, state_map)
        self.active_strategies = []

    def run(self):
        for i in range(60, len(self.data)):
            print(self.active_strategies)
            row = self.data.iloc[i]
            lookback_data = self.data.iloc[i-60:i]

            action = self.selector.update(row, lookback_data)

            if self.selector.current_strategy not in self.active_strategies:
                self.active_strategies.append((self.selector.current_strategy, i))

            for s in self.active_strategies:
                if i - s[1] >= 100:
                    self.active_strategies.remove(s)

            for order in self.env.orders:
                if order.strategy not in self.active_stratgies:
                    self.env.cancel_order(order)


if __name__ == '__main__':
    bt = Backtester(pd.read_feather('data/btc_test.feather'))

    bt.run()