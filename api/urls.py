from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # Auth
    path('auth/token/',         TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    path('me/',                 views.MeView.as_view(),         name='me'),

    # Procurements
    path('procurements/',              views.ProcurementListView.as_view(),   name='procurement_list'),
    path('procurements/<int:pk>/',     views.ProcurementDetailView.as_view(), name='procurement_detail'),

    # Bids
    path('procurements/<int:pk>/bids/',        views.BidListView.as_view(),   name='bid_list'),
    path('procurements/<int:pk>/bids/submit/', views.BidSubmitView.as_view(), name='bid_submit'),
    path('bids/mine/',                         views.MyBidsView.as_view(),    name='my_bids'),

    # Awards
    path('awards/', views.AwardListView.as_view(), name='award_list'),
]