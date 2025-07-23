import pandas as pd
import numpy as np 
from env import TradingEnvironment
from agents import risk_agent as risk

class BaseStrategy:
    def __init__(self):
        self.current_signal = None
        self.risk = risk.RiskAgent()
        self.trader = TradingEnvironment()
    
class GridStrategy(BaseStrategy):
    def generate_signal(self, lookback_data):
        high = lookback_data.close.max()
        low = lookback_data.close.min()
        spread = (high - low) / 10

        size = self.risk.get_size()
        
        for t in range(1, 6):
            self.trader.limit_order('buy', lookback_data.iloc[-1]['close'] - t*spread, size, 'grid')
            self.trader.limit_order('sell', lookback_data.iloc[-1]['close'] + t*spread, size, 'grid')


class MeanReversionStrategy(BaseStrategy):
    def generate_signal(self, data):
        # returns "buy", "sell", or "hold"
        ...

class MomentumStrategy(BaseStrategy):
    def generate_signal(self, data):
        # returns "buy", "sell", or "hold"
        ...
