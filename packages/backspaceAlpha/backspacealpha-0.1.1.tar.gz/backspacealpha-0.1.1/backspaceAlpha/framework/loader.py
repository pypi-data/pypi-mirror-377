import yfinance as yf
import numpy as np
from ib_insync import IB, Stock, util
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import os

class BaseDataFeed:
    '''
    Basic class used to define what a datafeed should be capable of doing.
    Based on a Java Iterator class and includes the functions:
    - has_next(): used to check if there is still more data
    - next(): used to return the next element and move data feed along
    - previous(): used to return previous elements (can be multiple)
    '''
    def has_next(self):
        raise NotImplementedError
    
    def next(self):
        raise NotImplementedError
    
    def previous(self):
        raise NotImplementedError

class YahooDataFeed(BaseDataFeed):
    '''
    Instance of BaseDataFeed class that uses Yahoo Finance
    Is initialised with a symbol and the timeframe
    '''
    def __init__(self, symbol, time_frame):
        data = yf.download(symbol, start=time_frame[0], end=time_frame[1], auto_adjust=True)
        self.df = data.reset_index(drop=True)
        self.index = 0
        self.length = len(self.df)

    def has_next(self):
        return self.index < self.length

    def next(self):
        row = self.df.iloc[self.index]
        self.index += 1
        return row.to_numpy()
    
    def previous(self, num):
        start = max(0, self.index - num)
        sub_df = self.df.iloc[start:self.index]
        return sub_df.to_numpy()

class IBKRDataFeed(BaseDataFeed):
    '''
    WIP:
    Will be an instance of BaseDataFeed that can fetch data from IBKR. 
    To be used for intraday behaviour
    '''
    def __init__(self, symbol, time_frame, interval, storage_dir='data', host='127.0.0.1', port=7497, client_id=1):
        self.symbol = symbol
        self.start_date = pd.to_datetime(time_frame[0])
        self.end_date = pd.to_datetime(time_frame[1])
        self.interval = interval
        print(interval)
        self.storage_dir = storage_dir
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)
        self.contract = Stock(symbol, 'SMART', 'USD')

        self.chunk_days = self.interval_to_duration_days(interval)
        self.sleep_between_requests = 12
        self.data_path = os.path.join(storage_dir, symbol, interval.replace(' ', ''))
        os.makedirs(self.data_path, exist_ok=True)

        self.df = pd.DataFrame()
        self.index = 0

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._load_data())

    def _get_chunk_file(self, start, end):
        return os.path.join(self.data_path, f"{start.date()}_{end.date()}.parquet")

    def _is_downloaded(self, start, end):
        return os.path.exists(self._get_chunk_file(start, end))
    
    def interval_to_duration_days(self, interval):
        mapping = {
            '1 sec': 0.02,     # ~30 minutes
            '5 secs': 0.2,     # ~5 hours
            '10 secs': 0.5,    # ~12 hours
            '15 secs': 1,      # ~1 day
            '30 secs': 2,      # ~2 days
            '1 min': 7,        # ~1 week
            '2 mins': 14,
            '3 mins': 21,
            '5 mins': 30,      # ~1 month
            '15 mins': 90,     # ~3 months
            '30 mins': 180,
            '1 hour': 180,     # ~6 months
            '1 day': 1000      # multiple years
        }
        return mapping.get(interval.lower(), 7)  # default to 7 days if unknown

    async def _fetch_chunk(self, end_time):
        bars = await self.ib.reqHistoricalDataAsync(
            self.contract,
            endDateTime=end_time.tz_localize('UTC') if end_time.tzinfo is None else end_time,
            durationStr=f'{self.chunk_days} D',
            barSizeSetting=self.interval,
            whatToShow='TRADES',
            useRTH=False,
            formatDate=1
        )
        df = util.df(bars)
        if not df.empty:
            df['date'] = df['date'].dt.tz_localize(None)
        return df

    async def _load_data(self):
        current_end = self.end_date
        frames = []

        while current_end > self.start_date:
            current_start = max(self.start_date, current_end - timedelta(days=self.chunk_days))
            file_path = self._get_chunk_file(current_start, current_end)

            if self._is_downloaded(current_start, current_end):
                df = pd.read_parquet(file_path)
            else:
                df = await self._fetch_chunk(current_end)
                if not df.empty:
                    df.to_parquet(file_path, index=False)
                    await asyncio.sleep(self.sleep_between_requests)

            if not df.empty:
                frames.append(df)

            current_end = current_start

        if frames:
            self.df = pd.concat(frames).drop_duplicates(subset=['date']).sort_values('date').reset_index(drop=True)
        else:
            self.df = pd.DataFrame()

    def has_next(self):
        return self.index < len(self.df)

    def next(self):
        if not self.has_next():
            raise StopIteration("No more data.")
        row = self.df.iloc[self.index]
        self.index += 1
        return row[['open', 'high', 'low', 'close', 'volume']].to_numpy()
    
    def previous(self, num):
        start = max(0, self.index - num)
        sub_df = self.df.iloc[start:self.index]
        return sub_df[['open', 'high', 'low', 'close', 'volume']].to_numpy()

class MultiDataFeed(BaseDataFeed):
    '''
    Important instance of the base data feed that is able to keep track of multiple individual feeds
    Used for keeping track of an entire portfolio's data feed
    '''
    def __init__(self, portfolio, time_frame, source, interval):
        self.feeds = []
        for ticker in portfolio:
            if source == "IBKR":
                self.feeds.append(IBKRDataFeed(ticker, time_frame, interval))
            elif source == "YAHOO":
                self.feeds.append(YahooDataFeed(ticker, time_frame))
    
    def has_next(self):
        return all(feed.has_next() for feed in self.feeds)  
        
    def next(self):
        out = np.zeros((len(self.feeds), 5))
        for i, feed in enumerate(self.feeds):
            out[i, :] = feed.next()
        return out
            
    def previous(self, num):
        a = min(min([x.index for x in self.feeds]),num)
        out = np.zeros((len(self.feeds), a, 5))
        for i, feed in enumerate(self.feeds):
            out[i,:,:] = feed.previous(a)
        return out