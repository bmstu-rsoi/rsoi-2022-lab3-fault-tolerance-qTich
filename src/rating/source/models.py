from django.core.validators import MaxValueValidator
from django.db import models


class RatingModel(models.Model):
    username = models.CharField(max_length=80)
    stars = models.PositiveSmallIntegerField(
        validators=(MaxValueValidator(100),), default=0,
    )
