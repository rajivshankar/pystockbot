from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_portfolio_home, name="portfolio_home")
]
