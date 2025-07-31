from env import TradingEnvironment
from agents.strat_agent import StrategySelector
import pandas as pd
import joblib as jl

bundle = jl.load('agents/models/regime_hmm_scaler.pkl')
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
        for i in range(60, 1001):
            row = self.data.iloc[i]

            signals = self.selector.update(i, row.drop(['regime']))
            for strat, signal in signals:
                print(f"Strategy: {strat.__class__.__name__}, Signal: {signal}")
                strat.action(signal, row)

            self.env.update_orders(row['close'])

            if i % 200 == 0:
                print('\n--------------------------------------------')
                print(self.active_strategies)
                print(f'\nTick: {i}\nClose: {row["close"]}\n')
                print(f'Orders: {len(self.env.orders)}\nCash: {self.env.cash}\nInventory: {self.env.inventory}\nTotal Value: {self.env.cash + self.env.inventory * row["close"]}')
                print('--------------------------------------------')


if __name__ == '__main__':
    data = pd.read_feather('data/btc_test.feather')
    data['regime'] = 'low_vol'  # Default regime
    
    bt = Backtester(data)
    bt.run()
