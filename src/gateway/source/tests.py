from django.test import TestCase
from django.test.client import Client


class GatewayTestCase(TestCase):

    def test_get_rating(self):
        client = Client(HTTP_X_USER_NAME="Test Max")
        response_instance = client.get(
            "http://rating:8050/api/v1/rating"
        )
        self.assertEqual(response_instance.status_code, 200)
        self.assertEqual(response_instance.json().get("stars", 0), 75)

    def test_get_libraries(self):
        client = Client()
        response_instance = client.get(
            "http://library:8060/api/v1/libraries"
        )
        self.assertEqual(response_instance.status_code, 200)
        self.assertIsInstance(response_instance.json(), list)

    def test_get_libraries_83575e12_7ce0_48ee_9931_51919ff3c9ee(self):
        client = Client()
        response_instance = client.get(
            "http://library:8060/api/v1/libraries/83575e12-7ce0-48ee-9931-51919ff3c9ee"
        )
        self.assertEqual(response_instance.status_code, 200)
        response_data = response_instance.json()
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data.get("name"), "Библиотека имени 7 Непьющих")
        self.assertEqual(response_data.get("city"), "Москва")
        self.assertEqual(response_data.get("name"), "2-я Бауманская ул., д.5, стр.1")
        self.assertIsInstance(response_data.get("books"), list)

    def test_get_libraries_83575e12_7ce0_48ee_9931_51919ff3c9ee_books_f7cdc58f_2caf_4b15_9727_f89dcc629b27(self):
        client = Client()
        response_instance = client.get(
            "http://library:8060/api/v1/libraries/83575e12-7ce0-48ee-9931-51919ff3c9ee/"
            "books/f7cdc58f-2caf-4b15-9727-f89dcc629b27/"
        )
        self.assertEqual(response_instance.status_code, 200)
        response_data = response_instance.json()
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data.get("name"), "Краткий курс C++ в 7 томах")
        self.assertEqual(response_data.get("author"), "Бьерн Страуструп")
        self.assertEqual(response_data.get("genre"), "Научная фантастика")
        self.assertIsInstance(response_data.get("condition"), "EXCELLENT")
