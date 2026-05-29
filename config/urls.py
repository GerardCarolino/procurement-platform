from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',       admin.site.urls),
    path('accounts/',    include('users.urls')),
    path('',             include('procurements.urls')),
    path('',             include('bids.urls')),
    path('api/',         include('api.urls')),
    path('admin-panel/', include('users.urls_admin')),
]