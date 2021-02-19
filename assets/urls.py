from django.urls import path

from . import views

urlpatterns = [
    path('sp500_meta', views.save_all_sp500_metadata, name='sp_meta'),
    path('sp500_prices', views.save_all_sp500_stock_prices, name='sp500_stock_prices'),
    # path('articles/<int:year>/', views.year_archive),
    # path('articles/<int:year>/<int:month>/', views.month_archive),
    # path('articles/<int:year>/<int:month>/<slug:slug>/', views.article_detail),
]
