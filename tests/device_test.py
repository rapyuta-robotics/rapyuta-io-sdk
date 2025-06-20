# encoding: utf-8
from __future__ import absolute_import

import copy
import json
import unittest
from datetime import timedelta, datetime
from time import time

import requests
from mock import patch, Mock, MagicMock, call
from requests import Response

from rapyuta_io import ROSDistro
from rapyuta_io.clients.device import Device, DeviceConfig, DevicePythonVersion
from rapyuta_io.clients.device_manager import DeviceArch
from rapyuta_io.clients.model import Command, SharedURL
from rapyuta_io.utils import DeviceNotFoundException, ParameterMissingException, \
    DeploymentRunningException, ResourceNotFoundError, BadRequestError, LogsUUIDNotFoundException, \
    InvalidParameterException, InternalServerError
from rapyuta_io.utils import ObjDict, InvalidCommandException
from tests.utils.client import get_client, headers
from tests.utils.device_respones import DEVICE_LIST, DEVICE_INFO, DEVICE_LIST_EMPTY, \
    DEVICE_NOT_FOUND, EXECUTE_COMMAND_BAD_REQUEST, EXECUTE_COMMAND_OK, DELETE_DEVICE_BAD_REQUEST, \
    DELETE_DEVICE_OK, UPDATE_DEVICE_BAD_REQUEST, UPDATE_DEVICE_OK, DEVICE_SELECTION, APPLY_PARAMETERS_SUCCESS_RESPONSE, \
    CREATE_DIRECT_LINK_SUCCESS_RESPONSE, CREATE_DOCKERCOMPOSE_DEVICE_SUCCESS, GET_DOCKERCOMPOSE_DEVICE_SUCCESS, \
    CREATE_PREINSTALLED_DEVICE_SUCCESS, GET_PREINSTALLED_DEVICE_SUCCESS, UPGRADE_DOCKERCOMPOSE_DEVICE_SUCCESS, \
    UPGRADE_DEVICE_BAD_REQUEST, CREATE_BOTH_RUNTIMES_DEVICE_SUCCESS, PATCH_DAEMONS_SUCCESS


class DeviceTests(unittest.TestCase):

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_device_list_ok(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_LIST
        get_device_response.status_code = requests.codes.OK
        mock_execute.return_value = get_device_response
        client = get_client()
        actual = client.get_all_devices()
        mock_execute.assert_called_once()
        self.assertIsNotNone(actual, 'Actual should not be empty')
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0]['uuid'], 'ebec2ef0-b2e8-4001-b255-4b2dbaeb8520')
        self.assertEqual(actual[1]['uuid'], '3747b7d7-ac60-4109-90a5-3dc4c8097384')
        self.assertEqual(actual[0]['status'], 'OFFLINE')
        self.assertEqual(actual[1]['status'], 'ONLINE')
        self.assertEqual(actual[0]['name'], 'D19-Device')
        self.assertEqual(actual[1]['name'], 'D239-Device')
        for device in actual:
            self.assertTrue(device.is_partial)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_device_list_empty_list_test_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_LIST_EMPTY
        get_device_response.status_code = requests.codes.OK
        mock_execute.return_value = get_device_response
        client = get_client()
        actual = client.get_all_devices()
        mock_execute.assert_called_once()
        self.assertEqual([], actual, 'Actual should not be empty')
        self.assertEqual(len(actual), 0)

    @patch('requests.Response', spec=Response)
    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_device_list_filter_by_arch_test_case(self, mock_execute, get_device_response,
                                                      device_selection_response):
        device_selection_response.text = DEVICE_SELECTION
        device_selection_response.status_code = requests.codes.OK
        get_device_response.text = DEVICE_LIST
        get_device_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_selection_response, get_device_response]
        client = get_client()
        actual = client.get_all_devices(arch_list=[DeviceArch.AMD64])
        mock_execute.assert_called()
        self.assertEqual(actual[0]['uuid'], '3747b7d7-ac60-4109-90a5-3dc4c8097384')
        self.assertEqual(actual[0]['status'], 'ONLINE')
        self.assertEqual(actual[0]['name'], 'D239-Device')
        for device in actual:
            self.assertTrue(device.is_partial)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_device_info_ok(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        mock_execute.return_value = get_device_response
        client = get_client()
        actual = client.get_device('test_device_id')
        mock_execute.assert_called_once()
        self.assertIsNotNone(actual, 'Actual should not be empty')
        self.assertEqual(actual['uuid'], 'test_device_id')
        self.assertEqual(actual['status'], 'ONLINE')
        self.assertEqual(actual['name'], 'D239-Device')
        self.assertFalse(actual.is_partial)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_device_info_device_not_found_failure_case(self, mock_execute,
                                                           get_device_response):
        get_device_response.text = DEVICE_NOT_FOUND
        get_device_response.status_code = requests.codes.NOT_FOUND
        mock_execute.return_value = get_device_response
        client = get_client()
        with self.assertRaises(ResourceNotFoundError):
            client.get_device('test_device_id')
        mock_execute.assert_called_once()

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_refresh_device_ok(self, mock_execute, device_list):
        device_list.text = DEVICE_LIST
        device_list.status_code = requests.codes.OK
        refresh_device_response = device_list()
        refresh_device_response.text = DEVICE_INFO
        refresh_device_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_list, refresh_device_response]
        client = get_client()
        devices = client.get_all_devices()
        device = devices[0]
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        self.assertTrue(device.is_partial)
        device.refresh()
        self.assertFalse(device.is_partial)
        self.assertEqual(mock_execute.call_count, 2)
        self.assertIsNotNone(device, 'Actual should not be empty')
        self.assertEqual(device['uuid'], 'test_device_id')
        self.assertEqual(device['status'], 'ONLINE')
        self.assertEqual(device['name'], 'D239-Device')

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_refresh_device_not_found_failure_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        device_refresh_response = get_device_response()
        device_refresh_response.text = DEVICE_NOT_FOUND
        device_refresh_response.status_code = requests.codes.NOT_FOUND
        mock_execute.side_effect = [get_device_response, device_refresh_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        with self.assertRaises(ResourceNotFoundError):
            device.refresh()
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_ok(self, mock_execute, response):
        response.text = DEVICE_INFO
        response.status_code = requests.codes.OK
        response2 = response()
        response2.text = UPDATE_DEVICE_OK
        response2.status_code = requests.codes.OK
        mock_execute.side_effect = [response, response2]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        device.name = 'Test Device-19'
        device.description = "Device description"
        device.status = 'ONLINE'
        device.device_id = 'test_device_id'
        device.save()
        self.assertEqual(mock_execute.call_count, 2)
        self.assertIsNotNone(device, 'device should not be empty')
        self.assertEqual(device.uuid, 'test_device_id')
        self.assertEqual(device.status, 'ONLINE')
        self.assertEqual(device.name, 'Test Device-19')

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_device_not_found_error_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        update_device_response = get_device_response()
        update_device_response.text = DEVICE_NOT_FOUND
        update_device_response.status_code = requests.codes.NOT_FOUND
        mock_execute.side_effect = [get_device_response, update_device_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        device.name = 'Test Device-19'
        device.description = "Device description"
        device.status = 'ONLINE'
        device.device_id = 'test_device_id'
        with self.assertRaises(DeviceNotFoundException):
            device.save()
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_empty_device_id_error_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        update_device_response = get_device_response()
        update_device_response.text = UPDATE_DEVICE_BAD_REQUEST
        update_device_response.status_code = requests.codes.BAD_REQUEST
        mock_execute.side_effect = [get_device_response, update_device_response]
        mock_execute.return_value = get_device_response
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        device.name = 'Test Device-19'
        device.description = "Device description"
        device.status = 'ONLINE'
        with self.assertRaises(ParameterMissingException):
            device.save(device)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_delete_device_ok(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        delete_device_response = get_device_response()
        delete_device_response.text = DELETE_DEVICE_OK
        delete_device_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, delete_device_response]
        client = get_client()
        device_id = 'test_device_id'
        device = client.get_device(device_id)
        delete_status = device.delete()
        self.assertTrue(delete_status, 'delete status should be true')

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_delete_device_device_not_found_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        delete_device_response = get_device_response()
        delete_device_response.text = DEVICE_NOT_FOUND
        delete_device_response.status_code = requests.codes.NOT_FOUND
        mock_execute.side_effect = [get_device_response, delete_device_response]
        client = get_client()
        device_id = 'test_device_id'
        device = client.get_device(device_id)
        with self.assertRaises(ResourceNotFoundError):
            device.delete()
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_delete_device_deployment_running_error_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        delete_device_response = get_device_response()
        delete_device_response.text = DELETE_DEVICE_BAD_REQUEST
        delete_device_response.status_code = requests.codes.BAD_REQUEST
        mock_execute.side_effect = [get_device_response, delete_device_response]
        client = get_client()
        device_id = 'test_device_id'
        device = client.get_device(device_id)
        with self.assertRaises(DeploymentRunningException):
            device.delete()
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_execute_command_ok(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        execute_command_response = get_device_response()
        execute_command_response.text = EXECUTE_COMMAND_OK
        execute_command_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, execute_command_response]
        mock_execute.return_value = get_device_response
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        command = Command('uname -a')
        command.shell = '/bin/bash'
        command.bg = False
        command.runas = 'root'
        command.cwd = ''
        result = device.execute_command(command)
        self.assertEqual(mock_execute.call_count, 2)
        expected = 'Linux rapyuta 4.9.80-v7+ #1098 SMP Fri Mar 9         19:11:42 GMT2018 armv7l ' \
                   'armv7l armv7l GNU/Linux'
        self.assertEqual(result, expected)

    def test_execute_command_invalid_parameters(self):
        test_cases = [
            {
                'response': 'Invalid execution command',
                'key': 'cmd',
                'value': True,
                'correct_value': 'pwd'
            },
            {
                'response': 'Invalid shell',
                'key': 'shell',
                'value': True,
                'correct_value': '/bin/bash'
            },
            {
                'response': 'Invalid background option',
                'key': 'bg',
                'value': 'true',
                'correct_value': False
            },
            {
                'response': 'Invalid runas option',
                'key': 'runas',
                'value': True,
                'correct_value': 'user'
            },
            {
                'response': 'Invalid cwd option',
                'key': 'cwd',
                'value': 123,
                'correct_value': '/home'
            },
            {
                'response': 'Invalid environment variables',
                'key': 'env',
                'value': [123],
                'correct_value': ['abc']
            },
            {
                'response': 'Invalid environment variables',
                'key': 'env',
                'value': {'123abc': 123},
                'correct_value': {'additionalProp1': 'abc'}
            }
        ]
        command = Command.__new__(Command)
        for test_case in test_cases:
            setattr(command, test_case['key'], test_case['value'])
            with self.assertRaises(InvalidCommandException) as e:
                command.validate()
            self.assertEqual(str(e.exception), test_case['response'])
            command[test_case['key']] = test_case['correct_value']

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_execute_command_failure_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        execute_command_response = get_device_response()
        execute_command_response.text = EXECUTE_COMMAND_BAD_REQUEST
        execute_command_response.status_code = requests.codes.BAD_REQUEST
        mock_execute.side_effect = [get_device_response, execute_command_response]
        mock_execute.return_value = get_device_response
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        command = Command('cmd')
        with self.assertRaises(ParameterMissingException):
            device.execute_command(command)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_deployment(self, mock_execute):
        get_device_response = Mock()
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        execute_command_response = Mock()
        execute_command_response.text = DEVICE_INFO
        execute_command_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, execute_command_response]
        mock_execute.return_value = get_device_response
        client = get_client()
        device = client.get_device('test_device_id')
        deployment = device.get_deployments()
        self.assertIsInstance(deployment, list, 'Object should be an instance of class List')
        self.assertIsInstance(deployment[0], ObjDict, 'Object should be an instance of class ObjDict')
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.request')
    def test_apply_parameters_success(self, mock_request):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = requests.codes.OK
        mock_response.text = APPLY_PARAMETERS_SUCCESS_RESPONSE
        mock_request.side_effect = [mock_response]
        expected_result = json.loads(APPLY_PARAMETERS_SUCCESS_RESPONSE)['response']['data']
        device_list = ['device-id-1', 'device-id-2']
        tree_names = ['tree1', 'tree2']

        result = get_client().apply_parameters(device_list, tree_names)
        self.assertSequenceEqual(expected_result, result)
        mock_request.assert_called_once_with(
            url='https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/parameters/', method='POST',
            headers=headers,
            params={}, json=dict(device_list=device_list, tree_names=tree_names),
            timeout=(30, 150),
        )

    @patch('requests.request')
    def test_apply_parameters_failure(self, mock_request):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = requests.codes.BAD_REQUEST
        mock_response.text = '{"error": "device_id should be a string"}'
        mock_request.side_effect = [mock_response]
        device_list = ['device-id-1', 'device-id-2']
        tree_names = ['tree1', 'tree2']

        with self.assertRaisesRegex(BadRequestError, 'device_id should be a string'):
            get_client().apply_parameters(device_list, tree_names)
        mock_request.assert_called_once_with(
            url='https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/parameters/',
            method='POST', headers=headers, params={},
            json=dict(device_list=device_list, tree_names=tree_names),
            timeout=(30, 150),
        )

    @patch('requests.request')
    def test_create_direct_link_for_log_file_not_found(self, mock_request):
        expected_err_msg = 'not able to find requested UUID request-uuid'
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = requests.codes.NOT_FOUND
        mock_response.text = '{"status":"error","response":{"data":{},"error":"log file not found"}}'
        mock_request.side_effect = [mock_response]
        device = Device._deserialize({'uuid': 'device-uuid',
                                      '_device_api_host': 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io',
                                      'config_variables': [
                                          {'id': 1, 'key': 'rosbag_mount_path', 'value': 'test/path', 'type': None}],
                                      'labels': [],
                                      'deployments': [],
                                      '_auth_token': 'auth-token',
                                      '_project': 'project-id'})
        expiry_time = datetime.fromtimestamp(time() + timedelta(days=7).total_seconds())
        with self.assertRaises(LogsUUIDNotFoundException) as e:
            device.create_shared_url(SharedURL('request-uuid', expiry_time))
        self.assertEqual(expected_err_msg, str(e.exception))

    @patch('rapyuta_io.utils.rest_client.DEFAULT_RETRY_COUNT', 0)
    @patch('requests.request')
    def test_create_direct_link_for_log_file_not_found(self, mock_request):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_response]
        device = Device._deserialize({'uuid': 'device-uuid',
                                      '_device_api_host': 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io',
                                      'config_variables': [
                                          {'id': 1, 'key': 'rosbag_mount_path', 'value': 'test/path', 'type': None}],
                                      'labels': [],
                                      'deployments': [],
                                      '_auth_token': 'auth-token',
                                      '_project': 'project-id'})
        expiry_time = datetime.fromtimestamp(time() + timedelta(days=7).total_seconds())
        with self.assertRaises(InternalServerError) as e:
            device.create_shared_url(SharedURL('request-uuid', expiry_time))

    @patch('requests.request')
    def test_create_direct_link_for_log_file_success(self, mock_request):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = requests.codes.OK
        mock_response.text = CREATE_DIRECT_LINK_SUCCESS_RESPONSE
        mock_request.side_effect = [mock_response]
        expected_uuid = json.loads(CREATE_DIRECT_LINK_SUCCESS_RESPONSE)['response']['data']['url_uuid']
        expected_result = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io//logs/sharedurl/{}'.format(expected_uuid)
        expiry_time = datetime.fromtimestamp(time() + timedelta(days=7).total_seconds())
        device = Device._deserialize({'uuid': 'device-uuid',
                                      '_device_api_host': 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io',
                                      'config_variables': [
                                          {'id': 1, 'key': 'rosbag_mount_path', 'value': 'test/path', 'type': None}],
                                      'labels': [],
                                      'deployments': [],
                                      '_auth_token': 'auth-token',
                                      '_project': 'project-id'})
        result = device.create_shared_url(SharedURL('required-uuid', expiry_time))
        self.assertIsInstance(result, SharedURL)
        self.assertEqual(expected_result, result.url)

    def test_shared_url_without_creating(self):
        expiry_time = datetime.now() + timedelta(days=7)
        expected_msg = 'SharedURL must be created first'
        shared_url = SharedURL('required-uuid', expiry_time)
        with self.assertRaises(InvalidParameterException) as e:
            shared_url.url
        self.assertEqual(expected_msg, str(e.exception))

    def test_shared_url_validation_invalid_request_uuid(self):
        expiry_time = datetime.now() + timedelta(days=7)
        expected_msg = 'request_uuid must be a non-empty string'
        with self.assertRaises(InvalidParameterException) as e:
            SharedURL(1, expiry_time)
        self.assertEqual(expected_msg, str(e.exception))

    def test_shared_url_validation_invalid_expiry_time(self):
        expected_msg = 'expiry_time must be a datetime.datetime'
        with self.assertRaises(InvalidParameterException) as e:
            SharedURL('required-uuid', 'some-time')
        self.assertEqual(expected_msg, str(e.exception))

    def test_shared_url_validation_empty_request_uuid(self):
        expiry_time = datetime.now() + timedelta(days=7)
        expected_msg = 'request_uuid must be a non-empty string'
        with self.assertRaises(InvalidParameterException) as e:
            SharedURL('', expiry_time)
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_name_failure(self):
        expected_msg = 'name must be a non-empty string'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(1)
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_python_version_failure(self):
        expected_msg = 'python_version must be one of rapyuta.io.client.device.DevicePythonVersion'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', python_version='invalid')
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_device_runtime_failure(self):
        expected_msg = 'runtime must be one of rapyuta_io.clients.device.DeviceRuntime'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', runtime='invalid-runtime')
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_device_docker_runtime_failure(self):
        expected_msg = 'runtime_docker must be a boolean'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', runtime_docker='True')
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_device_preinstalled_runtime_failure(self):
        expected_msg = 'runtime_preinstalled must be a boolean'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', runtime_preinstalled='True')
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_ros_distro_failure(self):
        expected_msg = 'ros_distro must be one of rapyuta_io.clients.package.ROSDistro'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', ros_distro='invalid-ros-distro')
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_preinstalled_noetic_failure(self):
        expected_msg = 'preinstalled runtime does not support noetic ros_distro yet'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', runtime_preinstalled=True,
                            ros_distro=ROSDistro.NOETIC)
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_noetic_python2_failure(self):
        expected_msg = 'noetic ros_distro not supported on python_version 2'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', runtime_docker=True,
                            ros_distro=ROSDistro.NOETIC, python_version=DevicePythonVersion.PYTHON2)
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_rosbag_mount_path_failure(self):
        expected_msg = 'rosbag_mount_path must be of type string'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', rosbag_mount_path=1)
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_ros_workspace_failure(self):
        expected_msg = 'ros_workspace must be of type string'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', ros_workspace=1)
        self.assertEqual(expected_msg, str(e.exception))

    def test_create_device_invalid_description_failure(self):
        expected_msg = 'description must be of type string'
        with self.assertRaises(InvalidParameterException) as e:
            device = Device(name='test-device', description=1)
        self.assertEqual(expected_msg, str(e.exception))

    @patch('requests.request')
    def test_create_device_dockercompose_success(self, mock_request):
        expected_payload = {
            'name': 'test-device',
            'description': 'test-description',
            'python_version': '2',
            'config_variables': {
                'runtime_docker': True,
                'ros_distro': 'melodic',
                'rosbag_mount_path': 'test/path'
            },
            'labels': {}
        }
        expected_create_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/auth-keys/?download_type=script'
        expected_get_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/devices/test-device-id'
        device = Device(name='test-device', runtime_docker=True, runtime_preinstalled=False,
                        ros_distro=ROSDistro.MELODIC, rosbag_mount_path='test/path', description='test-description')
        create_device_response = Mock()
        create_device_response.text = CREATE_DOCKERCOMPOSE_DEVICE_SUCCESS
        create_device_response.status_code = requests.codes.OK

        get_device_response = Mock()
        get_device_response.text = GET_DOCKERCOMPOSE_DEVICE_SUCCESS
        get_device_response.status_code = requests.codes.OK

        mock_request.side_effect = [create_device_response, get_device_response]
        client = get_client()
        device = client.create_device(device)
        mock_request.assert_has_calls([
            call(url=expected_create_device_url, method='POST', headers=headers, params={}, json=expected_payload,
                 timeout=(30, 150)),
            call(headers=headers, json=None, url=expected_get_device_url, method='GET', params={},
                 timeout=(30, 150)),
        ])

        self.assertEqual(device.name, 'test-device')
        self.assertEqual(device.description, 'test-description')

        expected_configs = {
            'runtime': 'dockercompose',
            'ros_distro': 'melodic',
            'rosbag_mount_path': 'test/path'
        }
        for config in device.config_variables:
            if config.key in expected_configs:
                self.assertEqual(expected_configs[config.key], config.value)

    @patch('requests.request')
    def test_create_device_preinstalled_success(self, mock_request):
        expected_payload = {
            'name': 'test-device',
            'description': 'test-description',
            'python_version': '2',
            'config_variables': {
                'runtime_preinstalled': True,
                'ros_distro': 'melodic',
                'ros_workspace': 'test/path'
            },
            'labels': {}
        }
        expected_create_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/auth-keys/?download_type=script'
        expected_get_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/devices/test-device-id'
        device = Device(name='test-device', runtime_preinstalled=True, ros_distro=ROSDistro.MELODIC,
                        ros_workspace='test/path', description='test-description')
        create_device_response = Mock()
        create_device_response.text = CREATE_PREINSTALLED_DEVICE_SUCCESS
        create_device_response.status_code = requests.codes.OK

        get_device_response = Mock()
        get_device_response.text = GET_PREINSTALLED_DEVICE_SUCCESS
        get_device_response.status_code = requests.codes.OK

        mock_request.side_effect = [create_device_response, get_device_response]
        client = get_client()
        device = client.create_device(device)
        mock_request.assert_has_calls([
            call(url=expected_create_device_url, method='POST', headers=headers, params={}, json=expected_payload,
                 timeout=(30, 150)),
            call(headers=headers, json=None, url=expected_get_device_url, method='GET', params={},
                 timeout=(30, 150))
        ])

        self.assertEqual(device.name, 'test-device')
        self.assertEqual(device.description, 'test-description')

        expected_configs = {
            'runtime': 'preinstalled',
            'ros_distro': 'melodic',
            'ros_workspace': 'test/path'
        }
        for config in device.config_variables:
            if config.key in expected_configs:
                self.assertEqual(expected_configs[config.key], config.value)

    @patch('requests.request')
    def test_create_device_dockercompose_success(self, mock_request):
        expected_payload = {
            'name': 'test-device',
            'description': 'test-description',
            'python_version': '2',
            'config_variables': {
                'runtime_docker': True,
                'runtime_preinstalled': True,
                'ros_distro': 'melodic',
                'rosbag_mount_path': 'test/path',
                'custom-config-variable-1': 'value1',
                'custom-config-variable-2': 'value2'
            },
            'labels': {
                'custom-label-1': 'label1',
                'custom-label-2': 'label2',
                'custom-label-3': 'label3'
            }
        }
        expected_create_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/auth-keys/?download_type=script'
        expected_get_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/devices/test-device-id'
        device = Device(name='test-device', runtime_docker=True, runtime_preinstalled=True,
                        ros_distro=ROSDistro.MELODIC, rosbag_mount_path='test/path', description='test-description',
                        config_variables={'custom-config-variable-1': 'value1','custom-config-variable-2': 'value2'},
                        labels={'custom-label-1': 'label1','custom-label-2': 'label2','custom-label-3': 'label3'})
        create_device_response = Mock()
        create_device_response.text = CREATE_BOTH_RUNTIMES_DEVICE_SUCCESS
        create_device_response.status_code = requests.codes.OK

        get_device_response = Mock()
        get_device_response.text = GET_DOCKERCOMPOSE_DEVICE_SUCCESS
        get_device_response.status_code = requests.codes.OK

        mock_request.side_effect = [create_device_response, get_device_response]
        client = get_client()
        device = client.create_device(device)
        mock_request.assert_has_calls([
            call(url=expected_create_device_url, method='POST', headers=headers, params={}, json=expected_payload,
                 timeout=(30, 150)),
            call(headers=headers, json=None, url=expected_get_device_url, method='GET', params={}, timeout=(30, 150))
        ])

        self.assertEqual(device.name, 'test-device')
        self.assertEqual(device.description, 'test-description')

        expected_configs = {
            'runtime': 'dockercompose',
            'ros_distro': 'melodic',
            'rosbag_mount_path': 'test/path',
            'custom-config-variable-1': 'value1',
            'custom-config-variable-2': 'value2',
        }
        for config in device.config_variables:
            if config.key in expected_configs:
                self.assertEqual(expected_configs[config.key], config.value)
        expected_labels = {
            'custom-label-1': 'label1',
            'custom-label-2': 'label2',
            'custom-label-3': 'label3'
        }
        for label in device.labels:
            if label.key in expected_labels:
                self.assertEqual(expected_labels[label.key], label.value)

    @patch('requests.request')
    def test_onboard_script_dockercompose_success(self, mock_request):
        expected_onboard_script_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager' \
                                      '/v0/auth-keys/test-device-id/token'
        expected_onboard_script = "curl -O -H 'Authorization: Bearer sample-token' " \
                                  "https://gaapiserver.apps.okd4v2.prod.rapyuta.io/start && " \
                                  "sudo bash start -r dockercompose -d melodic -b test/path"
        get_onboard_success = Mock()
        get_onboard_success.text = CREATE_DOCKERCOMPOSE_DEVICE_SUCCESS
        get_onboard_success.status_code = requests.codes.OK
        mock_request.side_effect = [get_onboard_success]
        device = Device(name='test-device', runtime_docker=True, ros_distro=ROSDistro.MELODIC,
                        rosbag_mount_path='test/path', python_version=DevicePythonVersion.PYTHON3)
        device.deviceId = 'test-device-id'
        device._device_api_host = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io'
        device._auth_token = headers['Authorization']
        device._project = headers['project']
        onboard_script = device.onboard_script()

        temp_header = copy.deepcopy(headers)
        temp_header['Content-Type'] = 'application/json'

        mock_request.assert_called_once_with(
            url=expected_onboard_script_url, method='GET', headers=temp_header, params=None, json=None, timeout=(30, 150))
        self.assertEqual(onboard_script.url, 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/start')
        self.assertEqual(onboard_script.command, 'sudo bash start -r dockercompose -d melodic -b test/path')
        self.assertEqual(onboard_script.token, 'sample-token')
        self.assertEqual(onboard_script.full_command(), expected_onboard_script)

    @patch('requests.request')
    def test_onboard_script_preinstalled_success(self, mock_request):
        expected_onboard_script_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager' \
                                      '/v0/auth-keys/test-device-id/token'
        expected_onboard_script = "curl -O -H 'Authorization: Bearer sample-token' " \
                                  "https://gaapiserver.apps.okd4v2.prod.rapyuta.io/start && " \
                                  "sudo bash start -r preinstalled -w test/path"
        get_onboard_success = Mock()
        get_onboard_success.text = CREATE_PREINSTALLED_DEVICE_SUCCESS
        get_onboard_success.status_code = requests.codes.OK
        mock_request.side_effect = [get_onboard_success]
        device = Device(name='test-device', runtime_preinstalled=True, ros_distro=ROSDistro.MELODIC,
                        rosbag_mount_path='test/path')
        device.deviceId = 'test-device-id'
        device._device_api_host = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io'
        device._auth_token = headers['Authorization']
        device._project = headers['project']
        onboard_script = device.onboard_script()

        temp_header = copy.deepcopy(headers)
        temp_header['Content-Type'] = 'application/json'

        mock_request.assert_called_once_with(
            url=expected_onboard_script_url, method='GET', headers=temp_header, params=None, json=None, timeout=(30, 150))
        self.assertEqual(onboard_script.url, 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/start')
        self.assertEqual(onboard_script.command, 'sudo bash start -r preinstalled -w test/path')
        self.assertEqual(onboard_script.token, 'sample-token')
        self.assertEqual(onboard_script.full_command(), expected_onboard_script)

    @patch('requests.request')
    def test_onboard_script_both_runtimes_success(self, mock_request):
        expected_onboard_script_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager' \
                                      '/v0/auth-keys/test-device-id/token'
        expected_onboard_script = "curl -O -H 'Authorization: Bearer sample-token' " \
                                  "https://gaapiserver.apps.okd4v2.prod.rapyuta.io/start && " \
                                  "sudo bash start -r dockercompose -d melodic -b test/path -r preinstalled"
        get_onboard_success = Mock()
        get_onboard_success.text = CREATE_BOTH_RUNTIMES_DEVICE_SUCCESS
        get_onboard_success.status_code = requests.codes.OK
        mock_request.side_effect = [get_onboard_success]
        device = Device(name='test-device', runtime_docker=True, runtime_preinstalled=True,
                        ros_distro=ROSDistro.MELODIC, rosbag_mount_path='test/path',
                        python_version=DevicePythonVersion.PYTHON3)
        device.deviceId = 'test-device-id'
        device._device_api_host = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io'
        device._auth_token = headers['Authorization']
        device._project = headers['project']
        onboard_script = device.onboard_script()

        temp_header = copy.deepcopy(headers)
        temp_header['Content-Type'] = 'application/json'

        mock_request.assert_called_once_with(
            url=expected_onboard_script_url, method='GET', headers=temp_header, params=None, json=None, timeout=(30, 150))
        self.assertEqual(onboard_script.url, 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/start')
        self.assertEqual(onboard_script.command, 'sudo bash start -r dockercompose -d melodic -b test/path -r '
                                                 'preinstalled')
        self.assertEqual(onboard_script.token, 'sample-token')
        self.assertEqual(onboard_script.full_command(), expected_onboard_script)

    def test_delete_device_invalid_id_failure(self):
        expected_msg = 'device_id needs to be a non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.delete_device(1)
        self.assertEqual(expected_msg, str(e.exception))

    @patch('requests.request')
    def test_delete_device_success(self, mock_request):
        device = Device(name='test-device', runtime_preinstalled=True, ros_distro=ROSDistro.MELODIC,
                        rosbag_mount_path='test/path')
        device.deviceId = 'test-device-id'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/devices/test-device-id'
        delete_device_success = Mock()
        delete_device_success.status_code = requests.codes.OK
        mock_request.side_effect = [delete_device_success]
        client = get_client()
        client.delete_device('test-device-id')
        mock_request.assert_called_once_with(
            url=expected_url, method='DELETE', headers=headers, params={}, json=None, timeout=(30, 150))

    def test_toggle_features_invalid_id_failure(self):
        expected_msg = 'device_id needs to be a non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.toggle_features(1, [])
        self.assertEqual(expected_msg, str(e.exception))

    def test_toggle_features_invalid_features_failure(self):
        expected_msg = 'device_id needs to be a non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.toggle_features(1, "features")
        self.assertEqual(expected_msg, str(e.exception))

    @patch('requests.request')
    def test_toggle_features_success(self, mock_request):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/devices/test-device-id/daemons'
        toggle_features_success = Mock()
        toggle_features_success.text = PATCH_DAEMONS_SUCCESS
        toggle_features_success.status_code = requests.codes.OK
        mock_request.side_effect = [toggle_features_success]
        client = get_client()
        client.toggle_features('test-device-id', [('vpn', True)])
        expected_payload = {"vpn": True}
        mock_request.assert_called_once_with(
            url=expected_url, method='PATCH', headers=headers, params={}, json=expected_payload, timeout=(30, 150))

    @patch('requests.request')
    def test_upgrade_device_dockercompose_success(self, mock_request):
        expected_upgrade_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/devices/device-uuid/upgrade'

        get_onboard_success = Mock()
        get_onboard_success.text = UPGRADE_DOCKERCOMPOSE_DEVICE_SUCCESS
        get_onboard_success.status_code = requests.codes.OK
        mock_request.side_effect = [get_onboard_success]
        device = Device._deserialize({'uuid': 'device-uuid',
                                      '_device_api_host': 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io',
                                      'config_variables': [
                                          {'id': 1, 'key': 'rosbag_mount_path', 'value': 'test/path', 'type': None}],
                                      'labels': [],
                                      'deployments': [],
                                      '_auth_token': 'Bearer test_auth_token',
                                      '_project': 'test_project'})
        upgrade_sucess = device.upgrade()

        temp_header = copy.deepcopy(headers)
        temp_header['Content-Type'] = 'application/json'

        mock_request.assert_called_once_with(
            url=expected_upgrade_device_url, method='PUT', headers=temp_header, params=None, json=None, timeout=(30, 150))

    @patch('requests.request')
    def test_upgrade_device_not_found(self, mock_request):
        get_device_response = Mock()
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        upgrade_device_response = get_device_response()
        upgrade_device_response.text = DEVICE_NOT_FOUND
        upgrade_device_response.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [get_device_response, upgrade_device_response]
        client = get_client()
        device_id = 'test_device_id'
        device = client.get_device(device_id)
        with self.assertRaises(ResourceNotFoundError):
            device.upgrade()
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.request')
    def test_upgrade_device_deployment_running_error(self, mock_request):
        get_device_response = Mock()
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        upgrade_device_response = get_device_response()
        upgrade_device_response.text = UPGRADE_DEVICE_BAD_REQUEST
        upgrade_device_response.status_code = requests.codes.BAD_REQUEST

        mock_request.side_effect = [get_device_response, upgrade_device_response]
        client = get_client()
        device_id = 'test_device_id'
        device = client.get_device(device_id)
        with self.assertRaises(DeploymentRunningException):
            device.upgrade()
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.request')
    def test_create_device_python3_dockercompose_success(self, mock_request):
        expected_payload = {
            'name': 'test-device',
            'description': 'test-description',
            'python_version': '3',
            'config_variables': {
                'runtime_docker': True,
                'ros_distro': 'melodic',
                'rosbag_mount_path': 'test/path'
            },
            'labels': {}
        }
        expected_create_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/auth-keys/?download_type=script'
        expected_get_device_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/devices/test-device-id'
        device = Device(name='test-device', runtime_docker=True, ros_distro=ROSDistro.MELODIC,
                        rosbag_mount_path='test/path', description='test-description',
                        python_version=DevicePythonVersion.PYTHON3)
        create_device_response = Mock()
        create_device_response.text = CREATE_DOCKERCOMPOSE_DEVICE_SUCCESS
        create_device_response.status_code = requests.codes.OK

        get_device_response = Mock()
        get_device_response.text = GET_DOCKERCOMPOSE_DEVICE_SUCCESS
        get_device_response.status_code = requests.codes.OK

        mock_request.side_effect = [create_device_response, get_device_response]
        client = get_client()
        device = client.create_device(device)
        mock_request.assert_has_calls([
            call(url=expected_create_device_url, method='POST', headers=headers, params={}, json=expected_payload,
                 timeout=(30, 150)),
            call(headers=headers, json=None, url=expected_get_device_url, method='GET', params={},
                 timeout=(30, 150))
        ])

        self.assertEqual(device.name, 'test-device')
        self.assertEqual(device.description, 'test-description')

        expected_configs = {
            'runtime': 'dockercompose',
            'ros_distro': 'melodic',
            'rosbag_mount_path': 'test/path'
        }
        for config in device.config_variables:
            if config.key in expected_configs:
                self.assertEqual(expected_configs[config.key], config.value)

    def test_device_is_docker_enabled_true(self):
        device = Device(name='test-device')
        device.config_variables = [
            DeviceConfig(id=100, key="runtime_docker", value="True")
        ]

        self.assertTrue(device.is_docker_enabled())

    def test_device_is_docker_enabled_false(self):
        device = Device(name='test-device')
        device.config_variables = [
            DeviceConfig(id=100, key="runtime_docker", value="False")
        ]

        self.assertFalse(device.is_docker_enabled())

    def test_device_is_docker_enabled_false_empty_config_variables(self):
        device = Device(name='test-device')
        device.config_variables = []

        self.assertFalse(device.is_docker_enabled())

    def test_device_is_docker_enabled_false_no_runtime_docker_config_variable(self):
        device = Device(name='test-device')
        device.config_variables = [
            DeviceConfig(id=100, key="testkey", value="testvalue")
        ]

        self.assertFalse(device.is_docker_enabled())

    def test_device_is_preinstalled_enabled_true(self):
        device = Device(name='test-device')
        device.config_variables = [
            DeviceConfig(id=100, key="runtime_preinstalled", value="True")
        ]

        self.assertTrue(device.is_preinstalled_enabled())

    def test_device_is_preinstalled_enabled_false(self):
        device = Device(name='test-device')
        device.config_variables = [
            DeviceConfig(id=100, key="runtime_preinstalled", value="False")
        ]

        self.assertFalse(device.is_preinstalled_enabled())

    def test_device_is_preinstalled_enabled_false_empty_config_variables(self):
        device = Device(name='test-device')
        device.config_variables = []

        self.assertFalse(device.is_preinstalled_enabled())

    def test_device_is_preinstalled_enabled_false_no_runtime_preinstalled_config_variable(self):
        device = Device(name='test-device')
        device.config_variables = [
            DeviceConfig(id=100, key="testkey", value="testvalue")
        ]

        self.assertFalse(device.is_preinstalled_enabled())
