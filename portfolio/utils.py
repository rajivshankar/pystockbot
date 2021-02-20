import logging
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
from django_pandas.io import read_frame

from assets import controller as co

logger = logging.getLogger(__name__)


def get_analytical_data(ticker):
    df_asset_prices = pd.DataFrame()
    df_asset_prices = co.get_data_for_ticker(ticker, dataset='all')
    df_asset_prices['sma_10w'] = calculate_SMA(df_asset_prices['adj_close'], 70)
    df_asset_prices['sma_30w'] = calculate_SMA(df_asset_prices['adj_close'], 70)
    df_asset_prices['adj_close_index'] = get_index_ticker_prices(ticker)
    series_mansfield = calculate_mansfield_relative_strength(
        df_asset_prices['adj_close'], df_asset_prices['adj_close_index'])
    df_asset_prices['RSM'] = series_mansfield
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
    except:
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

