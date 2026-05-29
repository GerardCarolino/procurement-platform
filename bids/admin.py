from django.contrib import admin
from .models import Bid, Award


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('procurement', 'submitted_by', 'status', 'submitted_at', 'amount_display')
    list_filter = ('status', 'procurement__agency')
    search_fields = ('submitted_by__username', 'procurement__reference_number')
    list_editable = ('status',)
    readonly_fields = ('submitted_at', 'updated_at')

    def amount_display(self, obj):
        if obj.is_amount_visible():
            return f"₱{obj.bid_amount:,.2f}"
        return "🔒 Sealed"
    amount_display.short_description = 'Bid Amount'


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('procurement', 'winning_bid', 'awarded_by', 'award_date')
    readonly_fields = ('award_date',)