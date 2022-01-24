from __future__ import absolute_import
import requests

from datetime import datetime
import unittest
import six
from mock import patch, Mock

from rapyuta_io.clients import LogsUploadRequest, SharedURL
from rapyuta_io.utils import InvalidParameterException, LogsUUIDNotFoundException, BadRequestError
from tests.utils.client import get_client
from tests.utils.device_respones import DEVICE_INFO, LOGS_UPLOAD_SUCCESS, LOGS_UPLOAD_STATUS_SUCCESS, \
    LOGS_DOWNLOAD_FILE, LOGS_GENERIC_RESPONSE, LIST_LOGS_UPLOAD_STATUS_SUCCESS, \
    LOGS_UPLOAD_STATUS_WITH_SHARED_URL_SUCCESS, LIST_LOGS_UPLOAD_STATUS_FAILURE_INVALID_OPTIONAL_PARAMETERS

TEST_DEVICE_ID = 'test_device_id'


class LogsUploadDownloadTest(unittest.TestCase):

    @patch('requests.request')
    def test_upload_log_file_success(self, mock_request):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/logs/{}/upload'.format(TEST_DEVICE_ID)
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LOGS_UPLOAD_SUCCESS
        mock_device_execute.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        upload_request = LogsUploadRequest('minion', '/var/log/salt/', True, False, {'key': 'value'})
        expected_body = upload_request.to_json()
        uuid = device.upload_log_file(upload_request)
        call_dict = mock_request.call_args_list[1][1]
        self.assertEqual(expected_url, call_dict['url'])
        self.assertEqual(expected_body, call_dict['json'])
        self.assertEqual('POST', call_dict['method'])
        self.assertEqual(mock_request.call_count, 2)
        self.assertEqual(uuid, 'skjfhkshflsjfoisjfsjfkjshfoij')

    @patch('requests.request')
    def test_list_log_file_success_with_no_optional_parameters(self, mock_request):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/logs/{}/list'.format(TEST_DEVICE_ID)
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LIST_LOGS_UPLOAD_STATUS_SUCCESS
        mock_device_execute.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        logs_list = device.list_uploaded_files_for_device()
        call_dict = mock_request.call_args_list[1][1]
        self.assertEqual(expected_url, call_dict['url'])
        self.assertEqual('GET', call_dict['method'])
        self.assertEqual(mock_request.call_count, 2)
        self.assertTrue(len(logs_list) == 2)
        self.assertTrue(logs_list[0]['request_uuid'] == 'file-uuid')
        self.assertTrue(logs_list[1]['request_uuid'] == 'file-uuid-1')

    @patch('requests.request')
    def test_list_log_file_failure_with_invalid_sort_parameter(self, mock_request):
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device]
        device = get_client().get_device(TEST_DEVICE_ID)
        with self.assertRaises(InvalidParameterException):
            device.list_uploaded_files_for_device(sort='invalid_sort_param', reverse=True)
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_list_log_file_failure_with_invalid_optional_parameters(self, mock_request):
        expected_query_param_str = 'filter=%7B%22and%22%3A+%5B%7B%22filename%22%3A+%7B%22like%22%3A+%22%25not_found' \
                                   '%25%22%7D%7D%2C+%7B%22or%22%3A+%5B%7B%22status%22%3A+%22invalid_status%22' \
                                   '%7D%5D%7D%5D%7D&page=%7B%22number%22%3A+0%2C+%22size%22%3A+0%7D'
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LIST_LOGS_UPLOAD_STATUS_FAILURE_INVALID_OPTIONAL_PARAMETERS
        mock_device_execute.status_code = requests.codes.BAD_REQUEST
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        with self.assertRaises(BadRequestError):
            device.list_uploaded_files_for_device(paginate=True, page_size=0, page_number=0,
                                                  filter_by_filename='not_found', filter_by_status=['invalid_status'])
        call_dict = mock_request.call_args_list[1][1]
        six.assertCountEqual(self, expected_query_param_str, call_dict['url'].split('?')[1])
        self.assertEqual('GET', call_dict['method'])
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.request')
    def test_list_log_file_success_with_correct_optional_parameters(self, mock_request):
        expected_query_param_str = 'sort=-filename&filter=%7B%22and%22%3A+%5B%7B%22filename' \
                                   '%22%3A+%7B%22like%22%3A+%22%25minion%25%22%7D%7D%2C+%7B%22or%22%3A+%5B%7B' \
                                   '%22status%22%3A+%22COMPLETED%22%7D%5D%7D%5D%7D&' \
                                   'page=%7B%22number%22%3A+1%2C+%22size%22%3A+10%7D'
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LIST_LOGS_UPLOAD_STATUS_SUCCESS
        mock_device_execute.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        logs_list = device.list_uploaded_files_for_device(sort='filename', reverse=True,
                                                          paginate=True, page_size=10, page_number=1,
                                                          filter_by_filename='minion', filter_by_status=['COMPLETED'])
        call_dict = mock_request.call_args_list[1][1]
        six.assertCountEqual(self, expected_query_param_str, call_dict['url'].split('?')[1])
        self.assertEqual('GET', call_dict['method'])
        self.assertEqual(mock_request.call_count, 2)
        self.assertTrue(len(logs_list) == 2)
        self.assertTrue(logs_list[0]['request_uuid'] == 'file-uuid')
        self.assertTrue(logs_list[1]['request_uuid'] == 'file-uuid-1')

    @patch('requests.request')
    def test_upload_log_file_status_success(self, mock_request):
        log_file_uuid = 'file-uuid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/logs/{}/status/{}'. \
            format(TEST_DEVICE_ID, log_file_uuid)
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LOGS_UPLOAD_STATUS_SUCCESS
        mock_device_execute.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        status = device.get_log_upload_status(log_file_uuid)
        call_dict = mock_request.call_args_list[1][1]
        self.assertEqual(expected_url, call_dict['url'])
        self.assertEqual('GET', call_dict['method'])
        self.assertEqual(status.request_uuid, log_file_uuid)
        self.assertEqual(status.filename, 'minion')
        self.assertEqual(status.status, 'COMPLETED')

    @patch('requests.request')
    def test_upload_log_file_status_with_shared_url_success(self, mock_request):
        log_file_uuid = 'file-uuid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/logs/{}/status/{}'. \
            format(TEST_DEVICE_ID, log_file_uuid)
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LOGS_UPLOAD_STATUS_WITH_SHARED_URL_SUCCESS
        mock_device_execute.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        status = device.get_log_upload_status(log_file_uuid)
        call_dict = mock_request.call_args_list[1][1]
        self.assertEqual(expected_url, call_dict['url'])
        self.assertEqual('GET', call_dict['method'])
        self.assertEqual(status.request_uuid, log_file_uuid)
        self.assertEqual(status.filename, 'minion')
        self.assertEqual(status.status, 'COMPLETED')
        self.assertIsInstance(status['shared_urls'], list)
        for shared_url in status['shared_urls']:
            self.assertIsInstance(shared_url, SharedURL)
            self.assertIsInstance(shared_url.expiry_time, datetime)
            self.assertIsNotNone(shared_url.url)

    @patch('requests.request')
    def test_download_log_file(self, mock_request):
        log_file_uuid = 'file-uuid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/logs/{}/{}'. \
            format(TEST_DEVICE_ID, log_file_uuid)
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LOGS_DOWNLOAD_FILE
        mock_device_execute.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        signed_url = device.download_log_file(log_file_uuid)
        call_dict = mock_request.call_args_list[1][1]
        self.assertEqual(expected_url, call_dict['url'])
        self.assertEqual('GET', call_dict['method'])
        self.assertEqual(signed_url, 'https://blob.azure.com/blob/upload/file-uuid')

    @patch('requests.request')
    def test_delete_log_file(self, mock_request):
        log_file_uuid = 'file-uuid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/logs/{}/{}'. \
            format(TEST_DEVICE_ID, log_file_uuid)
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LOGS_GENERIC_RESPONSE
        mock_device_execute.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        status = device.delete_uploaded_log_file(log_file_uuid)
        call_dict = mock_request.call_args_list[1][1]
        self.assertEqual(expected_url, call_dict['url'])
        self.assertEqual('DELETE', call_dict['method'])
        self.assertTrue(status)

    @patch('requests.request')
    def test_upload_cancel_file(self, mock_request):
        log_file_uuid = 'file-uuid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/device-manager/v0/logs/{}/{}/cancel'. \
            format(TEST_DEVICE_ID, log_file_uuid)
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_device_execute = Mock()
        mock_device_execute.text = LOGS_GENERIC_RESPONSE
        mock_device_execute.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_device, mock_device_execute]
        device = get_client().get_device(TEST_DEVICE_ID)
        status = device.cancel_log_file_upload(log_file_uuid)
        call_dict = mock_request.call_args_list[1][1]
        self.assertEqual(expected_url, call_dict['url'])
        self.assertEqual('PUT', call_dict['method'])
        self.assertTrue(status)

    @patch('requests.request')
    def test_upload_cancel_file_invalid_request_uuid(self, mock_request):
        log_file_uuid = 'file-uuid'
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_cancel_response = Mock()
        mock_cancel_response.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_get_device, mock_cancel_response]
        device = get_client().get_device(TEST_DEVICE_ID)
        with self.assertRaises(LogsUUIDNotFoundException):
            device.cancel_log_file_upload(log_file_uuid)

    @patch('requests.request')
    def test_download_file_invalid_request_uuid(self, mock_request):
        log_file_uuid = 'file-uuid'
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_cancel_response = Mock()
        mock_cancel_response.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_get_device, mock_cancel_response]
        device = get_client().get_device(TEST_DEVICE_ID)
        with self.assertRaises(LogsUUIDNotFoundException):
            device.download_log_file(log_file_uuid)

    @patch('requests.request')
    def test_delete_uploaded_file_invalid_request_uuid(self, mock_request):
        log_file_uuid = 'file-uuid'
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_cancel_response = Mock()
        mock_cancel_response.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_get_device, mock_cancel_response]
        device = get_client().get_device(TEST_DEVICE_ID)
        with self.assertRaises(LogsUUIDNotFoundException):
            device.delete_uploaded_log_file(log_file_uuid)

    @patch('requests.request')
    def test_log_upload_status_for_invalid_request_uuid(self, mock_request):
        log_file_uuid = 'file-uuid'
        mock_get_device = Mock()
        mock_get_device.text = DEVICE_INFO
        mock_get_device.status_code = requests.codes.OK
        mock_cancel_response = Mock()
        mock_cancel_response.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_get_device, mock_cancel_response]
        device = get_client().get_device(TEST_DEVICE_ID)
        with self.assertRaises(LogsUUIDNotFoundException):
            device.get_log_upload_status(log_file_uuid)

    def test_upload_invalid_upload_request(self):
        with self.assertRaises(InvalidParameterException):
            LogsUploadRequest('', 'minion', True, False, {'key': 'value'})
