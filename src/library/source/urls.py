from django.urls import path

from .views import (
    BookLibraryUUIDAPIView,
    BookUUIDLibraryUUIDAPIView, TakeBookUUIDLibraryUUIDAPIView, ReturnBookUUIDLibraryUUIDAPIView,
    LibraryAllAPIView,
    LibraryUUIDAPIView,
)

urlpatterns = [
    path(
        "libraries",
        LibraryAllAPIView.as_view(),
    ), path(
        "libraries/<uuid:library_uid>/",
        LibraryUUIDAPIView.as_view(),
    ), path(
        "libraries/<uuid:library_uid>/books",
        BookLibraryUUIDAPIView.as_view(),
    ), path(
        "libraries/<uuid:library_id__library_uid>/books/<uuid:book_id__book_uid>/",
        BookUUIDLibraryUUIDAPIView.as_view(),
    ), path(
        "libraries/<uuid:library_id__library_uid>/books/<uuid:book_id__book_uid>/take",
        TakeBookUUIDLibraryUUIDAPIView.as_view(),
    ), path(
        "libraries/<uuid:library_id__library_uid>/books/<uuid:book_id__book_uid>/return",
        ReturnBookUUIDLibraryUUIDAPIView.as_view(),
    ),
]
