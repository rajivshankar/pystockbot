import logging
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone, timedelta
from django_pandas.io import read_frame
import matplotlib.pyplot as plt
import base64
from io import BytesIO

from assets import controller as co

logger = logging.getLogger(__name__)


def get_analytical_data(ticker):
    df_asset_prices = pd.DataFrame()
    df_asset_prices = co.get_data_for_ticker(ticker, dataset='all')
    df_asset_prices['sma_10w'] = calculate_SMA(df_asset_prices['adj_close'], 70)
    df_asset_prices['sma_30w'] = calculate_SMA(df_asset_prices['adj_close'], 210)
    df_asset_prices['adj_close_index'] = get_index_ticker_prices(ticker)
    series_mansfield = calculate_mansfield_relative_strength(
        df_asset_prices['adj_close'], df_asset_prices['adj_close_index'])
    df_asset_prices['rsm'] = series_mansfield
    return df_asset_prices


def calculate_SMA(series, tenor):
    result = pd.Series()
    try:
        result = series.rolling(window=tenor, min_periods=1).mean()
    except Exception as e:
        logger.error(
            f'Exception {e} occured whilst calculating SMA for tenor: {tenor}')
    return result.astype('float')


def get_index_ticker_prices(ticker):
    result = pd.Series()
    index_ticker = co.get_index_ticker(ticker)
    df_index_prices = co.get_data_for_ticker(index_ticker)
    try:
        result = df_index_prices['adj_close']
    except Exception as e:
        logger.error(f'Exception {e} occured when getting index prices')

    return result.astype('float')


def calculate_dorsey_relative_strength(series, index_series):
    '''
    Calculates the Dorsey Relative Strenth using the historical data of the ticker and index_ticker
    '''
    result = pd.Series
    result = (series.astype('float') / index_series.astype('float')) * 100
    return result.astype('float')


def calculate_mansfield_relative_strength(series, index_series):
    """
    Calculates the Mansfield Relative Strength of the stock based on the value of Dorsey RS
    given by the key 'RSD' in the data frame
    """
    result = pd.Series(dtype=float)
    series_rsd = calculate_dorsey_relative_strength(series, index_series)
    try:
        result = ((series_rsd / series_rsd.rolling(window=7 *
                                                   52, min_periods=1).mean()) - 1) * 100
    except Exception as e:
        logging.error(f'Error {e} while computing RSM')
    return result.astype('float')


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x, y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10,5))
    plt.title("Stock Prices")
    plt.plot(x, y)
    plt.xticks(rotation=45)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.tight_layout()
    graph = get_graph()
    return graph


def get_full_plot(df_data):
    plt.switch_backend('AGG')
    # plt.figure(figsize=(10,5))
    # %matplotlib widget
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    fig.set_size_inches(15, 12)
    start_date = df_data.index.min()
    end_date = df_data.index.max()
    fig.suptitle(
        f'Technical Analysis from {start_date} to {end_date}')
    num_rows = 9
    num_cols = 1
    num_rows_ax1 = 5
    num_rows_ax2 = 2
    num_rows_ax3 = 2
    ax1 = plt.subplot2grid((num_rows, num_cols), (0, 0),
                           rowspan=num_rows_ax1, colspan=1)
    ax2 = plt.subplot2grid((num_rows, num_cols), (5, 0),
                           rowspan=num_rows_ax2, colspan=1, sharex=ax1)
    ax3 = plt.subplot2grid((num_rows, num_cols), (7, 0),
                           rowspan=num_rows_ax3, colspan=1, sharex=ax1)

    # Main share price chart
    ax1.plot(df_data['adj_close'], label='Adj Close')
    ax1.plot(df_data['sma_10w'], label='SMA - 10 week')
    ax1.plot(df_data['sma_30w'], label='SMA - 30 week')

    # ax1.plot(df_filtered[df_filtered['Price History 001M']]['{} Adj Close'.format(ticker)], 'c^', label='Local Maxima 1 M')
    # ax1.plot(df_filtered[df_filtered['Price History 036M']]['{} Adj Close'.format(ticker)], 'b^', label='Local Maxima 36 M')

    # ax1.plot(df_filtered[df_filtered['Stage Trend 30W'] == 1]['SMA 30W'], 'g^')
    # ax1.plot(df_filtered[df_filtered['Stage Trend 30W'] == -1]['SMA 30W'], 'rv')
    # ax1.plot(df_filtered[df_filtered['Stage Trend 30W'] == 0]['SMA 30W'], 'ys')

    ax1.set_title = 'Adj Close Price History'
    ax1.set_ylabel('Adj. Close Price in USD ($)')
    ax1.legend(loc='upper left')

    # Volume chart
    ax2.bar(df_data.index.map(mdates.date2num), df_data['volume'])
    # ax2.plot(df_data['Volume SMA 30D'], label='SMA - 30 day', color='b', alpha=0.3)

    ax2.legend(loc='upper left')
    ax2.set_ylabel('Volumes (10 mio)')

    # Mansfield Relative Strength chart
    ax3.plot(df_data['rsm'], label='Mansfield RS')
    ax3.axhline(y=0, color='g', alpha=0.4)

    ax3.legend(loc='upper left')
    ax3.set_ylabel('Mansfield RS')

    # plt.show()

    plt.tight_layout()
    graph = get_graph()
    return graph
