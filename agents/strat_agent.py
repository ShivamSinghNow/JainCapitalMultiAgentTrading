from strategy_tuning import strategies as s

class StrategySelector:
    """
    Bot that chooses strategy
    """
    def __init__(self, model, pca, scaler, state_map, env, backtester):
        self.strategies = {
            'momentum' : s.MomentumStrategy(env, backtester),
            'grid' : s.GridStrategy(env, backtester),
            'mean_reversion' : s.MeanReversionStrategy(env, backtester)
        } # dictionary of strategies and strategy objects
        self.model = model # trained model to be used
        self.scaler = scaler # scaler used for training the model
        self.pca = pca # pca used for training model
        self.state_map = state_map # 
        self.counter = 0 # counter for updating the current strategy
        self.current_strategy = None # keeping track of current strategy
        self.bt = backtester # strategy manager to keep track of active strategies


    def select_strategy(self, i, row):
        """
        Runs model on data and chooses next strategy to use
        """
        X = self.scaler.transform(row.to_frame().T)
        X = self.pca.transform(X)
        pred = self.model.predict(X)
        regime = self.state_map[pred[0]]
        self.bt.data.loc[i, 'regime'] = regime
        
        if regime == 'low_vol':
            return self.strategies['grid']
        elif regime == 'high_vol':
            return self.strategies['mean_reversion']
        elif regime == 'trending':
            return self.strategies['momentum']
    
    
    def update(self, i, row):
        """
        Updates current strategy every 20 periods
        Returns action for current strategy
        """
        self.counter += 1

        if self.counter == 60 or self.current_strategy == None:
            self.current_strategy = self.select_strategy(i, row)

            if not any(t[0] == self.current_strategy for t in self.bt.active_strategies):
                self.bt.active_strategies.append((self.current_strategy, i))
            else:
                for j, (strategy, _) in enumerate(self.bt.active_strategies):
                    if strategy == self.current_strategy:
                        self.bt.active_strategies[j] = (self.current_strategy, i)
                        break

            print(f"Strategy changed to {self.current_strategy.__class__.__name__}")
            self.counter = 0

        signals = []
        for strat in self.bt.active_strategies:
                if i - strat[1] >= 180: 
                    self.bt.active_strategies.remove(strat)
                    continue
                signals.append((strat[0], strat[0].generate_signal(row)))

        return signals
    
        