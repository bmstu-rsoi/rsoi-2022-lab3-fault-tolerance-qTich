import json

import requests
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound


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
    params: dict[str, int | float | str] = {},
    data={},
    **url_kwargs: dict[str, str]
):
    return requests.request(
        method=method,
        url=url.format(**url_kwargs),
        headers=headers,
        params=map_kwargs(**params),
        data=data,
    )


def as_JsonResponse(
    request: requests.models.Request = None,
    content: bytes = None,
    status: int = None,
) -> HttpResponse:
    if all(arg is None for arg in (request, content, status)):
        return HttpResponse()
    if content is None:
        content = request.content
    if status is None:
        status = request.status_code
    if not isinstance(content, (dict, list)):
        content = as_json(content)
    content = [remap_kwargs(**obj) for obj in content] if isinstance(content, list) else remap_kwargs(**content)
    return JsonResponse(content, status=status, safe=False)


def redirect_by_url(url: str):
    def wrap(WSGIRequest, /, **url_kwargs: dict[str, str]) -> HttpResponse:
        lrequest = make_request(
            WSGIRequest.method,
            url,
            headers=WSGIRequest.headers,
            params=getattr(
                WSGIRequest,
                "GET" if WSGIRequest.method == "GET" else "POST",
                {}
            ), **url_kwargs,
        )
        return as_JsonResponse(lrequest)
    return wrap


@api_view(["GET", "POST"])
def rating(WSGIRequest, /, **url_kwargs: dict[str, str]) -> HttpResponse:
    return redirect_by_url("http://rating:8050/api/v1/rating")(WSGIRequest, **url_kwargs)


@api_view(["GET"])
def libraries(WSGIRequest, /, **url_kwargs: dict[str, str]) -> HttpResponse:
    return redirect_by_url("http://library:8060/api/v1/libraries")(WSGIRequest, **url_kwargs)


@api_view(["GET"])
def libraries_uuid(WSGIRequest, /, **url_kwargs: dict[str, str]) -> HttpResponse:
    return redirect_by_url("http://library:8060/api/v1/libraries/{library_uid}/")(WSGIRequest, **url_kwargs)


@api_view(["GET"])
def libraries_uuid_books(WSGIRequest, /, **url_kwargs: dict[str, str]) -> HttpResponse:
    return redirect_by_url("http://library:8060/api/v1/libraries/{library_uid}/books")(WSGIRequest, **url_kwargs)


@api_view(["GET"])
def libraries_uuid_books_uuid(WSGIRequest, /, **url_kwargs: dict[str, str]) -> HttpResponse:
    return redirect_by_url("http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/")(
        WSGIRequest, **url_kwargs
    )


def get_reservations(WSGIRequest):
    rv_content = []
    for reservation_data in make_request(
        "get", "http://reservation:8070/api/v1/reservations",
        headers=WSGIRequest.headers, params=WSGIRequest.GET,
    ).json():
        library_instance = make_request(
            "get", "http://library:8060/api/v1/libraries/{library_uid}/",
            headers=WSGIRequest.headers, library_uid=reservation_data.get("library_uid"),
        )
        book_instance = make_request(
            "get", "http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/",
            headers=WSGIRequest.headers,
            library_uid=reservation_data.get("library_uid"),
            book_uid=reservation_data.get("book_uid"),
        )
        rvc = {
            "book": as_json(book_instance.content),
            "library": as_json(library_instance.content),
        }
        rvc.update(reservation_data)
        rv_content.append(rvc)
    return rv_content


def post_reservations(WSGIRequest):
    params = map_kwargs(**as_json(WSGIRequest.body))
    library_uid = params.get("library_uid", None)
    if library_uid is None:
        raise NotFound("\"library_uid\" is missing.")
    book_uid = params.get("book_uid", None)
    if book_uid is None:
        raise NotFound("\"book_uid\" is missing.")
    book_instance = make_request(
        "get", "http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/",
        headers=WSGIRequest.headers, library_uid=library_uid, book_uid=book_uid,
    )
    book_data = as_json(book_instance.content)
    if not book_data.get("available_count", 0):
        raise NotFound("\"available_count\" is 0")
    reservation_instance = make_request(
        "post", "http://reservation:8070/api/v1/reservations",
        headers=WSGIRequest.headers, data=as_bytes(params),
    )
    if reservation_instance.status_code != 201:
        return as_JsonResponse(reservation_instance)
    book_instance = make_request(
        "patch", "http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/",
        headers=WSGIRequest.headers, library_uid=library_uid, book_uid=book_uid,
        data=as_bytes({"available_count": book_data.get("available_count", 0) - 1}),
    )
    if book_instance.status_code != 200:
        raise NotFound("Problem with library.")
    library_instance = make_request(
        "get", "http://library:8060/api/v1/libraries/{library_uid}/",
        headers=WSGIRequest.headers, library_uid=library_uid,
    )
    if library_instance.status_code != 200:
        raise NotFound("Problem with library.")
    rv_content = {
        "book": as_json(book_instance.content),
        "library": as_json(library_instance.content),
    }
    rv_content.update(as_json(reservation_instance.content))
    return rv_content


@api_view(["GET", "POST"])
def reservations(WSGIRequest, /, **url_kwargs: dict[str, str]) -> JsonResponse:
    if WSGIRequest.method == "GET":
        rv_content = get_reservations(WSGIRequest)
    elif WSGIRequest.method == "POST":
        rv_content = post_reservations(WSGIRequest)
    return as_JsonResponse(content=rv_content, status=200)


@api_view(["POST"])
def reservations_uuid_return(WSGIRequest, /, **url_kwargs: dict[str, str]) -> HttpResponse:
    params = map_kwargs(**as_json(WSGIRequest.body))
    if "date" in params:
        params["till_date"] = params["date"]
    if "condition" not in params:
        raise NotFound("\"condition\" is empty")
    if "till_date" not in params:
        raise NotFound("\"till_date\" is empty")
    reservation_instance = make_request(
        "get", "http://reservation:8070/api/v1/reservations/{reservation_uid}/",
        headers=WSGIRequest.headers, **url_kwargs,
    )
    if reservation_instance.status_code != 200:
        raise NotFound("Problem with reservation")
    reservation_data = as_json(reservation_instance.content)
    if reservation_data.get("status") != "RENTED":
        raise NotFound("Reservation is closed.")
    is_expired = reservation_data.get("till_date", "") < params.get("till_date", "")
    reservation_instance = make_request(
        "patch", "http://reservation:8070/api/v1/reservations/{reservation_uid}/return",
        headers=WSGIRequest.headers, data=as_bytes({
            "till_date": params.get("till_date", ""),
            "status": ("EXPIRED" if is_expired else "RETURNED")
        }), **url_kwargs,
    )
    if reservation_instance.status_code != 200:
        raise NotFound("Problem with reservation")
    book_instance = make_request(
        "get", "http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/",
        headers=WSGIRequest.headers,
        library_uid=reservation_data.get("library_uid"),
        book_uid=reservation_data.get("book_uid"),
    )
    book_data = as_json(book_instance.content)
    book_instance = make_request(
        "patch", "http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/",
        headers=WSGIRequest.headers,
        library_uid=reservation_data.get("library_uid"),
        book_uid=reservation_data.get("book_uid"),
        data=as_bytes({"available_count": book_data.get("available_count", 0) + 1}),
    )
    if not is_expired:
        rating_instance = make_request(
            "get", "http://rating:8050/api/v1/rating",
            headers=WSGIRequest.headers,
        )
        if rating_instance.status_code != 200:
            raise NotFound("Problem with rating")
        stars = as_json(rating_instance.content).get("stars", 0)
        rating_instance = make_request(
            "patch", "http://rating:8050/api/v1/rating",
            headers=WSGIRequest.headers,
            data=as_bytes({
                "stars": stars + 1,
            }), **url_kwargs,
        )
        if rating_instance.status_code != 200:
            raise NotFound("Problem with rating")
    return as_JsonResponse(content=b"", status=204)
