import random
from tornado.web import RequestHandler
from sound_sync.buffer_list import BufferList

NOT_SUPPORTED_ERROR_CODE = 501
KEY_ERROR_CODE = 502
BUFFER_ERROR_CODE = 502

class ErrorHandler(RequestHandler):
    def get(self):
        self.send_error(NOT_SUPPORTED_ERROR_CODE)


class BufferHandler(RequestHandler):
    # noinspection PyMethodOverriding,PyAttributeOutsideInit
    def initialize(self, buffer_list, channel_list):
        self.buffer_list = buffer_list
        self.channel_list = channel_list

    def get(self, channel_hash, action, buffer_number):
        if channel_hash not in self.channel_list:
            self.send_error(KEY_ERROR_CODE)

        if action == "get":
            try:
                correct_buffer_list = self.buffer_list[channel_hash]
                buffer_content = correct_buffer_list.get_buffer_by_buffer_index(buffer_number)
                self.write(buffer_content.encode_json())
            except KeyError:
                self.send_error(BUFFER_ERROR_CODE)

        else:
            self.send_error(NOT_SUPPORTED_ERROR_CODE)

    def post(self, channel_hash, action):
        if channel_hash not in self.channel_list:
            self.send_error(KEY_ERROR_CODE)

        if action == "add_buffer":

            if channel_hash not in self.buffer_list:
                self.buffer_list.update({channel_hash: BufferList()})

            buffer_content = self.get_argument("buffer")
            next_buffer_number = self.buffer_list[channel_hash].add_buffer(buffer_content)
            self.write(next_buffer_number)

        else:
            self.send_error(NOT_SUPPORTED_ERROR_CODE)


class ListHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(ListHandler, self).__init__(application, request, **kwargs)

    # noinspection PyMethodOverriding,PyAttributeOutsideInit
    def initialize(self, item_type, item_list):
        self.item_type = item_type
        self.item_list = item_list

    def get(self, action, list_hash=None):
        if action == "add":
            new_hash = int(random.getrandbits(10))
            self.item_list.update({new_hash: self.item_type(new_hash)})

            self.write(str(new_hash))
        elif action == "delete":
            list_hash = int(list_hash)

            if list_hash in self.item_list:
                del self.item_list[list_hash]
                self.write("")
            else:
                self.send_error(KEY_ERROR_CODE)
        elif action == "get":
            self.write({item_hash: list_item.encode_json() for item_hash, list_item in self.item_list.iteritems()})

        else:
            self.send_error(NOT_SUPPORTED_ERROR_CODE)

    def post(self, action, list_hash):
        if action == "set":
            list_hash = int(list_hash)

            if list_hash in self.item_list:
                list_item = self.item_list[list_hash]

                for parameter_name in self.request.arguments:
                    parameter_value = self.get_argument(parameter_name)

                    setattr(list_item, parameter_name, parameter_value)
            else:
                self.send_error(KEY_ERROR_CODE)

        else:
            self.send_error(NOT_SUPPORTED_ERROR_CODE)