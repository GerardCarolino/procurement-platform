from django.contrib import admin
from .models import Agency, Procurement


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'created_at')
    search_fields = ('name', 'department')


@admin.register(Procurement)
class ProcurementAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'title', 'agency', 'status', 'category', 'approved_budget', 'bid_open_date')
    list_filter = ('status', 'category', 'agency')
    search_fields = ('reference_number', 'title')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')