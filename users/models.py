from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        AGENCY_ADMIN = 'AGENCY_ADMIN', 'Agency Admin'
        VENDOR = 'VENDOR', 'Vendor'
        PUBLIC = 'PUBLIC', 'Public Viewer'

    class VerificationStatus(models.TextChoices):
        PENDING  = 'PENDING',  'Pending'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PUBLIC)
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=255, blank=True)

    @property
    def is_agency_admin(self):
        return self.role == self.Role.AGENCY_ADMIN

    @property
    def is_vendor(self):
        return self.role == self.Role.VENDOR

    @property
    def is_verified_vendor(self):
        return self.role == self.Role.VENDOR and self.is_verified

    def __str__(self):
        return f"{self.username} ({self.role})"