from django.urls import path

from .views import ReservationAPIView, ReservationUUIDAPIView, ReturnReservationAPIView

urlpatterns = [
    path(
        "reservations", ReservationAPIView.as_view(),
    ), path(
        "reservations/<uuid:reservation_uid>/", ReservationUUIDAPIView.as_view(),
    ), path(
        "reservations/<uuid:reservation_uid>/return", ReturnReservationAPIView.as_view(),
    ),
]
