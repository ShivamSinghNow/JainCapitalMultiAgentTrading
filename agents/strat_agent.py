from strategy_tuning import strategies as s

class StrategySelector:
    """
    Bot that chooses strategy
    """
    def __init__(self, model, pca, scaler, state_map):
        self.strategies = {
            'momentum' : s.MomentumStrategy(),
            'grid' : s.GridStrategy(),
            'mean_reversion' : s.MeanReversionStrategy()
        } # dictionary of strategies and strategy objects
        self.model = model # trained model to be used
        self.scaler = scaler # scaler used for training the model
        self.pca = pca # pca used for training model
        self.state_map = state_map # 
        self.counter = 0 # counter for updating the current strategy
        self.current_strategy = None # keeping track of current strategy

    def select_strategy(self, row):
        """
        Runs model on data and chooses next strategy to use
        """
        X = self.scaler.transform(row.to_frame().T)
        X = self.pca.transform(X)
        pred = self.model.predict(X)
        regime = self.state_map[pred[0]]
        
        if regime == 'low_vol':
            return self.strategies['grid']
        elif regime == 'high_vol':
            return self.strategies['mean_reversion']
        elif regime == 'trending':
            return self.strategies['momentum']
    
    def update(self, row, lookback_data):
        """
        Updates current strategy every 20 periods
        Returns action for current strategy
        """
        self.counter += 1

        if self.counter == 60 or self.current_strategy == None:
            self.current_strategy = self.select_strategy(row)
            self.counter = 0

        return self.current_strategy.generate_signal(lookback_data)
        


        


