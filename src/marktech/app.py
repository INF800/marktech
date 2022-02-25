from pathlib import Path
from datetime import datetime, timedelta
import time

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from data import HistoricalData
from config import CfgPlot



st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title('Marktech 📈')


def add_sidebar(display_name="Selection"):
    wslc = st.sidebar.container() # create an empty container in the sidebar
    wslc.markdown(f"## {display_name}") # add a title to the sidebar container
    return wslc


def stock_selection(sidebar, history):
    symbol = sidebar.selectbox("Stock", history.available_stocks)
    return symbol


def date_selection(symbol, sidebar, history):
    selection = sidebar.columns(2)
    default_beg, default_end, interval = history.stock_life(symbol)

    beg = selection[0].date_input("From", value=default_beg, max_value=default_end, min_value=default_beg)
    end = selection[1].date_input("To", value=default_end, max_value=default_end, min_value=beg)
    return beg, end, interval


def enable_candlestick_plot():
    return st.checkbox('10min candlestick')


def plot_data(beg, end, symbol, history, enable_candle):
    chart_width = st.expander(label="chart width").slider("", *CfgPlot.slider_options)

    fig = go.Figure()
    fig = history.plot_data(fig, beg, end, symbol, candle10=enable_candle)
    fig.update_layout(width=chart_width, **CfgPlot.layout_kwds)
    fig.update_xaxes(rangebreaks=CfgPlot.rangebreaks)
    return fig




def main():
    # load data
    history = HistoricalData(dataset_dir=Path('data/feature'), pattern='univar-latest')

    # user interface
    sidebar = add_sidebar(display_name="Selection")
    symbol = stock_selection(sidebar, history)
    beg, end, interval = date_selection(symbol, sidebar, history)
    enable_candle = enable_candlestick_plot()

    # plot data
    fig = plot_data(beg, end, symbol, history, enable_candle)
    st.write(fig)

    # todo: handle multivariate data 

    # todo: plot live data

    # todo: plot seasonality & other metrics

    # todo: train model

    # changes in sidebar
    change_sidebar = st.sidebar.container()
    with change_sidebar:
        # do something wrt change
        print(symbol, interval, beg)


if __name__=='__main__':
    main()
