from env import TradingEnvironment
from agents import StrategySelector, RiskAgent
import pandas as pd

model=None

class Backtester:
    def __init__(self, data):
        self.data = data
        self.env = TradingEnvironment()
        self.selector = StrategySelector(model)
        self.active_strategies = []

    def run(self):
        for i in range(5, len(self.data)):
            row = self.data.iloc[i]

            action = self.selector.update(row[1:50])
            if self.selector.current_strategy not in self.active_strategies:
                self.active_strategies.append(self.selector.current_strategy)
            for order in self.env.orders:
                if order.strategy not in self.active_stratgies:
                    self.env.cancel_order(order)


