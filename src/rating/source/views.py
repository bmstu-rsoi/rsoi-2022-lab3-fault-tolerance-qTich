from collections import OrderedDict

from requests import Response
from rest_framework.generics import RetrieveUpdateAPIView
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


class RatingAPIView(RetrieveUpdateAPIView):
    serializer_class = RatingSerializer
    queryset = RatingModel.objects
    renderer_classes = (JSONRenderer,)
    lookup_field = "username"

    def get_object(self):
        self.kwargs["username"] = self.request.headers.get("X-User-Name")
        return super().get_object()
