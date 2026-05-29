from django.db import models
from users.models import CustomUser
from procurements.models import Procurement


class BidManager(models.Manager):
    def visible_to(self, user, procurement):
        from django.utils import timezone
        qs = self.filter(procurement=procurement)
        if user.is_agency_admin:
            return qs
        return qs.filter(submitted_by=user)


class Bid(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_EVALUATION = 'UNDER_EVALUATION', 'Under Evaluation'
        AWARDED = 'AWARDED', 'Awarded'
        REJECTED = 'REJECTED', 'Rejected'

    procurement = models.ForeignKey(
        Procurement, on_delete=models.PROTECT, related_name='bids'
    )
    submitted_by = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name='bids'
    )
    bid_amount = models.DecimalField(max_digits=15, decimal_places=2)
    technical_proposal = models.TextField()
    supporting_document = models.FileField(
        upload_to='bid_documents/', blank=True, null=True
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SUBMITTED
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BidManager()

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('procurement', 'submitted_by')

    def __str__(self):
        return f"Bid by {self.submitted_by.organization} on {self.procurement.reference_number}"

    def is_amount_visible(self):
        from django.utils import timezone
        return timezone.now() >= self.procurement.bid_open_date


class Award(models.Model):
    procurement = models.OneToOneField(
        Procurement, on_delete=models.PROTECT, related_name='award'
    )
    winning_bid = models.OneToOneField(
        Bid, on_delete=models.PROTECT, related_name='award'
    )
    awarded_by = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name='awards_made'
    )
    award_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Award: {self.procurement.reference_number} → {self.winning_bid.submitted_by.organization}"