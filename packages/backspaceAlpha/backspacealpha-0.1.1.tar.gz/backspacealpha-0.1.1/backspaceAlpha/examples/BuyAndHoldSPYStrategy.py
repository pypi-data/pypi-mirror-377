from backspaceAlpha.framework.strategy import Strategy
import numpy as np

class BuyAndHoldSPYStrategy(Strategy):
    def __init__(self):
        super().__init__(["SPY"], self.__class__.__name__)
    
    def init(self):
        self.once = False
        self.shares = 0
    
    def update(self, data):
        #Ensures only run once at start
        if not self.once:
            #Calculate how many shares
            price = data[0][3]        
            self.shares = self.broker.cash // price
            
            #Buys those shares
            self.broker.buy(self.portfolio[0], self.shares)

            #Ensures it is not rerun
            self.once = True
        
        #Sells all stocks at the end
        if not self.feed.has_next():
            self.broker.sell("SPY", self.shares)