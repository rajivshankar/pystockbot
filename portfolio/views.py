from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import pandas as pd

from . import utils

# Create your views here.
def get_portfolio_home(request):
    template = loader.get_template("portfolio_home.html")
    context = {}

    asset_prices = utils.get_analytical_data('AAPL')
    # x = [x for x in asset_prices.index]
    # y = [y for y in asset_prices['adj_close']]
    chart = utils.get_full_plot(asset_prices)
    context['chart'] = chart
    return HttpResponse(template.render(context, request))