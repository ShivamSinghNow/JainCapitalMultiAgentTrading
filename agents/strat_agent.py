from strategy_tuning import strategies as s

class StrategySelector:
    """
    Bot that chooses strategy
    """
    def __init__(self, model):
        self.strategies = {
            'momentum' : s.MomentumStrategy(),
            'grid' : s.GridStrategy(),
            'breakout' : s.BreakoutStrategy(),
            'mean_reversion' : s.MeanReversionStrategy()
        } # dictionary of strategies and strategy objects
        self.model = model # trained model to be used
        self.counter = 0 # counter for updating the current strategy
        self.current_strategy = None # keeping track of current strategy

    def select_strategy(self, features):
        """
        Runs model on data and chooses next strategy to use
        """
        prediction = self.model.predict(features)
        return self.strategies[prediction[0]]
    
    def update(self, features):
        """
        Updates current strategy every 20 periods
        Returns action for current strategy
        """
        if self.counter%20 == 0 or self.current_strategy == None:
            self.current_strategy = self.select_strategy(features)
        self.counter += 1

        return self.current_strategy.generate_signal()
        


        


