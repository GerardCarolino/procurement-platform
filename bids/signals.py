from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bid


@receiver(post_save, sender=Bid)
def log_bid_saved(sender, instance, created, **kwargs):
    from audit.logger import log_event
    if created:
        log_event(
            event_type='BID_SUBMITTED',
            user=instance.submitted_by,
            object_type='Bid',
            object_id=instance.pk,
            detail=f"Bid submitted for {instance.procurement.reference_number}"
        )