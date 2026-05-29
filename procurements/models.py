from django.db import models
from users.models import CustomUser


class Agency(models.Model):
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Agencies'
        ordering = ['name']

    def __str__(self):
        return self.name


class Procurement(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'
        AWARDED = 'AWARDED', 'Awarded'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class Category(models.TextChoices):
        INFRASTRUCTURE = 'INFRASTRUCTURE', 'Infrastructure'
        IT_SYSTEMS = 'IT_SYSTEMS', 'IT & Systems'
        MEDICAL = 'MEDICAL', 'Medical'
        CONSULTING = 'CONSULTING', 'Consulting'
        SUPPLIES = 'SUPPLIES', 'Supplies'
        OTHER = 'OTHER', 'Other'

    reference_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, related_name='procurements')
    posted_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='procurements')
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.OTHER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    approved_budget = models.DecimalField(max_digits=15, decimal_places=2)
    bid_open_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} — {self.title}"

    def is_open(self):
        from django.utils import timezone
        return self.status == self.Status.OPEN and timezone.now() < self.bid_open_date

    def is_sealed(self):
        from django.utils import timezone
        return timezone.now() < self.bid_open_date