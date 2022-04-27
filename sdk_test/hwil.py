from __future__ import absolute_import
from __future__ import print_function
from time import sleep

import requests

from sdk_test.config import Configuration
from sdk_test.util import get_logger
from six.moves import range


class HWIL(object):
    """
    HWIL class implements methods to interact with Hardware-in-loop APIs and manipulate virtual devices
    programmatically.
    """
    RUN_COMMAND_URL = '{}/command/'
    GET_COMMAND_URL = '{}/command/{}'
    GET_DEVICE_URL = '{}/device/'

    def __init__(self):
        self.config = Configuration()
        self.logger = get_logger()
        self._device_map = dict()

    def run_command(self, device_id, cmd, wait=True, timeout=60, tries=5):
        """
        It runs the command on the given device using the HWIL APIs and optionally waits for it to finish.
        """
        url = self.RUN_COMMAND_URL.format(self.config.hwil_server)
        # Note: If this is not efficient, we can directly take the device_id as input from configuration.
        payload = {'device_id': device_id, 'command': cmd, 'timeout': timeout, 'uuid': ''}
        response = requests.post(url, json=payload, auth=self.config.get_hwil_credentials()).json()
        self.logger.debug('Submitted the command successfully!')
        if wait:
            self.logger.debug('Waiting for the command status...')
            self._watch_command_status(response['uuid'], timeout=timeout, tries=tries)

    def get_device_id(self, device_ip):
        """
        It returns the Device ID under HWIL based on the Device's IP Address. It does so by first fetching the entire
        list of the devices and then finding the one that matches the IP Address. It also caches the results to second
        time it need not fetch the list.
        """
        if device_ip not in self._device_map:
            url = self.GET_DEVICE_URL.format(self.config.hwil_server)
            response = requests.get(url, auth=self.config.get_hwil_credentials()).json()
            for device in response:
                if device['ip_address'] == device_ip:
                    self._device_map[device_ip] = device['id']
                    break
        return self._device_map[device_ip]

    def _watch_command_status(self, cmd_id, timeout=60, tries=5):
        """
        The command API on HWIL is asynchronous. This method can be used to stop the execution until the command is
        finished.
        """
        def failure(data):
            print('Command {} did not succeed!'.format(cmd_id))
            print(data)
            raise Exception
        url = self.GET_COMMAND_URL.format(self.config.hwil_server, cmd_id)
        for i in range(tries):
            response = requests.get(url, auth=self.config.get_hwil_credentials()).json()
            if response['status'] == 'IN_PROGRESS' or response['status'] == 'PENDING':
                sleep(timeout)
                continue
            elif response['status'] == 'SUCCESS':
                return
            else:
                failure(response)
        failure("Timeout!")
