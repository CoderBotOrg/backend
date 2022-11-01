import os
from urllib.request import urlopen, Request
import json
import logging

class Balena():
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Balena()
        return cls._instance

    def __init__(self):
        self.supervisor_address = os.environ["BALENA_SUPERVISOR_ADDRESS"]
        self.supervisor_key = os.environ["BALENA_SUPERVISOR_API_KEY"]
        self.app_id_data = json.dumps({ "appId": os.environ["BALENA_APP_ID"] }).encode("utf-8")
        self.headers = { 'Content-Type': 'application/json' }

    def purge(self):
        logging.debug("reset bot")
        req = Request(f'{self.supervisor_address}/v1/purge?apikey={self.supervisor_key}', data=self.app_id_data, headers=self.headers, method='POST')
        return json.load(urlopen(req))

    def shutdown(self):
        logging.debug("shutdown bot")
        req = Request(f'{self.supervisor_address}/v1/shutdown?apikey={self.supervisor_key}', headers=self.headers, method='POST')
        return json.load(urlopen(req))

    def restart(self):
        logging.debug("restarting bot")
        req = Request(f'{self.supervisor_address}/v1/restart?apikey={self.supervisor_key}', data=self.app_id_data, headers=self.headers, method='POST')
        return json.load(urlopen(req))

    def reboot(self):
        logging.debug("reboot bot")
        req = Request(f'{self.supervisor_address}/v1/reboot?apikey={self.supervisor_key}', headers=self.headers, method='POST')
        return json.load(urlopen(req))

    def device(self):
        logging.debug("reboot bot", f'{self.supervisor_address}get?apikey={self.supervisor_key}')
        req = Request(f'{self.supervisor_address}/v1/device?apikey={self.supervisor_key}', headers=self.headers, method='GET')
        return json.load(urlopen(req))
