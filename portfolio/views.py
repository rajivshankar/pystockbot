from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import pandas as pd

# Create your views here.
def get_portfolio_home(request):
    template = loader.get_template("portfolio_home.html")
    context = {}
    return HttpResponse(template.render(context, request))