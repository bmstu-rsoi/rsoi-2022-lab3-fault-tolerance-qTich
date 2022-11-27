from django.urls import path

from .views import (
    RatingAPIView, IncreaseStarsRatingAPIView, DecreaseStarsRatingAPIView
)

urlpatterns = [
    path(
        "rating", RatingAPIView.as_view(),
    ), path(
        "rating/increase", IncreaseStarsRatingAPIView.as_view(),
    ), path(
        "rating/decrease", DecreaseStarsRatingAPIView.as_view(),
    )
]
