import queue
from threading import Thread

from .request import Request
from .utils import Service


class _Queue:
    def __init__(self):
        self.information = {
            service: queue.Queue() for service in Service
        }

    def put(self, service: Service, item: Request):
        if service in self.information:
            self.information[service].put(item)

    def retry_library(self):
        while True:
            instance = self.information[Service.LIBRARY].get()
            if instance.execute().status_code not in (200, 201):
                self.put(Service.LIBRARY, instance)
            self.information[Service.LIBRARY].task_done()

    def retry_rating(self):
        while True:
            instance = self.information[Service.RATING].get()
            if instance.execute().status_code not in (200, 201):
                self.put(Service.RATING, instance)
            self.information[Service.RATING].task_done()

    def retry_reservation(self):
        while True:
            instance = self.information[Service.RESERVATION].get()
            if instance.execute().status_code not in (200, 201):
                self.put(Service.RESERVATION, instance)
            self.information[Service.RESERVATION].task_done()

    def join(self):
        for q in self.information.values():
            q.join()


Queue = _Queue()
Thread(target=Queue.retry_library, daemon=True).start()
Thread(target=Queue.retry_rating, daemon=True).start()
Thread(target=Queue.retry_reservation, daemon=True).start()
Queue.join()
