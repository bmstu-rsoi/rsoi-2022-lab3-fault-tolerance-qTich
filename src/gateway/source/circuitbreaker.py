import enum
import time


class Service(enum.Enum):
    LIBRARY = 1
    RATING = 2
    RESERVATION = 3


class _CircuitBreaker:
    def __init__(
        self,
        /,
        max_fails: int = 5,
        delay: float | int = 55,
    ):
        self.max_fails = max_fails
        self.delay = delay
        self.information = {
            service: {
                "fails": 0,
                "await": 0,
            } for service in Service
        }

    def is_overflow(self, service: Service) -> bool:
        return self.max_fails < self.information.get(service, {}).get("fails", 0)

    def is_failed(self, service: Service) -> bool:
        return not not self.information.get(service, {}).get("fails", 0)

    def should_raise(self, service: Service) -> bool:
        return self.is_overflow(service) \
               and self.delay > self.information.get(service, {}).get("await", 0) - time.time()

    def on_failure(self, service: Service):
        self.information.get(service, {})["await"] = time.time()
        if not self.is_overflow(service):
            self.information.get(service, {})["fails"] += 1

    def on_ok(self, service: Service):
        self.information.get(service, {})["fails"] = 0


CircuitBreaker = _CircuitBreaker()
