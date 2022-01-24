# encoding: utf-8
from __future__ import absolute_import
import requests
import unittest

from mock import patch
from requests import Response

from rapyuta_io.clients.device import Device
from rapyuta_io.clients.model import Label
from rapyuta_io.utils import ParameterMissingException, LabelNotFoundException, \
    InternalServerError
from tests.utils.client import get_client
from tests.utils.device_respones import DEVICE_INFO, DEVICE_LABELS_LIST_OK, ADD_DEVICE_LABEL_OK, \
    ADD_DEVICE_LABEL_ERROR, ADD_DEVICE_LABEL_BAD_REQUEST, UPDATE_DEVICE_LABEL_OK, \
    UPDATE_DEVICE_lABEL_NOT_FOUNT, UPDATE_DEVICE_LABEL_BAD_REQUEST, DELETE_LABEL_NOT_FOUNT


class DeviceLabelTests(unittest.TestCase):

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_device_label_list_ok(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        device_labels_response = device_info_response()
        device_labels_response.status_code = requests.codes.OK
        device_labels_response.text = DEVICE_LABELS_LIST_OK
        mock_execute.side_effect = [device_info_response, device_labels_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        actual = device.get_labels()
        self.assertEqual(mock_execute.call_count, 2)
        self.assertEqual(len(actual), 1)
        self.assertTrue(isinstance(actual[0], Label), 'Actual should be an instance of class Label')
        self.assertEqual(actual[0]['id'], 100)
        self.assertEqual(actual[0]['key'], 'label1')
        self.assertEqual(actual[0]['value'], 'value1')

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_add_device_label_ok(self, rest_mock, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        add_label_response = device_info_response()
        add_label_response.text = ADD_DEVICE_LABEL_OK
        add_label_response.status_code = requests.codes.OK
        rest_mock.side_effect = [device_info_response, add_label_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        actual = device.add_label(key='label', value='value')
        expected = Label(key='label', value='value')
        expected.id = 100
        labels = [Label(key='label', value='value')]
        payload = {labels[0].key: labels[0].value}
        self.assertEqual(3, len(device.labels), 'Label count should be equal')
        rest_mock.assert_called_with(payload=payload)
        self.assertEqual(expected, actual, 'expected and actual should be same')
        self.assertEqual(rest_mock.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_add_device_label_duplicate_label_failure_case(self, mock_execute,
                                                           device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        add_label_response = device_info_response()
        add_label_response.text = ADD_DEVICE_LABEL_ERROR
        add_label_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_execute.side_effect = [device_info_response, add_label_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        with self.assertRaises(InternalServerError):
            device.add_label(key='label', value='value')
        self.assertEqual(2, len(device.labels))
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_add_device_label_missing_param_failure_case(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        add_label_response = device_info_response()
        add_label_response.text = ADD_DEVICE_LABEL_BAD_REQUEST
        add_label_response.status_code = requests.codes.BAD_REQUEST
        mock_execute.side_effect = [device_info_response, add_label_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        with self.assertRaises(ParameterMissingException):
            device.add_label(key='', value='')
        self.assertEqual(mock_execute.call_count, 1)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_label_ok(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        update_label_response = device_info_response()
        update_label_response.text = UPDATE_DEVICE_LABEL_OK
        update_label_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_info_response, update_label_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        label = Label(id=100, key='label', value='value')
        actual = device.update_label(label)
        mock_execute.assert_called_with(payload=label)
        self.assertEqual(mock_execute.call_count, 2)
        self.assertEqual(label, actual, 'expected actual should be same')
        self.assertEqual(len(device.labels), 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_label_invalid_label_failure_case(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        update_label_response = device_info_response()
        update_label_response.text = UPDATE_DEVICE_lABEL_NOT_FOUNT
        update_label_response.status_code = requests.codes.NOT_FOUND
        mock_execute.side_effect = [device_info_response, update_label_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        label = Label(id=105, key='label', value='value')
        with self.assertRaises(LabelNotFoundException):
            device.update_label(label)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_update_device_label_empty_label_failure_case(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        update_label_response = device_info_response()
        update_label_response.text = UPDATE_DEVICE_LABEL_BAD_REQUEST
        update_label_response.status_code = requests.codes.NOT_FOUND
        mock_execute.side_effect = [device_info_response, update_label_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        label = Label()
        with self.assertRaises(ParameterMissingException):
            device.update_label(label)
        self.assertEqual(mock_execute.call_count, 1)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_delete_device_label_ok(self, mock_execute, device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        delete_label_response = device_info_response()
        delete_label_response.text = ''' { "status": "success", "response": { "data": {} } } '''
        delete_label_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_info_response, delete_label_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        label_id = 100
        is_deleted = device.delete_label(label_id)
        self.assertTrue(is_deleted, 'actual should be True')
        self.assertEqual(len(device.labels), 1)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_delete_device_label_label_not_found_failure_case(self, mock_execute,
                                                              device_info_response):
        device_info_response.text = DEVICE_INFO
        device_info_response.status_code = requests.codes.OK
        delete_label_response = device_info_response()
        delete_label_response.text = DELETE_LABEL_NOT_FOUNT
        delete_label_response.status_code = requests.codes.NOT_FOUND
        mock_execute.side_effect = [device_info_response, delete_label_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        label_id = 105
        with self.assertRaises(LabelNotFoundException):
            device.delete_label(label_id)
        self.assertEqual(len(device.labels), 2)
