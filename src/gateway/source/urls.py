from django.urls import path

from .views import rating, libraries, libraries_uuid, libraries_uuid_books, reservations, reservations_uuid_return

urlpatterns = [
    path(
        "rating", rating,
    ),  path(
        "libraries", libraries,
    ), path(
        "libraries/<uuid:library_uid>/", libraries_uuid,
    ), path(
        "libraries/<uuid:library_uid>/books", libraries_uuid_books,
    ), path(
        "reservations", reservations,
    ), path(
        "reservations/<uuid:reservation_uid>/return", reservations_uuid_return,
    )
]
