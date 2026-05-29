from django.urls import path
from . import views

app_name = 'procurements'

urlpatterns = [
    # Public
    path('', views.procurement_list, name='list'),
    path('<int:pk>/', views.procurement_detail, name='detail'),

    # Agency Admin
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/new/', views.procurement_create, name='create'),
    path('dashboard/<int:pk>/edit/', views.procurement_edit, name='edit'),
    path('dashboard/<int:pk>/delete/', views.procurement_delete, name='delete'),
]