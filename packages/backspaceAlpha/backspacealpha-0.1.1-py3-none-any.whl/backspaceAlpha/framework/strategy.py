from abc import ABC, abstractmethod
from .broker import Broker
from .loader import BaseDataFeed

class Strategy(ABC):
    '''
    Base class that all strategies are defined from - ALL STRATEGIES MUST INHERIT THIS CLASS
    Contains an update function which is where the logic of the strategy should be housed
    '''
    def __init__(self, portfolio, name):
        '''
        Initialises some variables that will be used by the backtester
        '''
        self.portfolio = portfolio
        self.broker: Broker = None
        self.feed: BaseDataFeed = None
        self.name = name
    
    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def update(self, data):
        pass
    
    def log(self, name, value):
        self.broker.log_variable(name, value)