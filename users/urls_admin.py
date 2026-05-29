from django.urls import path
from . import views

urlpatterns = [
    # Vendor panel
    path('',                    views.vendor_admin_panel, name='vendor_admin_panel'),
    path('<int:pk>/verify/',    views.vendor_verify,      name='vendor_verify'),
    path('<int:pk>/reject/',    views.vendor_reject,      name='vendor_reject'),
    path('<int:pk>/revoke/',    views.vendor_revoke,      name='vendor_revoke'),
    path('<int:pk>/delete/',    views.vendor_delete,      name='vendor_delete'),

    # Agency panel
    path('agencies/',                   views.agency_admin_panel, name='agency_admin_panel'),
    path('agencies/create/',            views.agency_create,      name='agency_create'),
    path('agencies/<int:pk>/edit/',     views.agency_edit,        name='agency_edit'),
    path('agencies/<int:pk>/delete/',   views.agency_delete,      name='agency_delete'),
]