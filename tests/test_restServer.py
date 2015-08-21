from tornado.testing import AsyncHTTPTestCase
from sound_sync.rest_server.server import RestServer
import json
import urllib


class ServerTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return RestServer().get_app()

    def assertError(self, response, error_code=500):
        self.assertEqual(response.code, error_code)

    def assertResponse(self, response, content=None):
        self.assertEqual(response.code, 200)
        if content is not None:
            self.assertEqual(response.body, content)
        else:
            return response.body


class TestChannelListFromServer(ServerTestCase):
    def test_get_channels(self):
        response = self.fetch('/channels/get')
        self.assertResponse(response, "{}")

    def test_set_channel_properties(self):
        response = self.fetch('/channels/add')
        item_hash = self.assertResponse(response)

        parameters = {"name": "My New Name", "description": "This is a description. It <strong>even</strong>" +
                                                            "have some html tags."}
        body = urllib.urlencode(parameters)

        response = self.fetch('/channels/set/' + str(item_hash), method="POST", body=body)
        self.assertResponse(response, "")

        response = self.fetch('/channels/set/' + str(item_hash + "1"), method="POST", body=body)
        self.assertError(response)

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        added_channel = response_dict[item_hash]

        self.assertEqual(added_channel["name"], "My New Name")
        self.assertEqual(added_channel["item_hash"], item_hash)
        self.assertEqual(added_channel["description"], "This is a description. It <strong>even</strong>" +
                         "have some html tags.")

    def test_add_channels(self):
        response = self.fetch('/channels/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 1)

        added_channel = response_dict[item_hash]

        self.assertEqual(type(added_channel), dict)
        self.assertIn("start_time", added_channel)
        self.assertIn("name", added_channel)
        self.assertEqual(added_channel["name"], "")

        self.assertIn("item_hash", added_channel)
        self.assertEqual(added_channel["item_hash"], item_hash)

        self.assertIn("description", added_channel)
        self.assertEqual(added_channel["description"], "")

        self.assertIn("now_playing", added_channel)
        self.assertEqual(added_channel["now_playing"], "")

        self.assertEqual(len(added_channel), 5)

        response = self.fetch('/channels/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 2)

    def test_delete_channels(self):
        response = self.fetch('/channels/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/channels/delete/' + item_hash)
        self.assertResponse(response, "")

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertEqual(len(response_dict), 0)

        response = self.fetch('/channels/delete/' + item_hash)
        self.assertError(response)


class TestClientListFromServer(ServerTestCase):
    def test_get_clients(self):
        response = self.fetch('/clients/get')
        self.assertResponse(response, "{}")

    def test_set_clients_properties(self):
        response = self.fetch('/clients/add')
        item_hash = self.assertResponse(response)

        parameters = {"name": "My New Name", "ip_address": "111.111.222.333"}
        body = urllib.urlencode(parameters)

        response = self.fetch('/clients/set/' + str(item_hash), method="POST", body=body)
        self.assertResponse(response, "")

        response = self.fetch('/clients/set/' + str(item_hash + "1"), method="POST", body=body)
        self.assertError(response)

        response = self.fetch('/clients/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        added_channel = response_dict[item_hash]

        self.assertEqual(added_channel["name"], "My New Name")
        self.assertEqual(added_channel["item_hash"], item_hash)
        self.assertEqual(added_channel["ip_address"], "111.111.222.333")

    def test_add_clients(self):
        response = self.fetch('/clients/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/clients/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 1)

        added_client = response_dict[item_hash]

        self.assertEqual(type(added_client), dict)
        self.assertIn("login_time", added_client)
        self.assertIn("name", added_client)
        self.assertEqual(added_client["name"], "")

        self.assertIn("item_hash", added_client)
        self.assertEqual(added_client["item_hash"], item_hash)

        self.assertIn("ip_address", added_client)
        self.assertEqual(added_client["ip_address"], "None")

        self.assertEqual(len(added_client), 4)

        response = self.fetch('/clients/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/clients/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 2)

    def test_delete_clients(self):
        response = self.fetch('/clients/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/clients/delete/' + item_hash)
        self.assertResponse(response, "")

        response = self.fetch('/clients/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertEqual(len(response_dict), 0)

        response = self.fetch('/clients/delete/' + item_hash)
        self.assertError(response)


class TestRestServer(ServerTestCase):
    def test_main(self):
        response = self.fetch('/')
        self.assertError(response)

    def test_unused_action(self):
        response = self.fetch("/channels/foo")
        self.assertError(response)

        parameter = {"test": "test"}
        body = urllib.urlencode(parameter)
        response = self.fetch("/channels/foo/1", method="POST", body=body)
        self.assertError(response, 500)

        response = self.fetch("/clients/foo")
        self.assertError(response)

        parameter = {"test": "test"}
        body = urllib.urlencode(parameter)
        response = self.fetch("/clients/foo/1", method="POST", body=body)
        self.assertError(response, 500)
