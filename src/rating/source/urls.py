from django.urls import path

from .views import RatingAPIView

urlpatterns = [
    path(
        "rating", RatingAPIView.as_view(),
    ),
]
