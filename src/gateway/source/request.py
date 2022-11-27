import requests


class Response:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class Request:
    def __init__(
        self,
        /, *,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, int | float | str],
        data: dict,
    ):
        self.method = method
        self.url = url
        self.headers = headers
        self.params = params
        self.data = data

    def __repr__(self):
        return f"<{self.__class__.__name__}: ({self.method}, {self.url}, {self.headers}, {self.params}, {self.data}>"

    def execute(self):
        try:
            return requests.request(
                method=self.method,
                url=self.url,
                headers=self.headers,
                params=self.params,
                data=self.data,
            )
        except requests.exceptions.ConnectionError as ex:
            return Response(status_code=503)

