from django.http import HttpResponse
from rest_framework.decorators import api_view


@api_view(["GET"])
def health(WSGIRequest, **kwargs):
    return HttpResponse(status=200)
