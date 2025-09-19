from .loader import MultiDataFeed
from .broker import Broker
from .strategy import Strategy
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
from tqdm import tqdm
from datetime import datetime

class BaseBackTest:
    '''
    This class is used to bring everything together and run the backtest on it. The heart of the modular system
    Allows you to run the backtest on a strategy and provides some graphs to show results:
    - Portfolio Value vs Time               (shows overall how portfolio performed)
    - Portfolio Distribution vs Time        (shows PnL of different stocks in the portfolio over time)
    - Ticker Value vs Time                  (shows when trades were made on a ticker as its price changed)
    - Overall                               (shows results of the strategy (profit))
    - Will be adding more values and metrics soon...
    '''
    def __init__(self, strategy: Strategy, time_frame, start=10000, source="YAHOO", interval="1D", verbose=True, hedging=False):
        self.start = start
        self.strategy = strategy
        self.verbose = verbose
        self.portfolio = self.strategy.portfolio
        self.broker = Broker(self.portfolio, start, verbose=verbose, hedging=hedging)
        self.strategy.broker = self.broker
        self.feed = MultiDataFeed(self.portfolio, time_frame, source, interval)
        self.strategy.feed = self.feed
        self.strategy.init()
    
    def run(self, pbar = None):
        '''
        Heart of the backtest and does the basic loop:
        - Updates data feed by 1 tick
        - Sends data to broker first
        - Then strategy
        - Allows broker to respond to new orders from strategy
        '''
        if not self.verbose and pbar is None:
            pbar = tqdm(total=self.feed.feeds[0].length, ncols=70, desc="Running Backtest")
        while self.feed.has_next():
            data = self.feed.next()
            self.broker.update_price(data[:,3])
            self.strategy.update(data)
            self.broker.update()
            if not self.verbose:
                pbar.update(1)
        if not self.verbose and pbar is None:
            pbar.close()
    
            
    def show_portfolio(self):
        data = [x["equity"] for x in self.broker.history]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data)
        formatter = ScalarFormatter(useOffset=False)
        ax.yaxis.set_major_formatter(formatter)
        plt.title(f"{self.strategy.name} - Portfolio Value")
        plt.xlabel("Time Step")
        plt.ylabel("Portfolio Value")
        plt.grid(True)
        plt.show()
        
    def show_portfolio_distribution(self):
        data = [x["portfolio"] for x in self.broker.history]
        data = np.array(data)
        plt.figure(figsize=(10, 5))
        for i in range(data.shape[1]):
            plt.plot(data[:, i], label=self.portfolio[i])
        plt.legend()
        plt.title(f"{self.strategy.name} - Portfolio Distribution")
        plt.xlabel("Time Step")
        plt.ylabel("PnL of Open Positions")
        plt.grid(True)
        plt.show()


    def show_stock(self, ticker):
        distance = 0.2
        i = self.portfolio.index(ticker)
        data = [x["current"][i] for x in self.broker.history]
        orders = enumerate([x['orders'][ticker] for x in self.broker.history])
        open = {}
        plt.figure(figsize=(10, 5))
        plt.plot(data)
        for t, a in orders:
            for order in a:
                if order[0] == "B" or order[0] == "LNG":
                    plt.scatter(t, data[t] - distance, marker='^', color='green', label=order[1], s=100)
                elif order[0] == "S" or order[0] == "SHT":
                    plt.scatter(t, data[t] + distance, marker='v', color='red', label=order[1], s=100)
                   
                if order[0] == "LNG" or order[0] == "SHT":
                    open[order[2]] = (t,order[0],order[5]) 
                    
                if order[0] == "CLS":
                    start, action, price = open[order[1]]
                    if action == "LNG":
                        plt.plot([start, t], [price, price], linestyle='--', color='green', linewidth=1.5)  
                        if data[t] > price:
                            plt.scatter(t, price-distance, marker='^', color='green', s=100) 
                        else:
                            plt.scatter(t, price+distance, marker='v', color='red', s=100)     
                    else:
                        plt.plot([start, t], [price, price], linestyle='--', color='red', linewidth=1.5)  
                        if data[t] < price:
                            plt.scatter(t, price+distance, marker='v', color='green', s=100) 
                        else:
                            plt.scatter(t, price-distance, marker='^', color='red', s=100)
                    del open[order[1]]
        t = len(data)-1
        for id, o in open.items():
            start, action, price = o
            if action == "LNG":
                plt.plot([start, t], [price, price], linestyle='--', color='gray', linewidth=1.5) 
            else: 
                plt.plot([start, t], [price, price], linestyle='--', color='gray', linewidth=1.5)
        plt.title(f"Stock Value with Buys/Sells - {ticker}")
        plt.xlabel("Time Step")
        plt.ylabel("Stock Value")
        plt.grid(True)
        plt.show()
        
    def show_results(self):
        final = self.broker.history[len(self.broker.history)-1]
        tqdm.write(f"\n\nRESULTS - {self.strategy.name}:")
        tqdm.write(f"Profit: £{final['equity']-self.start}")
        
class BackTest:
    def __init__(self, strategy: [Strategy], time_frame, start=10000, source="YAHOO", interval="1D", verbose=True, hedging=False):
        self.backtests = []    
        self.verbose = verbose    
        for strat in strategy:
            self.backtests.append(BaseBackTest(strat, time_frame, start, source, interval, verbose, hedging))
        self.names = [x.strategy.name for x in self.backtests]
        if len(strategy) == 0:
            print("ERROR - Please ensure there are valid strategies to backtest")
            return
        start_dt = datetime.strptime(time_frame[0], '%Y-%m-%d')
        end_dt   = datetime.strptime(time_frame[1], '%Y-%m-%d')
        delta_days = (end_dt - start_dt).days
        self.years = delta_days / 365.25
        if self.years <= 0:
            print("ERROR - Please ensure that a valid timeframe has been inputted")
            return
    
    def run(self):
        if len(self.names) == 0:
            print("ERROR - Please ensure there are valid strategies to backtest")
            return
        pbar = None
        if not self.verbose:
            lengths = [x.feed.feeds[0].length for x in self.backtests]
            pbar = tqdm(total=np.sum(lengths), ncols=70, desc="Running Backtest")
        for backtest in self.backtests:
            backtest.run(pbar)
        if not self.verbose:
            pbar.close()
    
    def show_portfolio(self):
        if len(self.names) == 0:
            print("ERROR - Please ensure there are valid strategies to backtest")
            return
        plt.figure(figsize=(10, 5))
        for i in range(len(self.backtests)):
            data = [x["equity"] for x in self.backtests[i].broker.history]
            plt.plot(data, label=self.names[i])
        plt.legend()
        plt.title(f"Portfolio Value")
        plt.xlabel("Time Step")
        plt.ylabel("Portfolio Value")
        plt.grid(True)
        plt.show()
        
    def show_stock(self, name, ticker):
        if len(self.names) == 0:
            print("ERROR - Please ensure there are valid strategies to backtest")
            return
        if name not in self.names:
            print("ERROR - Please ensure the given strategy was present in the backtest")
            return
        i = self.names.index(name)
        if ticker not in self.backtests[i].portfolio:
            print("ERROR - Please ensure the given ticker is present in the strategy portfolio")
            return
        self.backtests[i].show_stock(ticker)
        
    def show_graph(self, variable_names):
        plt.figure(figsize=(10, 5))
        name = ""
        for variable in variable_names:
            if variable["strategy"] not in self.names:
                print("ERROR - Please ensure the given strategy was present in the backtest")
                return
            i = self.names.index(variable["strategy"])
            if variable["variable"] not in self.backtests[i].broker.history[0]:
                print("ERROR - Please ensure the given variable was present in the strategy")
                return
            data = [x[variable["variable"]] for x in self.backtests[i].broker.history]
            name += f"{self.names[i]} ({variable["variable"]}), "
            plt.plot(data, label=f"{self.names[i]} ({variable["variable"]})")
        plt.legend()
        plt.title(name[:-2])
        plt.xlabel("Time Step")
        plt.ylabel("Value")
        plt.grid(True)
        plt.show()

    def show_results(self):
        if len(self.names) == 0:
            print("ERROR - Please ensure there are valid strategies to backtest")
            return
        results = [ ["","Start [$]","Final [$]","Peak [$]","Profit [$]","Return [%]", "Return (CAGR) [%]", "Max Drawdown [%]"] ]
        for backtest in self.backtests:
            result = []
            data = [x["equity"] for x in backtest.broker.history]
            result.append(backtest.strategy.name)
            result.append(backtest.start)
            final = data[len(backtest.broker.history)-1]
            result.append(final)
            result.append(max(data))
            result.append(final - backtest.start)
            result.append(((final - backtest.start)/backtest.start)*100)
            result.append((((final/backtest.start)**(1/self.years))-1)*100)
            running_max = np.maximum.accumulate(data)
            drawdowns = (data - running_max) / running_max
            result.append(drawdowns.min()*100)
            results.append(result)
        data = list(zip(*results))
        spacing = np.max([len(x) for x in data[0]])
        spacing = max(spacing, 20)
        
        formatted = []        
        for row in data:
            new_row = []
            for val in row:
                if isinstance(val, (float, np.floating, int)):
                    new_row.append(f"{val:{spacing}.{5}{"g"}}")
                else:
                    new_row.append(str(val).ljust(spacing))  # pad strings
            formatted.append(new_row)
        
        tqdm.write("Backtest Complete - Outputting results\n")
        tqdm.write(" | ".join(formatted[0]) + " |")
        tqdm.write("-"*spacing + "-|-" + ("-"*spacing + "-+-")*(len(self.names)-1) + "-"*spacing + "-|")
        for row in formatted[1:]:
            tqdm.write(" | ".join(row) + " |")