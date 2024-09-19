from __future__ import absolute_import

import json
import os

import six
from six.moves import filter

from rapyuta_io import Client, DeviceArch
from rapyuta_io.utils.error import InvalidParameterException
from rapyuta_io.utils.utils import create_auth_header, \
    prepend_bearer_to_auth_token, generate_random_value
from sdk_test.util import get_logger
from sdk_test.v2_client import V2Client


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args,
                                                                  **kwargs)
        return cls._instances[cls]


class Configuration(six.with_metaclass(_Singleton, object)):
    """
    Configuration is a singleton class that is initialized once and all subsequent creations use the same Object. It
    reads in the JSON configuration file for Integration tests. It exposes various combinations of values through
    specialized methods.

    The first instantiation must be done in the setUpSuite method of the Integration Suite. The first instantiation will
    also validate the JSON (fail fast). All unittests should set the config attribute with the Configuration instance.

        >>> class TestClass(unittest):
        >>>     def __init__(self):
        >>>         self.config = Configuration()

    NOTE: You must set the RIO_CONFIG environment variable to also point to the JSON file. This is required because
    internal client classes use it to point to the approriate staging environment routes.

    Following snippet is an example configuration file with all possible fields. There is no validation on extra fields.
    The configuration MUST include one device each of the following configuration:
    * AMD64 with Preinstalled runtime
    * AMD64 with Dockercompose runtime

    Example:
        {
            "catalog_host": "http://catalog-server",
            "core_api_host": "http://api-server",
            "hwil_host": "http://hwil-server",
            "hwil_user": "user",
            "hwil_password": "password",
            "auth_token": "<AUTH>",
            "organization_guid": "<org_guid>",
            "devices": [
                {
                    "name": "DEVICE_NAME",
                    "runtime": "DEVICE_RUNTIME",
                    "distro": "DEVICE_DISTRO", # Optional
                    "ip": "DEVICE_IP"
                    "arch": "ARCHITECTURE",
                    "distro": "ROS_DISTRO"
                }
            ]
        }
    """

    def __init__(self, file_path=None):
        if file_path is None:
            file_path = os.getenv('RIO_CONFIG')
        self._devices = None
        self._secrets = None
        with open(file_path, "r") as config_file:
            self._config = json.load(config_file)
        self.validate()
        self.client = Client(self._config['auth_token'])
        self.catalog_server = self._config['catalog_host']
        self.api_server = self._config['core_api_host']
        self.hwil_server = self._config['hwil_host']
        self.v2_server = self._config['v2_api_host']
        self._project_guid = None
        self.test_files = self._config['test_files']
        if not isinstance(self.test_files, list):
            raise InvalidParameterException('test_files must be a list of test file names')
        self.worker_threads = self._config['worker_threads']
        self.organization_guid = self._config.get('organization_guid')
        self.logger = get_logger()
        self.v2_client = V2Client(self._config['auth_token'], self.v2_server)

    def validate(self):
        if len(self.get_device_configs(arch=DeviceArch.AMD64, runtime='Dockercompose')) != 1:
            raise InvalidConfig('One amd64 device with Docker Compose runtime is required')

    def get_hwil_credentials(self):
        return self._config['hwil_user'], self._config['hwil_password']

    def get_auth_header(self):
        auth_token = prepend_bearer_to_auth_token(self._config['auth_token'])
        return create_auth_header(auth_token, self._config['project'])

    def get_auth_token(self):
        return self._config['auth_token']

    def create_project(self):
        # Project name needs to be between 3 and 15 Characters
        name = 'test-{}'.format(generate_random_value(8))
        self._project_guid = self.v2_client.create_project({
            'metadata': {
                'name': name,
                'organizationGUID': self.organization_guid
            },
        })
        self.logger.info('Created project: {}'.format(name))
        self.set_project(self._project_guid)

    def delete_project(self):
        if self._project_guid is None:
            return
        self.v2_client.delete_project(self._project_guid)

    def set_project(self, project_guid):
        self._config['project'] = project_guid
        self.client.set_project(project_guid)

    def get_device_configs(self, arch=None, distro=None, runtime=None):
        if arch is None and distro is None and runtime is None:
            return self._config['devices']

        configs = self._config['devices']
        if arch is not None:
            configs = [x for x in configs if x['arch'] == arch]
        if distro is not None:
            configs = [x for x in configs if x['distro'] == distro]
        if runtime is not None:
            configs = [x for x in configs if x['runtime'] == runtime]

        return configs

    def get_devices(self, arch=None, distro=None, runtime=None):
        if arch is None and distro is None and runtime is None:
            return self._devices

        configs = self.get_device_configs(arch=arch, distro=distro, runtime=runtime)
        devices = list(filter(filter_devices_by_name(configs), self._devices))
        return devices

    def set_devices(self, devices):
        if devices is None:
            self._devices = None
        else:
            self._devices = list(filter(filter_devices_by_name(), devices))


class InvalidConfig(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


def filter_devices_by_name(device_configs=None):
    if device_configs is None:
        device_configs = Configuration().get_device_configs()

    def filter_func(device):
        for config in device_configs:
            if device['name'] == config['name']:
                return True
        return False

    return filter_func
