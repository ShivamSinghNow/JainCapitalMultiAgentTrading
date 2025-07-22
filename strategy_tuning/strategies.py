import pandas as pd
import numpy as np 
from strategy_tuning import LOOKBACK

class BaseStrategy:
    def generate_signal(self, data):
        raise NotImplementedError
    
    def get_action(self, env, data_row):
        raise NotImplementedError
    
class GridStrategy(BaseStrategy):
    def generate_signal(self, data):
        # returns "buy", "sell", or "hold"
        ...

class BreakoutStrategy(BaseStrategy):
    def generate_signal(self, data):
        # returns "buy", "sell", or "hold"
        ...

class MeanReversionStrategy(BaseStrategy):
    def generate_signal(self, data):
        # returns "buy", "sell", or "hold"
        ...

class MomentumStrategy(BaseStrategy):
    def generate_signal(self, data):
        # returns "buy", "sell", or "hold"
        ...
