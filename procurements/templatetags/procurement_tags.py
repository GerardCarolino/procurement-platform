from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def format_currency(value):
    try:
        return f"₱{value:,.2f}"
    except (TypeError, ValueError):
        return value


@register.simple_tag
def bid_countdown(bid_open_date):
    now = timezone.now()
    if now >= bid_open_date:
        return "Bids opened"
    delta = bid_open_date - now
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    if days > 0:
        return f"{days}d {hours}h left"
    elif hours > 0:
        return f"{hours}h {minutes}m left"
    else:
        return f"{minutes}m left"