import pandas as pd
import numpy as np 
from env import TradingEnvironment
from agents import risk_agent as risk

class BaseStrategy:
    def __init__(self, env, backtester):
        self.trader = env # trading environment
        self.bt = backtester # backtester that created the strategy
        self.risk = risk.RiskAgent(1, self.trader) # risk agent to manage risk for the strategy

    
class GridStrategy(BaseStrategy):
    def __init__(self, env, bt):
        super().__init__(env, bt)

    def generate_signal(self, lookback_data):
        """
        Generates a signal based on the current state of the strategy
        Returns "buy" or "hold"
        """
        if any(t[0] == self for t in self.bt.active_strategies) and not any(o.strategy == self for o in self.trader.orders):
            return 'buy'
        else:
            return 'hold'
        

    def action(self, signal, lookback_data):
        """
        Executes the action based on the generated signal
        If the signal is "buy", it places limit orders at various price levels
        Else it does nothing
        """
        if signal == 'buy':
            high = lookback_data.close.max()
            low = lookback_data.close.min()
            spread = (high - low) / 10

            size = self.risk.get_size(lookback_data.iloc[-1])
            print(size)
            
            for t in range(1, 6):
                self.trader.limit_order('buy', lookback_data.iloc[-1]['close'] - t*spread, size, self)
                self.trader.limit_order('sell', lookback_data.iloc[-1]['close'] + t*spread, size, self)
        else:
            pass


class MeanReversionStrategy(BaseStrategy):
    def __init__(self, env, bt):
        super().__init__(env, bt)


    def generate_signal(self, data):
        # returns "buy", "sell", or "hold"
        ...


    def action(self, signal, lookback_data):
        """
        Executes the action based on the generated signal
        If the signal is "buy", it places a limit order below the current price
        If the signal is "sell", it places a limit order above the current price
        Else it does nothing
        """
        if signal == 'buy':
            size = self.risk.get_size(lookback_data.iloc[-1])
            self.trader.limit_order('buy', lookback_data.iloc[-1]['close'] * 0.99, size, self)
        elif signal == 'sell':
            size = self.risk.get_size(lookback_data.iloc[-1])
            self.trader.limit_order('sell', lookback_data.iloc[-1]['close'] * 1.01, size, self)
        else:
            pass

class MomentumStrategy(BaseStrategy):
    def __init__(self, env, bt):
        super().__init__(env, bt)


    def generate_signal(self, data):
        # returns "buy", "sell", or "hold"
        ...

    def action(self, signal, lookback_data):
        """
        Executes the action based on the generated signal
        If the signal is "buy", it places a limit order above the current price
        If the signal is "sell", it places a limit order below the current price
        Else it does nothing
        """
        if signal == 'buy':
            size = self.risk.get_size(lookback_data.iloc[-1])
            self.trader.limit_order('buy', lookback_data.iloc[-1]['close'] * 1.01, size, self)
        elif signal == 'sell':
            size = self.risk.get_size(lookback_data.iloc[-1])
            self.trader.limit_order('sell', lookback_data.iloc[-1]['close'] * 0.99, size, self)
        else:
            pass
        
