import json
import logging

import requests


class EspaAPI(object):

    def __init__(self, host, username, password):
        self.username = username
        self.password = password
        self.host = host

    def call(self, endpoint, verb='get', body=None):
        auth_tup = (self.username, self.password)
        response = getattr(requests, verb)(self.host + endpoint, auth=auth_tup, json=body)
        logging.debug(f'{response.status_code} {response.reason}')
        data = response.json()
        if isinstance(data, dict):
            messages = data.pop("messages", None)
            if messages:
                logging.debug(json.dumps(messages, indent=4))
        try:
            response.raise_for_status()
        except Exception as e:
            logging.warning(e)
            raise
        else:
            return data
