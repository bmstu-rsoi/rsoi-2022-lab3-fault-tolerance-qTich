from collections import OrderedDict

import django_filters
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .serializers import (
    BookLibrarySerializer,
    LibrarySerializer,
    LibraryWithoutBooksSerializer,
    BookUUIDLibraryUUIDSerializer,
)
from .models import BookLibraryModel, LibraryModel

from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_size = None
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total_elements', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page', self.page.number),
            ('page_size', self.page.paginator.per_page),
            ('items', data)
        ]))


class LibraryAllAPIView(ListAPIView):
    serializer_class = LibraryWithoutBooksSerializer
    queryset = LibraryModel.objects
    renderer_classes = (JSONRenderer,)
    pagination_class = Pagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = "__all__"


class LibraryUUIDAPIView(RetrieveAPIView):
    serializer_class = LibrarySerializer
    queryset = LibraryModel.objects
    renderer_classes = (JSONRenderer,)
    lookup_field = "library_uid"


class BookLibraryUUIDAPIView(ListAPIView):
    serializer_class = BookLibrarySerializer
    queryset = BookLibraryModel.objects
    renderer_classes = (JSONRenderer,)
    lookup_field = "library_uid"
    pagination_class = Pagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = "__all__"

    def get_queryset(self):
        queryset = super().get_queryset()
        if "False" in self.request.query_params.get("showAll", "False").capitalize():
            queryset = queryset.filter(available_count__gt=0)
        return queryset


class BookUUIDLibraryUUIDAPIView(RetrieveUpdateAPIView):
    serializer_class = BookUUIDLibraryUUIDSerializer
    queryset = BookLibraryModel.objects
    renderer_classes = (JSONRenderer,)
    lookup_field = ("library_id__library_uid", "book_id__book_uid",)

    def get_object(self):
        """
        Override for working with multiple fields in `lookup_field`.
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset())
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert all(k in self.kwargs for k in self.lookup_field), (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {
            k: self.kwargs.get(k) for k in self.lookup_field
        }
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj
