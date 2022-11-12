import uuid

from django.db import models


class ReservationModel(models.Model):
    class StatusChoices(models.TextChoices):
        RENTED = ("RENTED", "Rented")
        RETURNED = ("RETURNED", "Returned")
        EXPIRED = ("EXPIRED", "Expired")

    reservation_uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=80)
    book_uid = models.UUIDField()
    library_uid = models.UUIDField()
    status = models.CharField(
        choices=StatusChoices.choices,
        default=StatusChoices.RENTED,
        max_length=20,
    )
    start_date = models.DateField(auto_now_add=True, editable=False, null=False, blank=False)
    till_date = models.DateField(null=False, blank=False)
