from backspaceAlpha.framework import BackTest
from backspaceAlpha.examples import PairsTradingStrategy, MeanReversionStrategy, BuyAndHoldSPYStrategy

'''
Quick example to show how to use the backtester to run the simulation and then show results
Can process a backtest of 5 years on a 1 day timeframe in about a few seconds with a large portfolio
'''

#Run the backtest on multiple strategies simultaneously
strategies = [PairsTradingStrategy(),MeanReversionStrategy(),BuyAndHoldSPYStrategy()]
backtest = BackTest(strategies, ('2000-01-01', '2025-01-01'), 10000, "YAHOO", "1D", verbose=False)
backtest.run()

#Show graphs for the results of the backtest
backtest.show_portfolio()
backtest.show_stock("MeanReversionStrategy", "SPY")
backtest.show_stock("BuyAndHoldSPYStrategy", "SPY")
backtest.show_graph([{"strategy": "PairsTradingStrategy", "variable": "Spread"}])

#Show results of the backtest
backtest.show_results()