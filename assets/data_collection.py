import os
import requests
import logging
from datetime import datetime, date, timedelta, timezone
from bs4 import BeautifulSoup
import pandas as pd
import pandas_datareader.data as web

from django.conf import settings

logger = logging.getLogger(__name__)

SP500_WIKI_PAGE = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
DATA_DIR = os.path.join(settings.BASE_DIR, "data", "stock_dfs")
ANALYSIS_PERIOD = 5
SP500_INDEX_TICKER = '^GSPC'


def read_sp500_wiki_page(): 
    """
    Read the wiki page and return the content in HTML
    """
    response  = requests.get(SP500_WIKI_PAGE)
    if not (response.status_code >= 200 and response.status_code < 300):
        return pd.DataFrame()
    
    return response.content
   

def parse_sp500_wiki_page(html_page):
    """
    Read the html and parse the table to return meta data of the stocks
    data plus the column names
    """
    soup = BeautifulSoup(html_page, 'html.parser')
    table = soup.find("table", {"id": "constituents"})
    
    data = []
    column_names = [col_name.text.strip() for col_name in table.find_all('th')]
    for row in table.find_all('tr'):
        data_row = [col_name.text.strip() for col_name in row.find_all('td')]
        if data_row:
            data.append(data_row)
    return data, column_names

    
def get_SP500_info():
    """
    Retrieve the html, parse it and return the data as a pandas DataFrame
    """
    html_page = read_sp500_wiki_page()
    data, column_names = parse_sp500_wiki_page(html_page)
    
    sp_stock_dataframe = pd.DataFrame(data, columns=column_names)
    return sp_stock_dataframe


def get_start_date(end_date=datetime.now(), num_years=ANALYSIS_PERIOD):
    """
    Get the start date of the analysis period based on an end date
    """
    start_date = end_date - timedelta(num_years*365)
    start_date = pd.to_datetime(date(start_date.year, start_date.month, start_date.day))
    return(start_date)


def get_start_and_end_dates(new_start_date=None):
    """
    Get the start and end dates based on the start date input
    if the start date is none, get the whole daya
    """
    curr_date = datetime.utcnow()
    curr_date = pd.to_datetime(date(curr_date.year, curr_date.month, curr_date.day))
    if not(new_start_date):
        end_date = curr_date
        start_date = get_start_date(end_date, ANALYSIS_PERIOD)
    else:
        start_date = new_start_date
        end_date = curr_date
    
    start_date = start_date.replace(tzinfo=timezone.utc)
    end_date = end_date.replace(tzinfo=timezone.utc)
    return start_date, end_date


def get_filename_for_ticker(ticker):
    ticker = ticker.replace('.', '_')
    filename = os.path.join(DATA_DIR, f'{ticker}.csv')
    return filename
    

def get_existing_data_for_ticker(ticker):
    """
    retrieve data from existing file as a pandas DataFrame
    """
    filename = get_filename_for_ticker(ticker)
    logger.debug(f'Processing {filename}')
    df_ticker_data = pd.DataFrame()
    try:
        df_ticker_data = pd.read_csv(filename, index_col='Date')
        df_ticker_data.index = pd.to_datetime(df_ticker_data.index)
    except FileNotFoundError:
        logger.error(f'Error in opening {filename}')
    except Exception as e:
        logging.error(f'Error {e} while accessing existing data')
    return df_ticker_data


def get_ticker_start_and_end_dates(df_data):
    """
    Get the last date in the exisitng data, set the start date as one 
    dayt after, and get the end date as current date
    """
    if df_data.empty:
        start_date, end_date = get_start_and_end_dates()
    else:
        new_start_date = df_data.index.max() + timedelta(days=1)
        logger.debug(f'new start date = {new_start_date}')
        start_date, end_date = get_start_and_end_dates(new_start_date)
    logger.debug(f'returning {start_date} and {end_date} from get_ticker_start_and_end_dates')
    return start_date, end_date


def ping_yahoo_for_ticker(ticker, start_date, end_date):
    """
    retrieve date from yahoo
    """
    logger.debug(f'retrieving for {ticker} from yahoo between {start_date} and {end_date}')
    try:
        df = web.DataReader(ticker, 'yahoo', start_date, end_date)
        logger.debug('Successfully retrieved data for {}'.format(ticker))
        return df
    except Exception as e:
        logging.error('Error while accessing Yahoo - {}'.format(str(e)))
        return pd.DataFrame()


def get_data_for_ticker(ticker):
    """
    get the stock price data, write into CSV and return Pandas DataFrame
    """
    logger.debug(f'processing get_data_for_ticker({ticker})')
    df_data = get_existing_data_for_ticker(ticker)
    start_date, end_date = get_ticker_start_and_end_dates(df_data)
    logger.debug(f'retrieving for {ticker} from {start_date} to {end_date}')
    df_new_data = pd.DataFrame()
    if start_date != end_date:
        df_new_data = ping_yahoo_for_ticker(ticker, start_date, end_date)
    if df_data.empty:
        df_data = df_new_data
    else:
        df_data =  df_data.append(df_new_data)
    return df_data


def retrieve_data_for_all_sp500_tickers(store_in_csv=False):
    """
    get the files for all the information from the S&P 500 stocks
    """
    df_sp500_info = get_SP500_info()
    symbol_list = list(df_sp500_info['Symbol'])
    symbol_list.append(SP500_INDEX_TICKER)
    symbol_count = 0
    for symbol in symbol_list:
        try:
            df_symbol_data = get_data_for_ticker(symbol)
            if store_in_csv:
                logger.debug(f'writing csv for {symbol}')
                filename = get_filename_for_ticker(symbol)
                df_symbol_data.to_csv(filename)
        except:
            logger.error(f'error processing: {symbol}')
        symbol_count += 1

    return symbol_count
