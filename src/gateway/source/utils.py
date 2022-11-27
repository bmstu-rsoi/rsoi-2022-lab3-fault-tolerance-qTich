import requests
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from rest_framework import status as status_codes
from rest_framework.exceptions import APIException
from rest_framework.utils import json

from .circuitbreaker import (
    Service, CircuitBreaker,
)
from .queue import Queue
from .request import Request


def as_json(
    content: bytes | str
):
    return json.loads(content or "{}")


def as_bytes(
    content: dict[str, int | float | str]
):
    return json.dumps(content, cls=DjangoJSONEncoder)


def map_kwargs(**url_kwargs: dict[str, str]) -> dict[str, str]:
    """
    Add `_` before upper case char.
    :param url_kwargs:
    :return:
    """
    return {
        key: v for k, v in url_kwargs.items()
        if (key := "".join(
                char for c in k
                if (char := (c if c.islower() else "_" + c.lower()))
           )
        )
    }


def remap_kwargs(**kwargs) -> dict[str, str]:
    """
    Capitalize char after `_`.
    :param kwargs:
    :return:
    """
    return {
        (
            k if index == -1 else k[:index] + k[index + 1:].capitalize()
        ): (
            remap_kwargs(**v) if isinstance(v, dict) else [remap_kwargs(**d) if isinstance(d, dict) else d for d in v]
            if isinstance(v, list) else v
        ) for k, v in kwargs.items() if (index := k.find("_"))
    }


def make_request(
    method: str,
    url: str,
    /, *,
    headers: dict[str, str],
    params: dict[str, int | float | str] = None,
    data: dict = None,
    **url_kwargs: dict[str, str],
) -> Request:
    params = {} if params is None else params
    data = {} if data is None else data
    return Request(
        method=method,
        url=url.format(**url_kwargs),
        headers=headers,
        params=map_kwargs(**params),
        data=data,
    )


def as_JsonResponse(
    response: requests.models.Response = None,
    content: bytes | dict | list = None,
    status: int = None,
) -> JsonResponse:
    if all(arg is None for arg in (response, content, status)):
        return JsonResponse()
    if content is None:
        content = response.content
    if status is None:
        status = response.status_code
    if not isinstance(content, (dict, list)):
        content = as_json(content)
    content = [remap_kwargs(**obj) for obj in content] if isinstance(content, list) else remap_kwargs(**content)
    return JsonResponse(content, status=status, safe=False)


def get_request_instance(url: str, WSGIRequest, **url_kwargs):
    return make_request(
        url_kwargs.pop("method", WSGIRequest.method),
        url,
        headers=url_kwargs.pop("headers", WSGIRequest.headers),
        params=url_kwargs.pop("params", getattr(
            WSGIRequest,
            "GET" if WSGIRequest.method == "GET" else "POST",
            {}
        )),
        data=url_kwargs.pop("data", {}),
        **url_kwargs,
    )


class ServiceUnAvailable(APIException):
    status_code = status_codes.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service is unavailable.'
    default_code = 'service_unavailable'


def request_error(request, *args, detail=None, **kwargs):
    data = {
        "error": "Service is unavailable."
    } if detail is None else detail
    return as_JsonResponse(
        content=data,
        status=status_codes.HTTP_503_SERVICE_UNAVAILABLE,
    )


def validate_on_cb(
    service: Service, url: str, on_unavailable: dict | list | str, shielding: dict = {}, as_method: str = None
):
    def upper(func):
        def wrap(
            WSGIRequest, /, *, in_json: bool = True, query_params: dict = None, **url_kwargs: dict[str, str]
        ) -> JsonResponse | Request:
            if CircuitBreaker.should_raise(service):
                return request_error(WSGIRequest, detail=on_unavailable)
            params = query_params if query_params is not None else {}
            params.update(**map_kwargs(**as_json(WSGIRequest.body)))
            params = {
                shielding.get(key, key): value
                for key, value in params.items()
            }
            request_instance = get_request_instance(
                url, WSGIRequest, data=as_bytes(params),
                method=as_method or url_kwargs.pop("method", WSGIRequest.method),
                **url_kwargs
            )
            if not in_json:
                return request_instance
            if (rq := request_instance.execute()).status_code not in (200, 201):
                if request_instance.method in ("POST", "PUT", "PATCH"):
                    Queue.put(service, request_instance)
                CircuitBreaker.on_failure(service)
                return request_error(WSGIRequest, detail=on_unavailable)
            CircuitBreaker.on_ok(service)
            if func is None:
                return as_JsonResponse(rq)
            return func(WSGIRequest, as_JsonResponse(rq), params)
        return wrap
    return upper


def validate_on_cb_with(service: Service, url: str, before: dict, on: dict, on_unavailable: dict | list | str):
    def upper(func):
        def wrap(WSGIRequest, /, *, in_json: bool = True, **url_kwargs: dict[str, str]) -> JsonResponse | Request:
            for key, value in before.items():
                r = validate_on_cb(
                    value.get("service"), value.get("url"), value.get("on_unavailable")
                )(None)(WSGIRequest, in_json=in_json, method="GET", **url_kwargs)
                if r.status_code not in (200, 201):
                    return r
            return validate_on_cb(
                service, url, on_unavailable.get(WSGIRequest.method)
            )(on.get(WSGIRequest.method))(WSGIRequest, in_json=in_json, **url_kwargs)
        return wrap
    return upper
