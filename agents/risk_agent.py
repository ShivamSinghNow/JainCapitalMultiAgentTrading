class RiskAgent:
    def __init__(self, max_inventory, env, regime_sensitivity=0.5):
        self.max_inventory = max_inventory
        self.env = env
        self.risk_factor = 1.0
        self.regime_sensitivity = regime_sensitivity
        self.risk_factor = 1.0
        self.drawdown = 0.0
        self.base_size = 0.01 
    
    def get_size(self, row):
        vol = row['volatility']
        regime = row['regime']

        adjustment = 1 + (vol * self.risk_factor)
        if regime == 'high_vol':
            adjustment *= 1 - self.regime_sensitivity
        elif regime == 'low_vol':
            adjustment *= 1 + self.regime_sensitivity

        return self.base_size * adjustment


    def should_trade(self, state):
        if abs(self.inventory) >= self.max_inventory:
            return False
        if self.drawdown > 0.1: 
            return False
        return True
    

    def update(self, pnl, inventory):
        self.drawdown = max(self.drawdown, -pnl)
        self.inventory = inventory