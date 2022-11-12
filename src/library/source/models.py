import uuid

from django.db import models


class BookModel(models.Model):
    class ConditionChoices(models.TextChoices):
        EXCELLENT = ("EXCELLENT", "Excellent")
        GOOD = ("GOOD", "Good")
        BAD = ("BAD", "Bad")

    book_uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    condition = models.CharField(
        choices=ConditionChoices.choices,
        default=ConditionChoices.EXCELLENT,
        max_length=20,
    )


class LibraryModel(models.Model):
    library_uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=80)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    books = models.ManyToManyField(
        BookModel,
        through="BookLibraryModel",
    )


class BookLibraryModel(models.Model):
    book_id = models.ForeignKey(BookModel, on_delete=models.CASCADE, related_name="book")
    library_id = models.ForeignKey(LibraryModel, on_delete=models.CASCADE, related_name="library")
    available_count = models.PositiveIntegerField()
