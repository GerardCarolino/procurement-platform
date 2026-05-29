from django.urls import path
from . import views

app_name = 'bids'

urlpatterns = [
    path('bids/submit/', views.submit_bid, name='submit'),
    path('bids/mine/', views.my_bids, name='my_bids'),
    path('bids/all/', views.all_bids, name='all_bids'),
    path('bids/awarded/', views.awarded_contracts, name='awarded'),
    path('bids/<int:bid_pk>/award/', views.award_bid, name='award'),
]