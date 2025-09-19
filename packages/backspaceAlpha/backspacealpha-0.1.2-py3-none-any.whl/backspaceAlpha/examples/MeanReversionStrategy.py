from backspaceAlpha.framework.strategy import Strategy
import numpy as np

class MeanReversionStrategy(Strategy):
    def __init__(self):
        super().__init__(["SPY"], self.__class__.__name__)
    
    def init(self):
        self.window_size = 25
        self.threshold = 2
        self.exit = 0.5
        self.shares = 5
    
    def update(self, data):
        #Get close prices
        price = data[0][3]
        
        #Get rolling window
        previous_prices = self.feed.previous(self.window_size)[:,:,3]
        mean = np.mean(previous_prices)
        std = np.std(previous_prices)
        
        #Calculate z-score
        if std == 0:
            return
        z = (price - mean)/(std)
        
        #Make trades
        if z > self.threshold:
            self.broker.short(self.portfolio[0], self.shares, "short_order")
        elif z < -self.threshold:
            self.broker.long(self.portfolio[0], self.shares, "long_order")
        elif z < self.exit and z > -self.exit:
            self.broker.close("short_order")
            self.broker.close("long_order")