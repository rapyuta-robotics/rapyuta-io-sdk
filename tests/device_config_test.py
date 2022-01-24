# encoding: utf-8
from __future__ import absolute_import
import requests
import unittest

from mock import patch
from requests import Response

from rapyuta_io.clients.device import Device
from rapyuta_io.clients.model import DeviceConfig
from rapyuta_io.utils import ParameterMissingException, ConfigNotFoundException, \
    OperationNotAllowedError, InternalServerError
from tests.utils.client import get_client
from tests.utils.device_respones import DEVICE_INFO, CONFIG_VARIABLES, ADD_CONFIG_VARIABLE_OK, \
    ADD_CONFIG_VARIABLE_BAD_REQUEST, ADD_CONFIG_VARIABLE_INTERNAL_ERROR, UPDATE_CONFIG_VARIABLE_OK, \
    UPDATE_CONFIG_VARIABLE_BAD_REQUEST, UPDATE_CONFIG_VARIABLE_INTERNAL_ERROR, \
    DELETE_CONFIG_VARIABLE_OK, DELETE_CONFIG_VARIABLE_NOT_FOUND


class DeviceConfigTests(unittest.TestCase):

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_device_config_list_ok(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        config_variable_response = device_info_response()
        config_variable_response.status_code = requests.codes.OK
        config_variable_response.text = CONFIG_VARIABLES
        mock_execute.side_effect = [device_info_response, config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        config_variables = device.get_config_variables()
        self.assertEqual(mock_execute.call_count, 2)
        self.assertIsNotNone(config_variables, 'Actual should not be empty')
        self.assertEqual(len(config_variables), 3)
        for config_var in config_variables:
            self.assertTrue(isinstance(config_var, DeviceConfig),
                            'Object should be an instance of class DeviceConfig')
        self.assertEqual(config_variables[0]['id'], 2140)
        self.assertEqual(config_variables[0]['key'], 'runtime')
        self.assertEqual(config_variables[0]['value'], 'preinstalled')

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_add_device_config_ok(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        add_config_variable_response = device_info_response()
        add_config_variable_response.text = ADD_CONFIG_VARIABLE_OK
        add_config_variable_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_info_response, add_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        actual = device.add_config_variable(key='testkey', value='value')
        self.assertTrue(isinstance(actual, DeviceConfig),
                        'Object should be an instance of class DeviceConfig')
        self.assertEqual(actual['id'], 100)
        self.assertEqual(actual['key'], 'testkey')
        self.assertEqual(actual['value'], 'value')
        self.assertEqual(len(device.config_variables), 5)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_add_device_config_empty_config_failure_case(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        add_config_variable_response = device_info_response()
        add_config_variable_response.text = ADD_CONFIG_VARIABLE_BAD_REQUEST
        add_config_variable_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_execute.side_effect = [device_info_response, add_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        with self.assertRaises(ParameterMissingException):
            device.add_config_variable('', None)
        self.assertEqual(mock_execute.call_count, 1)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_add_device_config_duplicate_key_failure_case(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        add_config_variable_response = device_info_response()
        add_config_variable_response.text = ADD_CONFIG_VARIABLE_INTERNAL_ERROR
        add_config_variable_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_execute.side_effect = [device_info_response, add_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        with self.assertRaises(InternalServerError):
            device.add_config_variable(key="testkey", value="testvalue")
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_config_ok(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        update_config_variable_response = device_info_response()
        update_config_variable_response.text = UPDATE_CONFIG_VARIABLE_OK
        update_config_variable_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_info_response, update_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        config = DeviceConfig(id=100, key="testkey", value="value")
        actual = device.update_config_variable(config)
        self.assertTrue(isinstance(actual, DeviceConfig),
                        'actual should be an instance of class DeviceConfig')
        self.assertEqual(actual['id'], 100)
        self.assertEqual(actual['key'], config.key)
        self.assertEqual(actual['value'], config.value)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_config_empty_config_failure_case(self, mock_execute,
                                                            device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        update_config_variable_response = device_info_response()
        update_config_variable_response.text = UPDATE_CONFIG_VARIABLE_BAD_REQUEST
        update_config_variable_response.status_code = requests.codes.BAD_REQUEST
        mock_execute.side_effect = [device_info_response, update_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        config = DeviceConfig(id=100, key='testKey')
        with self.assertRaises(ParameterMissingException):
            device.update_config_variable(config)
        self.assertEqual(mock_execute.call_count, 1)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_config_failure_case(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        update_config_variable_response = device_info_response()
        update_config_variable_response.text = UPDATE_CONFIG_VARIABLE_INTERNAL_ERROR
        update_config_variable_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_execute.side_effect = [device_info_response, update_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        config = DeviceConfig(id=100, key="testkey", value="testvalue")
        with self.assertRaises(InternalServerError):
            device.update_config_variable(config)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_default_device_config_variable_failure_case(self, mock_execute,
                                                                device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        mock_execute.return_value = device_info_response
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        config = DeviceConfig(id=100, key="runtime", value="testvalue")
        with self.assertRaises(OperationNotAllowedError):
            device.update_config_variable(config)
        self.assertEqual(mock_execute.call_count, 1)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_delete_device_config_ok(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        delete_config_variable_response = device_info_response()
        delete_config_variable_response.text = DELETE_CONFIG_VARIABLE_OK
        delete_config_variable_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_info_response, delete_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        config_id = 2134
        actual = device.delete_config_variable(config_id)
        self.assertTrue(actual, 'actual should be true')
        self.assertEqual(len(device.config_variables), 3)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_delete_default_device_config_variable_failure_case(self, mock_execute,
                                                                device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        delete_config_variable_response = device_info_response()
        delete_config_variable_response.text = DELETE_CONFIG_VARIABLE_OK
        delete_config_variable_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_info_response, delete_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        config_id = 2140
        with self.assertRaises(OperationNotAllowedError):
            device.delete_config_variable(config_id)
        self.assertEqual(mock_execute.call_count, 1)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_delete_device_config_invalid_config_id_failure_case(self, mock_execute,
                                                                 device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        delete_config_variable_response = device_info_response()
        delete_config_variable_response.text = DELETE_CONFIG_VARIABLE_NOT_FOUND
        delete_config_variable_response.status_code = requests.codes.NOT_FOUND
        mock_execute.side_effect = [device_info_response, delete_config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        config_id = 100
        with self.assertRaises(ConfigNotFoundException):
            device.delete_config_variable(config_id)
        self.assertEqual(mock_execute.call_count, 2)
