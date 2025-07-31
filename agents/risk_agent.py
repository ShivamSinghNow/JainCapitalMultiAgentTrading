class RiskAgent:
    def __init__(self, env, regime_sensitivity=0.5):
        self.env = env # trading environment to keep track of trades and balances
        self.max_inventory = 1 # maximum inventory allowed
        self.risk_factor = 1.0 # risk factor to adjust position size
        self.regime_sensitivity = regime_sensitivity # sensitivity to market regime changes
        self.drawdown = 0.0 # maximum drawdown
        self.base_size = (0.01 * self.env.cash) # base size of percent of capital to be used
        self.var = 0.02  # value at risk for position sizing
    
    
    def get_size(self, row):
        vol = row['volatility']
        regime = row['regime']
        adjustment = 1 + (vol * self.risk_factor)

        if regime == 'high_vol':
            adjustment *= 1 - self.regime_sensitivity
        elif regime == 'low_vol':
            adjustment *= 1 + self.regime_sensitivity

        return self.base_size/row['close'] * adjustment


    def update(self, pnl, inventory):
        self.drawdown = max(self.drawdown, -pnl)
