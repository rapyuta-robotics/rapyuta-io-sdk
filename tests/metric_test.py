from __future__ import absolute_import
import requests
import json
import unittest

from mock import patch, MagicMock
from requests import Response

from rapyuta_io.clients import Metric
from rapyuta_io.clients.device import SystemMetric, QoS
from rapyuta_io.utils import ConflictError, BadRequestError
from rapyuta_io.utils.rest_client import HttpMethod
from tests.utils.client import get_client
from tests.utils.device_respones import METRIC_SUBSCRIPTION_STATUS_SUCCESS, DEVICE_INFO, \
    METRIC_SUBSCRIPTION_STATUS_ERROR, METRIC_STATUS


class MetricTests(unittest.TestCase):

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    @patch('rapyuta_io.clients.device.Device._execute_api')
    def test_metric_subscribe_success(self, mock_device_execute, mock_execute, mock_get_device):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/metrics/test_device_id'
        expected_payload = {'name': 'cpu', 'config': {'qos': 1}}
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_execute.side_effect = [mock_get_device]
        mock_device_execute.return_value = MagicMock()
        mock_device_execute.return_value.status_code = 201
        mock_device_execute.return_value.text = METRIC_SUBSCRIPTION_STATUS_SUCCESS
        device = get_client().get_device('test_device_id')
        status = device.subscribe_metric(SystemMetric.CPU, QoS.MEDIUM)
        mock_device_execute.assert_called_once_with(expected_url, HttpMethod.POST, expected_payload, 0)
        self.assertTrue(status)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    @patch('rapyuta_io.clients.device.Device._execute_api')
    def test_metric_unsubscribe_success(self, mock_device_execute, mock_execute, mock_get_device):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/metrics/test_device_id/cpu'
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_execute.side_effect = [mock_get_device]
        mock_device_execute.return_value = MagicMock()
        mock_device_execute.return_value.status_code = 201
        mock_device_execute.return_value.text = METRIC_SUBSCRIPTION_STATUS_SUCCESS
        device = get_client().get_device('test_device_id')
        status = device.unsubscribe_metric(SystemMetric.CPU)
        mock_device_execute.assert_called_once_with(expected_url, HttpMethod.DELETE, retry_limit=0)
        self.assertTrue(status)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    @patch('rapyuta_io.clients.device.Device._execute_api')
    def test_metric_status_success(self, mock_device_execute, mock_execute, mock_get_device):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/metrics/test_device_id'
        metrics = json.loads(METRIC_STATUS)['response']['data']
        expected_status = []
        for metric in metrics:
            expected_status.append(Metric(metric))
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_execute.side_effect = [mock_get_device]
        mock_device_execute.return_value = MagicMock()
        mock_device_execute.return_value.status_code = 201
        mock_device_execute.return_value.text = METRIC_STATUS
        device = get_client().get_device('test_device_id')
        metrics_status = device.metrics()
        mock_device_execute.assert_called_once_with(expected_url, HttpMethod.GET, retry_limit=0)
        self.assertEqual(expected_status, metrics_status)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    @patch('rapyuta_io.clients.device.Device._execute_api')
    def test_metric_subscribe_error(self, mock_device_execute, mock_execute, mock_get_device):
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_execute.side_effect = [mock_get_device]
        mock_device_execute.return_value = MagicMock()
        mock_device_execute.return_value.status_code = requests.codes.CONFLICT
        mock_device_execute.return_value.text = METRIC_SUBSCRIPTION_STATUS_ERROR
        device = get_client().get_device('test_device_id')
        with self.assertRaises(ConflictError):
            device.subscribe_metric(SystemMetric.CPU, QoS.MEDIUM)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    @patch('rapyuta_io.clients.device.Device._execute_api')
    def test_metric_unsubscribe_error(self, mock_device_execute, mock_execute, mock_get_device):
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_execute.side_effect = [mock_get_device]
        mock_device_execute.return_value = MagicMock()
        mock_device_execute.return_value.status_code = requests.codes.BAD_REQUEST
        mock_device_execute.return_value.text = METRIC_SUBSCRIPTION_STATUS_ERROR
        device = get_client().get_device('test_device_id')
        with self.assertRaises(BadRequestError):
            device.unsubscribe_metric(SystemMetric.CPU)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    @patch('rapyuta_io.clients.device.Device._execute_api')
    def test_metric_status_error(self, mock_device_execute, mock_execute, mock_get_device):
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_execute.side_effect = [mock_get_device]
        mock_device_execute.return_value = MagicMock()
        mock_device_execute.return_value.status_code = requests.codes.BAD_REQUEST
        mock_device_execute.return_value.text = METRIC_SUBSCRIPTION_STATUS_ERROR
        device = get_client().get_device('test_device_id')
        with self.assertRaises(BadRequestError):
            device.metrics()
