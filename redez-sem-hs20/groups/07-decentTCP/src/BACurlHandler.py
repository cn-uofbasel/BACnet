import json

import requests as requests

from BaseHandler import BaseHandler


class BACurlHandler(BaseHandler):

    def __init__(self):
        self.handlers = {}
        self.set_handler("get", self.handle_get)
        pass


    def handle_get(self, event, json_payload):
        payload = json.loads(json_payload)
        response = requests.get(payload['url'])
        return {"status_code": response.status_code, "headers": response.headers, "content":  response.content}

