# encoding: utf-8
from __future__ import absolute_import
import requests
import unittest

from mock import call, patch, Mock
from requests import Response

from rapyuta_io.utils.error import APIError
from rapyuta_io.utils.rest_client import RestClient, HttpMethod
from requests.exceptions import RequestException
from six.moves import range


class RESTClientTests(unittest.TestCase):
    PAYLOAD = {'key1': {'subkey1': 'subval1', 'subkey2': 1.2}}
    CALL = call(json=None, method='GET', url='request_rul', headers={'headers': 'test'}, params={})
    CALL_PAYLOAD = call(method='GET', url='request_rul', headers={'headers': 'test'}, json=PAYLOAD)

    @patch('requests.Response', spec=Response)
    @patch('requests.request')
    def test_ok(self, req_mock, response):
        response.status_code = 200
        req_mock.return_value = response
        c = RestClient('request_rul').method(HttpMethod.POST).headers({'headers': 'test'}).\
            query_param({'query': 'string'})
        c.execute()
        req_mock.assert_called_once_with(headers={'headers': 'test'}, method='POST', url='request_rul',
                                         params={'query': 'string'}, json=None)

    @patch('rapyuta_io.utils.rest_client.WAIT_TIME_IN_SEC', 0.01)
    @patch('requests.Response', spec=Response)
    @patch('requests.request')
    def test_retries(self, req_mock, response):
        response.status_code = requests.codes.OK
        response.text = ''
        req_mock.return_value = response
        rest_client = RestClient('request_rul').retry(4).headers({'headers': 'test'})
        rest_client.execute()
        self.assertEqual(req_mock.call_count, 1)
        req_mock.assert_called_once_with(method='GET', url='request_rul',
                                         headers={'headers': 'test'}, params={},
                                         json=None)

    @patch('rapyuta_io.utils.rest_client.WAIT_TIME_IN_SEC', 0.01)
    @patch('requests.request')
    def test_retries_internal_server_error(self, req_mock):
        response = Mock()
        response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        req_mock.return_value = response
        rest_client = RestClient('request_rul').retry(4).method(HttpMethod.GET).headers({'headers': 'test'})
        rest_client.execute()
        self.assertEqual(req_mock.call_count, 5)
        req_mock.assert_has_calls([self.CALL for _ in range(5)])

    @patch('requests.request')
    def test_no_retries_non_get_internal_server_error(self, req_mock):
        response = Mock()
        response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        req_mock.return_value = response
        rest_client = RestClient('request_rul').retry(4).method(HttpMethod.PATCH).headers({'headers': 'test'})
        rest_client.execute()
        self.assertEqual(req_mock.call_count, 1)
        req_mock.assert_called_once_with(method='PATCH', url='request_rul',
                                         headers={'headers': 'test'}, params={},
                                         json=None)

    @patch('requests.Response', spec=Response)
    @patch('requests.request')
    def test_ok_payload(self, req_mock, response):
        response.status_code = requests.codes.OK
        req_mock.return_value = response
        c = RestClient('request_rul').method(HttpMethod.POST).headers({'headers': 'test'})
        c.execute(self.PAYLOAD)
        req_mock.assert_called_once_with(method='POST', url='request_rul',
                                         headers={'headers': 'test'}, params={},
                                         json=self.PAYLOAD)

    @patch('rapyuta_io.utils.rest_client.WAIT_TIME_IN_SEC', 0.01)
    @patch('requests.Response', spec=Response)
    @patch('requests.request')
    def test_retries_payload(self, req_mock, response):
        response.status_code = requests.codes.OK
        response.text = ''
        req_mock.return_value = response
        c = RestClient('request_rul').retry(1).headers({'headers': 'test'})
        c.execute(self.PAYLOAD)
        self.assertEqual(req_mock.call_count, 1)
        req_mock.assert_called_once_with(method='GET', url='request_rul',
                                         headers={'headers': 'test'}, params={},
                                         json=self.PAYLOAD)

    @patch('rapyuta_io.utils.rest_client.WAIT_TIME_IN_SEC', 0.01)
    @patch('requests.request')
    def test_exception(self, req_mock):
        req_mock.side_effect = RequestException
        c = RestClient('request_rul').retry(4).headers({'headers': 'test'})
        with self.assertRaises(APIError):
            c.execute()
        req_mock.assert_has_calls([self.CALL for _ in range(5)])
