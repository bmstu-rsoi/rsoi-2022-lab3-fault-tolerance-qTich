from django.http import JsonResponse
from rest_framework.decorators import api_view

from .utils import (
    as_json, map_kwargs,
    as_JsonResponse,
    validate_on_cb, validate_on_cb_with,
)

from .request import Request

from .circuitbreaker import (
    Service
)


@api_view(["GET"])
@validate_on_cb(
    service=Service.RATING, url="http://rating:8050/api/v1/rating",
    on_unavailable={"message": "Bonus Service unavailable"},
)
def rating(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@validate_on_cb(
    service=Service.RATING, url="http://rating:8050/api/v1/rating/increase", on_unavailable={}
)
def rating_increase(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@validate_on_cb(
    service=Service.RATING, url="http://rating:8050/api/v1/rating/decrease", on_unavailable={}
)
def rating_decrease(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@api_view(["GET"])
@validate_on_cb(
    service=Service.LIBRARY, url="http://library:8060/api/v1/libraries", on_unavailable=[]
)
def libraries(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@api_view(["GET"])
@validate_on_cb(
    service=Service.LIBRARY, url="http://library:8060/api/v1/libraries/{library_uid}/", on_unavailable={}
)
def libraries_uuid(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@validate_on_cb(
    service=Service.LIBRARY, url="http://library:8060/api/v1/libraries/{library_uid}/", on_unavailable={}
)
def libraries_uuid_no_view(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@api_view(["GET"])
@validate_on_cb(
    service=Service.LIBRARY, url="http://library:8060/api/v1/libraries/{library_uid}/books", on_unavailable={}
)
def libraries_uuid_books(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@api_view(["GET"])
@validate_on_cb(
    service=Service.LIBRARY,
    url="http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/", on_unavailable={}
)
def libraries_uuid_books_uuid(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@validate_on_cb(
    service=Service.LIBRARY,
    url="http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/", on_unavailable={}
)
def libraries_uuid_books_uuid_no_view(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@validate_on_cb(
    service=Service.LIBRARY,
    url="http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/take",
    on_unavailable={}
)
def libraries_uuid_books_uuid_take(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


@validate_on_cb(
    service=Service.LIBRARY,
    url="http://library:8060/api/v1/libraries/{library_uid}/books/{book_uid}/return",
    on_unavailable={}
)
def libraries_uuid_books_uuid_return(
    WSGIRequest, instance: JsonResponse | Request, params: dict
) -> JsonResponse | Request:
    return instance


def get_reservations(WSGIRequest, instance: JsonResponse | Request, params: dict) -> JsonResponse | Request:
    rv_content = []
    for reservation_data in [map_kwargs(**kv) for kv in as_json(instance.content)]:
        library_instance = libraries_uuid_no_view(
            WSGIRequest, method="GET",
            library_uid=reservation_data.get("library_uid"),
            on_unavailable=rv_content,
        )
        book_instance = libraries_uuid_books_uuid_no_view(
            WSGIRequest, method="GET",
            library_uid=reservation_data.get("library_uid"), book_uid=reservation_data.get("book_uid"),
            on_unavailable=rv_content,
        )
        rvc = {"book": as_json(book_instance.content), "library": as_json(library_instance.content)}
        rvc.update(reservation_data)
        rv_content.append(rvc)
    return as_JsonResponse(content=rv_content, status=instance.status_code)


def post_reservations(WSGIRequest, instance: JsonResponse | Request, params: dict) -> JsonResponse | Request:
    book_instance = libraries_uuid_books_uuid_take(
        WSGIRequest, method="PATCH",
        library_uid=params.get("library_uid", None),
        book_uid=params.get("book_uid", None),
        on_unavailable=params, available_count=1,
    )
    rv_content = {
        "book": as_json(book_instance.content),
        "library": {},
    }
    library_instance = libraries_uuid_no_view(
        WSGIRequest, method="GET",
        library_uid=params.get("library_uid", None),
        on_unavailable=rv_content,
    )
    rv_content["library"] = as_json(library_instance.content)
    rv_content.update(as_json(instance.content))
    return as_JsonResponse(content=rv_content, status=200)


@api_view(["GET", "POST"])
@validate_on_cb_with(
    service=Service.RESERVATION,
    url="http://reservation:8070/api/v1/reservations",
    before={
        "GET": {
            "service": Service.RATING,
            "url": "http://rating:8050/api/v1/rating",
            "on_unavailable": {"message": "Bonus Service unavailable"}
        },
    },
    on={"GET": get_reservations, "POST": post_reservations},
    on_unavailable={"GET": [], "POST": {}}
)
def reservations(WSGIRequest, instance: JsonResponse | Request, params: dict) -> JsonResponse | Request:
    return instance


@api_view(["GET"])
@validate_on_cb(
    service=Service.RESERVATION,
    url="http://reservation:8070/api/v1/reservations/{reservation_uid}/", on_unavailable={}
)
def reservations_uuid(WSGIRequest, instance: JsonResponse | Request, params: dict) -> JsonResponse | Request:
    return instance


@api_view(["POST"])
@validate_on_cb(
    service=Service.RESERVATION,
    url="http://reservation:8070/api/v1/reservations/{reservation_uid}/return",
    on_unavailable={}, shielding={"date": "till_date"},
    as_method="PATCH",
)
def reservations_uuid_return(WSGIRequest, instance: JsonResponse | Request, params: dict) -> JsonResponse | Request:
    reservation_data = as_json(instance.content)
    is_expired = reservation_data.get("status") == "EXPIRED"
    book_instance = libraries_uuid_books_uuid_return(
        WSGIRequest, method="PATCH",
        library_uid=reservation_data.get("library_uid"),
        book_uid=reservation_data.get("book_uid"),
        query_params={"available_count": 1},
    )
    if not is_expired:
        rating_increase(
            WSGIRequest, method="PATCH",
            on_unavailable={"message": "Bonus Service unavailable"}, query_params={"stars": 1}
        )
    elif is_expired:
        rating_decrease(
            WSGIRequest, method="PATCH",
            on_unavailable={"message": "Bonus Service unavailable"}, query_params={"stars": 10}
        )
    if as_json(book_instance.content).get("condition") != reservation_data.get("condition"):
        rating_decrease(
            WSGIRequest, method="PATCH",
            on_unavailable={"message": "Bonus Service unavailable"}, query_params={"stars": 10}
        )
    return as_JsonResponse(content=b"", status=204)
