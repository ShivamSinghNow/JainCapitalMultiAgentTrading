import pandas as pd
import numpy as np
import joblib as jl
from env import TradingEnvironment
from agents import risk_agent as risk

class BaseStrategy:
    def __init__(self, env, backtester):
        self.trader = env # trading environment
        self.bt = backtester # backtester that created the strategy
        self.risk = risk.RiskAgent(self.trader) # risk agent to manage risk for the strategy

    
class GridStrategy(BaseStrategy):
    def __init__(self, env, bt):
        super().__init__(env, bt)

    def generate_signal(self, row):
        """
        Generates a signal based on the current state of the strategy
        Returns "buy" or "hold"
        """
        if any(t[0] == self for t in self.bt.active_strategies) and not any(o.strategy == self for o in self.trader.orders):
            return 'buy'
        else:
            return 'hold'
        

    def action(self, signal, row):
        """
        Executes the action based on the generated signal
        If the signal is "buy", it places limit orders at various price levels
        Else it does nothing
        """
        i = self.bt.data.index.get_loc(row.name)
        lookback_data = self.bt.data.iloc[i-59:i+1]

        if signal == 'buy':
            high = lookback_data.close.max()
            low = lookback_data.close.min()
            spread = (high - low) / 20

            size = self.risk.get_size(row)
            
            for t in range(1, 11):
                self.trader.limit_order('buy', row['close'] - t*spread, size, self)
                self.trader.limit_order('sell', row['close'] + t*spread, size, self)
        else:
            pass


class MomentumStrategy(BaseStrategy):
    def __init__(self, env, bt):
        super().__init__(env, bt) 
        self.bought = False  # flag to track if a position has been bought
        self.exits = None  # list to keep track of exit signals
        self.max_price = None  # maximum price reached since entry
        self.buy_size = None
        self.model = jl.load('./agents/models/momentum_exit_model.pkl')  # load the trained model


    def generate_signal(self, row): 
        """
        Generates a signal based on the current state of the strategy
        Returns "buy" or "hold"
        """
        if self.bought:
            self.exits = self.get_exits(row)

        if self.exits:
            return 'sell'

        score = 0
        score = (row['macd_hist'] > 0).astype(int) + \
                (row['qema_d1'] > 0).astype(int) + \
                (row['qema_d2'] > 0).astype(int) + \
                (row['close'] > row['donchian_upper']).astype(int) + \
                (row['ema_60'] > row['ema_240'] and row['close'] > row['ema_60']).astype(int)
        
        if score >= 3 and not self.bought:
            return 'buy'
        else:
            return 'hold'
        

    def get_exits(self, row):
        """
        Generates exit signals based on the row data
        Returns a list of exit prices
        """
        if row['close'] > self.max_price:
            self.max_price = row['close']

        momentum_reversal = row['ema_240'] > row['ema_60']
        trailing_stop = row['close'] < (self.max_price - 5 * row['atr_14'])

        
        features = row[['close', 'ema_60', 'ema_240', 'atr_14',
                'rsi_14', 'macd_hist', 'volatility', 'adx',
                'donchian_lower', 'donchian_width', 'stoch_d',
                'stoch_k', 'mfi_14', 'buy_pressure',
                'vwap_distance_z', 'qema', 'qema_d1', 'qema_d2']]
        X = features.astype(float).values.reshape(1, -1)
        expected_return = self.model.predict(X)[0]

        exits = (
            momentum_reversal 
            or trailing_stop
            or expected_return < 0
        )

        return exits


    def action(self, signal, row):
        """
        Executes the action based on the generated signal
        If the signal is "buy", it places a limit order above the current price
        If the signal is "sell", it places a limit order below the current price
        Else it does nothing
        """
        if signal == 'buy' and not self.bought:
            self.buy_size = self.risk.get_size(row)
            self.trader.limit_order('buy', row['close'], self.buy_size, self)
            
            self.max_price = row['close']
            self.bought = True

        elif signal == 'sell' and self.bought:
            self.trader.limit_order('sell', row['close'], self.buy_size, self)
            
            self.bought = False
            self.buy_size = None
            self.max_price = None
            self.exits = None
            
        else:
            pass


class MeanReversionStrategy(BaseStrategy):
    def __init__(self, env, bt):
        super().__init__(env, bt)
        self.bought = False # flag to track if a position has been bought
        self.entry = None  # entry price for the position
        self.exits = None  # list to keep track of exit signals


    def generate_signal(self, row): 
        """
        Generates a signal based on the current state of the strategy
        Returns "buy" or "hold"
        """
        for exit in self.exits:
            if row['close'] <= exit and self.bought:
                return 'sell'

        score = 0
        score = (row['macd_hist'] > 0).astype(int) + \
                (row['qema_d1'] > 0).astype(int) + \
                (row['qema_d2'] > 0).astype(int) + \
                (row['close'] > row['donchian_upper']).astype(int) + \
                (row['ema_60'] > row['ema_240'] and row['close'] > row['ema_60']).astype(int)
        
        if score >= 4 and not self.bought:
            return 'buy'
        else:
            return 'hold'


    def get_exits(self, row):
        """
        Generates exit signals based on the row data
        Returns a list of exit prices
        """
        exits = []

        return exits


    def action(self, signal, row):
        """
        Executes the action based on the generated signal
        If the signal is "buy", it places a limit order below the current price
        If the signal is "sell", it places a limit order above the current price
        Else it does nothing
        """
        if signal == 'buy' and not self.bought:
            size = self.risk.get_size(row)
            self.trader.limit_order('buy', row['close'] * 0.99, size, self)
            self.bought = True
        elif signal == 'sell' and self.bought:
            size = self.risk.get_size(row)
            self.trader.limit_order('sell', row['close'] * 1.01, size, self)
            self.bought = False
        else:
            pass

