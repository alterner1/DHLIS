# тестирование производительности с помощью сервиса locust 
from locust import HttpUser, task, between
import xmlrpc.client
import time

class XmlRpcUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def search_students(self):
        start_time = time.time()  # Начало замера времени
        try:
            proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
            proxy.search_students({"gender": "мужской"}, "age", "desc", 1, 5)
            response_time = int((time.time() - start_time) * 1000)  # Время в мс
            self.environment.events.request.fire(
                request_type="XMLRPC",
                name="search_students",
                response_time=response_time,
                response_length=0,
                exception=None  # Успех
            )
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="XMLRPC",
                name="search_students",
                response_time=response_time,
                response_length=0,
                exception=e  # Ошибка
            )