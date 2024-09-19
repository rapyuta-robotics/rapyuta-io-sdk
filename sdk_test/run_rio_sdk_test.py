from __future__ import absolute_import
import os
import sys
from itertools import cycle
from time import sleep
from unittest import TestLoader, TestSuite
import testtools

from rapyuta_io import DeviceArch
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import get_api_response_data, generate_random_value
from sdk_test.hwil import HWIL
from sdk_test.config import Configuration, filter_devices_by_name
from sdk_test.util import get_logger
from six.moves import filter


class IntegrationSuite(testtools.ConcurrentTestSuite):
    _REMOVE_COMMAND = 'sudo rapyuta-agent-uninstall'
    _CATKIN_WS = '/home/rapyuta/catkin_ws'

    def __init__(self):
        super(testtools.ConcurrentTestSuite, self).__init__()
        self.config = Configuration()
        self.hwil = HWIL()
        self.logger = get_logger()
        self.tests = self.get_concurrent_test_suites()

    def get_concurrent_test_suites(self):
        if self.config.test_files:
            return TestLoader().loadTestsFromNames(self.config.test_files)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return TestLoader().discover(dir_path, pattern='*test*.py')

    def setUpSuite(self):
        self.logger.info('Creating project')
        self.config.create_project()
        self.onboard_devices()
        self.wait_for_devices()

    def tearDownSuite(self):
        self.remove_devices()
        self.config.set_devices(None)
        self.logger.info('Deleting project')
        self.config.delete_project()

    def run(self, *args, **kwargs):
        self.setUpSuite()
        try:
            result = testtools.TextTestResult(sys.stdout)
            result.startTestRun()
            try:
                super(IntegrationSuite, self).run(result)
            finally:
                result.stopTestRun()
        finally:
            self.tearDownSuite()

    def onboard_devices(self):
        for device in self.config.get_device_configs():
            self.logger.info('On-boarding the device: %s', device['name'])
            self.onboard_device(device)

    def remove_devices(self):
        devices = self.config.client.get_all_devices(online_device=True, arch_list=[DeviceArch.AMD64])
        configs = self.config.get_device_configs()
        for device in devices:
            device_name = device.get('name')
            self.logger.info('Removing the device: %s', device_name)
            for config in configs:
                if config.get('name') == device_name:
                    device.delete()
                    device_id = self.hwil.get_device_id(config['ip'])
                    self.hwil.run_command(device_id, self._REMOVE_COMMAND)

    def onboard_device(self, device):
        """
        The device dictionary is used to know the details about the Device. The device is added to the Platform and
        using the HWIL APIs the script is run on the Device for it to onboard.
        """
        self.logger.debug('Adding the device on the platform')
        name, runtime, distro, ip = device['name'], device['runtime'], device['distro'], device['ip']
        response_data = self.add_device(name, runtime, distro)
        cmd = self.generate_onboard_command(response_data)
        self.logger.debug('Running the onboarding command')
        device_id = self.hwil.get_device_id(ip)
        self.hwil.run_command(device_id, cmd, wait=True, timeout=60, tries=20)

    def add_device(self, name, runtime, distro):
        """
        Adds the device on the Platform and fetches the JWT Token to be used for the on-boarding of the Device.
        """
        url = self.config.api_server + '/api/device-manager/v0/auth-keys/?download_type=script'
        payload = {'name': name, 'description': '', 'python_version': '3'}
        if runtime == 'Dockercompose':
            payload['config_variables'] = {
                'runtime_docker': True,
                'ros_distro': distro.lower()
            }
        elif runtime == 'Preinstalled':
            payload['config_variables'] = {
                'runtime_preinstalled': True,
                'ros_workspace': self._CATKIN_WS
            }
        response = RestClient(url).method(HttpMethod.POST).headers(self.config.get_auth_header()).execute(payload)
        return get_api_response_data(response, parse_full=True)

    def generate_onboard_command(self, response_data):
        """
        Generates the command to run on the device for it to onboard on the platform. It supports both Dockercompose and
        Preinstalled runtimes.

        The use-case is simple enough to not use template but in future we might want to switch to a template.
        """
        url = '{}/start'.format(self.config.api_server)
        run_cmd = response_data['response']['script_command']

        download_cmd = "curl -O -H 'Authorization: Bearer {}' {}".format(
            response_data['response']['data'], url
        )
        return '{} && {}'.format(download_cmd, run_cmd)

    def wait_for_devices(self):
        self.logger.info('Waiting for devices to come online')
        while True:
            devices = self.config.client.get_all_devices(online_device=True)
            devices = list(filter(filter_devices_by_name(), devices))
            if len(devices) == len(self.config.get_device_configs()):
                break
            sleep(20)

        self.logger.info('All devices came online')
        self.config.set_devices(devices)

    def make_tests(self, suite):
        # ConcurrentTestSuite class expects a make_tests method that splits the registered tests into bounded
        # number of tests which can run concurrently.
        suites = self.tests._tests
        worker_threads = min(len(suites), self.config.worker_threads)
        partitions = [list() for _ in range(worker_threads)]
        for partition, suite in zip(cycle(partitions), suites):
            partition.append(suite)
        return [Partition(partition) for partition in partitions]


class Partition(object):
    def __init__(self, partition_suite):
        self._hash = hash(generate_random_value())
        self._suite = partition_suite

    def run(self, result):
        TestSuite(self._suite).run(result)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Partition):
            return self._hash == other._hash
        return False


if __name__ == '__main__':
    suite = IntegrationSuite()
    suite.run()
