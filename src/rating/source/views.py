from collections import OrderedDict

from requests import Response
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer

from .models import RatingModel
from .serializers import RatingSerializer


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


def get_object_based_on_header(self):
    self.kwargs["username"] = self.request.headers.get("X-User-Name")
    return super(self.__class__, self).get_object()


class RatingAPIView(RetrieveAPIView):
    serializer_class = RatingSerializer
    queryset = RatingModel.objects
    renderer_classes = (JSONRenderer,)
    lookup_field = "username"

    get_object = get_object_based_on_header


class IncreaseStarsRatingAPIView(UpdateAPIView):
    serializer_class = RatingSerializer
    queryset = RatingModel.objects
    renderer_classes = (JSONRenderer,)
    lookup_field = "username"

    get_object = get_object_based_on_header

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs and args:
            kwargs["data"]["stars"] = args[0].stars + kwargs["data"].get("stars", 0)
        return super().get_serializer(*args, **kwargs)


class DecreaseStarsRatingAPIView(UpdateAPIView):
    serializer_class = RatingSerializer
    queryset = RatingModel.objects
    renderer_classes = (JSONRenderer,)
    lookup_field = "username"

    get_object = get_object_based_on_header

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs and args:
            kwargs["data"]["stars"] = args[0].stars - kwargs["data"].get("stars", 0)
        return super().get_serializer(*args, **kwargs)
