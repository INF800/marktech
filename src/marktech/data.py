from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass 
import streamlit as st
from dateutil.parser import parse
import utils
import pandas as pd
import plotly.graph_objects as go



@dataclass
class HistoricalData:
    
    # required arguments
    dataset_dir: Path 
    pattern: str
    
    # optional
    available_stocks = ['HLL', 'INFY','RELI', 'HDBK']
    time_column = 'time'


    # @st.cache(show_spinner=False) 
    def load_stock_data(self, stock):
        pattern = f"*{stock}*{self.pattern}*"
        return utils.load_csv_files(self.dataset_dir, pattern)


    def plot_data(self, fig, beg, end, symbol, candle10=False):
        # filter data by time stamps in selection area
        data = self._data[symbol]
        data = data[beg:end+timedelta(days=1)]

        # raw data plot (2mins)        
        raw_time = data.index
        raw_close = data.y.values
        fig = fig.add_trace(
            go.Scatter(
                x=raw_time,
                y=raw_close,
                mode="lines",
                name=symbol,
            ),
        )

        if not candle10:
            return fig

        # todo: i think there is some issue...
        # candle stick for 10mins skip every 5th data point
        # for 10min because time interval is 2min
        time10 = raw_time[::5]
        close10 = raw_close[::5]
        open10 = [close10[0], *close10[:-1]]
        high10 = [raw_close[i:i+5].max() for i in range(0, len(raw_close), 5)]
        low10 = [raw_close[i:i+5].min() for i in range(0, len(raw_close), 5)]

        fig = fig.add_trace(
            go.Candlestick(
                x=time10,
                open=open10,
                close=close10,
                high=high10,
                low=low10,
                name=symbol,
            )
        )
        return fig


    def stock_life(self, symbol):
        data = self._data[symbol]
        beg = data.index[0]
        end = data.index[-1]
        interval = data.index[-1]-data.index[-2]
        return beg, end, interval


    def __post_init__(self):
        self._data = {}
        for stock in self.available_stocks:
            data = self.load_stock_data(stock)
            data[self.time_column]= pd.to_datetime(data[self.time_column])
            self._data[stock] = data.set_index(self.time_column)

