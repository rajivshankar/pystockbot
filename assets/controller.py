import logging
import datetime
import pandas as pd
from django_pandas.io import read_frame

from django.core.exceptions import ObjectDoesNotExist

from .models import Asset, AssetPrice
from . import data_collection as dc

logger = logging.getLogger(__name__)

COL_MAPPING_YAHOO_DATABASE = {
    'High': 'high',
    'Low': 'low',
    'Open': 'open',
    'Close': 'close',
    'Volume': 'volume',
    'Adj Close': 'adj_close',
}

def update_asset_data_for_sp500():
    df_sp500_metadata = dc.get_SP500_info()
    number_of_records = 0
    asset_list = get_asset_list(df_sp500_metadata)
    try:
        logger.debug(f'storing Asset list')
        Asset.objects.bulk_create(asset_list)
        number_of_records = len(asset_list)
    except Exception as e:
        logger.error(f"Error {e} saving asset list")
    return number_of_records


def get_asset_list(df_sp500_metadata):
    asset_list = []
    if df_sp500_metadata.empty:
        return asset_list
    for i in df_sp500_metadata.index:
        symbol = df_sp500_metadata.loc[i, 'Symbol']
        logger.debug(f'adding asset class for {symbol}')
        asset = Asset(
            symbol=symbol,
            market_symbol='^GSPC',
            security_name=df_sp500_metadata.loc[i, 'Security'],
            gics_industry=df_sp500_metadata.loc[i, 'GICS Sector'],
            gics_sub_industry=df_sp500_metadata.loc[i, 'GICS Sub-Industry'],
        )
        asset_list.append(asset)
    return asset_list

    
def update_asset_price_data_for_sp500():
    number_of_tickers = 0
    num_price_points = 0

    df_sp500_metadata = dc.get_SP500_info()
    ticker_list = df_sp500_metadata['Symbol'].to_list()
    ticker_list.append(dc.SP500_INDEX_TICKER)
    ticker_list.sort()

    for ticker in ticker_list:
        num_price_points += update_asset_price_for_sp500_ticker(ticker)
        number_of_tickers += 1
        logger.debug(f'updated {num_price_points} price points for {ticker}')
    
    return number_of_tickers, num_price_points


def update_asset_price_for_sp500_ticker(ticker):
    num_price_points = 0
    df_ticker_data = get_data_for_ticker(ticker, dataset='new')
    asset_price_list = get_asset_price_list(ticker, df_ticker_data)
    try:
        logger.debug(f'storing Asset Prices for {ticker}')
        AssetPrice.objects.bulk_create(asset_price_list)
        num_price_points = len(asset_price_list)
    except Exception as e:
        logger.error(f"{ticker}: Error {e} on price_point for {date}")
    return num_price_points


def get_data_for_ticker(ticker, dataset='all'):
    logger.debug(f'retrieving EXISTING for {ticker} from DB')
    df_prev_data = get_existing_data_for_ticker(ticker)

    if dataset=='existing':
        return df_prev_data
    
    logger.debug(f'retrieving NEW for {ticker} from DB')
    start_date, end_date = dc.get_ticker_start_and_end_dates(df_prev_data)
    df_new_data = get_new_data_for_ticker(ticker, start_date, end_date)

    if dataset=='new':
        return df_new_data

    logger.debug(f'retrieving ALL for {ticker} from DB')
    if df_prev_data.empty:
        df_prev_data = df_new_data
    else:
        df_prev_data =  df_prev_data.append(df_new_data)
    return df_prev_data


def get_existing_data_for_ticker(ticker):
    df_result = pd.DataFrame()
    try:
        ticker_asset = Asset.objects.get(symbol=ticker)
        ticker_prices = AssetPrice.objects.filter(asset_id=ticker_asset.id)
        if ticker_prices:
            df_result = read_frame(ticker_prices, index_col='datetime')
            df_result.drop(['id', 'asset'], axis=1, inplace=True)
    except ObjectDoesNotExist:
        logger.error(f'Asset {ticker} does not Exist')
    except Exception as e:
        logger.error(f'ERROR get data for {ticker}: {e}')
    return df_result


def get_new_data_for_ticker(ticker, start_date, end_date):
    df_new_data = pd.DataFrame()
    try:
        if start_date != end_date:
            df_new_data = dc.ping_yahoo_for_ticker(ticker, start_date, end_date)
        if not(df_new_data.empty):
            
            df_new_data.rename(columns=COL_MAPPING_YAHOO_DATABASE, inplace=True)
            df_new_data.index.name = 'datetime'
    except Exception as e:
        logger(f'Error {e} occured when getting new date for {ticker}')
    return df_new_data


def get_asset_price_list(ticker, df_ticker_data):
    asset_price_list = []
    if df_ticker_data.empty:
        return asset_price_list
    try:
        asset = Asset.objects.get(symbol=ticker)
        for i in range(len(df_ticker_data.index)):
            data = df_ticker_data.iloc[i].to_dict()
            date = pd.to_datetime(df_ticker_data.index[i])
            date = date.replace(tzinfo=datetime.timezone.utc)
            asset_price = AssetPrice(
                                     asset = asset,
                                     datetime = date,
                                     high = data['high'],
                                     low = data['low'],
                                     open = data['open'],
                                     close = data['close'],
                                     volume = data['volume'],
                                     adj_close = data['adj_close'],
                                     )
            asset_price_list.append(asset_price)
    except ObjectDoesNotExist:
        logger.error(f'Asset not found. Skipping {ticker}')
    except Exception as e:
        logger.error(f'Error {e} processing {ticker}. Skipping')
    return asset_price_list
