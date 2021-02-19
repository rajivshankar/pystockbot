from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import pandas as pd

from . import data_collection as dc
from . import controller


# Create your views here.
def save_all_sp500_metadata(request):
    num_updated = controller.update_asset_data_for_sp500()
    template = loader.get_template('status.html')
    context = {
        'status': f'Successfully loaded {num_updated} records of S&P 500',
    }
    return HttpResponse(template.render(context, request))


def save_all_sp500_stock_prices(request):
    num_tickers, num_records = controller.update_asset_price_data_for_sp500()
    template = loader.get_template('status.html')
    context = {
        'status': f'Successfully loaded {num_records} price points for {num_tickers} tickers of S&P 500',
    }
    return HttpResponse(template.render(context, request))