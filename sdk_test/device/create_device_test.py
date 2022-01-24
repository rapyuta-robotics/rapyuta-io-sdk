from __future__ import absolute_import

import re

from rapyuta_io import ROSDistro
from rapyuta_io.clients.device import Device, DeviceRuntime, DevicePythonVersion
from sdk_test.config import Configuration
from sdk_test.util import get_logger
from sdk_test.device.device_test import DeviceTest


class CreateDeviceTest(DeviceTest):

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()

    def test_create_device_docker_compose(self):
        self.logger.info('creating a device with dockercompose runtime')
        device_object = Device(name='test-docker-device', runtime=DeviceRuntime.DOCKER, ros_distro=ROSDistro.MELODIC,
                               rosbag_mount_path='test/path', description='test-description')
        device = self.config.client.create_device(device_object)
        self.assertEqual(device.name, 'test-docker-device')
        self.assertEqual(device.description, 'test-description')
        expected_configs = {
            'runtime': 'dockercompose',
            'ros_distro': 'melodic',
            'rosbag_mount_path': 'test/path'
        }
        self.logger.info('validating the config variables of the created device')
        for config in device.config_variables:
            if config.key in expected_configs:
                self.assertEqual(expected_configs[config.key], config.value)
        self.logger.info('deleting the device')
        self.config.client.delete_device(device.deviceId)

    def test_create_device_preinstalled(self):
        self.logger.info('creating a device with preinstalled runtime')
        device_object = Device(name='test-preinstalled-device', runtime=DeviceRuntime.PREINSTALLED,
                               ros_distro=ROSDistro.MELODIC, ros_workspace='test/path', description='test-description')
        device = self.config.client.create_device(device_object)
        self.assertEqual(device.name, 'test-preinstalled-device')
        self.assertEqual(device.description, 'test-description')
        expected_configs = {
            'runtime': 'preinstalled',
            'ros_distro': 'melodic',
            'ros_workspace': 'test/path'
        }
        self.logger.info('validating the config variables of the created device')
        for config in device.config_variables:
            if config.key in expected_configs:
                self.assertEqual(expected_configs[config.key], config.value)
        self.logger.info('deleting the device')
        self.config.client.delete_device(device.deviceId)

    def test_onboard_device_print(self):
        url = self.config.api_server+'/start'
        onboard_script_regex = "curl -O -H 'Authorization: Bearer .*' " \
                                           "{url} && " \
                                           "sudo bash start -w test/path".format(url=url)
        self.logger.info('creating a device')
        device_object = Device(name='test-onboard-device-print', runtime=DeviceRuntime.PREINSTALLED,
                               ros_distro=ROSDistro.MELODIC, ros_workspace='test/path', description='test-description')
        device = self.config.client.create_device(device_object)
        onboard_script = device.onboard_script()
        self.assertIsNotNone(re.match(onboard_script_regex, onboard_script.full_command()))
        self.logger.info('deleting the device')
        self.config.client.delete_device(device.deviceId)

    def test_onboard_script_run(self):
        # TODO
        pass


    def test_create_device_python3_preinstalled(self):
        self.logger.info('creating a device with python3 preinstalled runtime')
        device_object = Device(name='test-preinstalled-device', runtime=DeviceRuntime.PREINSTALLED,
                               ros_distro=ROSDistro.MELODIC, ros_workspace='test/path',
                               python_version=DevicePythonVersion.PYTHON3,
                               description='test-description')
        device = self.config.client.create_device(device_object)
        self.assertEqual(device.name, 'test-preinstalled-device')
        self.assertEqual(device.description, 'test-description')
        self.assertEqual(device.python_version, DevicePythonVersion.PYTHON3.value)
        expected_configs = {
            'runtime': 'preinstalled',
            'ros_distro': 'melodic',
            'ros_workspace': 'test/path'
        }
        self.logger.info('validating the config variables of the created device')
        for config in device.config_variables:
            if config.key in expected_configs:
                self.assertEqual(expected_configs[config.key], config.value)
        self.logger.info('deleting the device')
        self.config.client.delete_device(device.deviceId)

    def test_upgrade_python2_to_python3_device(self):
        self.logger.info('creating a device on python2 with dockercompose runtime')
        device_object = Device(name='test-docker-device', runtime=DeviceRuntime.DOCKER, ros_distro=ROSDistro.MELODIC,
                               rosbag_mount_path='test/path', python_version=DevicePythonVersion.PYTHON2,
                               description='test-description')
        device = self.config.client.create_device(device_object)
        self.assertEqual(device.name, 'test-docker-device')
        self.assertEqual(device.description, 'test-description')
        self.assertEqual(device.python_version, DevicePythonVersion.PYTHON2)
        expected_configs = {
            'runtime': 'dockercompose',
            'ros_distro': 'melodic',
            'rosbag_mount_path': 'test/path'
        }
        self.logger.info('validating the config variables of the created device')
        for config in device.config_variables:
            if config.key in expected_configs:
                self.assertEqual(expected_configs[config.key], config.value)
        device.upgrade()
        device = self.config.client.get_device(device.deviceId)
        self.assertEqual(device.python_version, DevicePythonVersion.PYTHON3)
        self.logger.info('deleting the device')
        self.config.client.delete_device(device.deviceId)
