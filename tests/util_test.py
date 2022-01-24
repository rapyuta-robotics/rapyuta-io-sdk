from __future__ import absolute_import
import unittest

from rapyuta_io.utils import prepend_bearer_to_auth_token, ParameterMissingException
from rapyuta_io.utils.utils import create_auth_header, get_error, validate_key_value


class UtilTests(unittest.TestCase):

    def test_prepend_bearer_to_auth_token_ok(self):
        expected_value = 'Bearer auth_token'
        auth_token = prepend_bearer_to_auth_token('auth_token')
        self.assertEqual(expected_value, auth_token)

    def test_prepend_bearer_to_auth_token_bearer_already_exists_ok(self):
        expected_value = 'Bearer auth_token'
        auth_token = prepend_bearer_to_auth_token('Bearer auth_token')
        self.assertEqual(expected_value, auth_token)

    def test_create_auth_project_header_ok(self):
        expected_header = {
            'Authorization': 'auth_token',
            'project': 'test_project'
        }
        actual_header = create_auth_header('auth_token', 'test_project')
        self.assertEqual(expected_header, actual_header)

    def test_get_error_ok(self):
        expected_error = 'something went wrong'
        response_data = ''' {
                    "status": "error",
                    "response": { "data": {}, "error": "something went wrong" } }'''
        error_msg = get_error(response_data)
        self.assertEqual(expected_error, error_msg)

    def test_get_error_empty_error_ok(self):
        expected_error = ''
        response_data = ''' {
                    "status": "error",
                    "response": { "data": {}} }'''
        error_msg = get_error(response_data)
        self.assertEqual(expected_error, error_msg)

    def test_get_error_empty_data_ok(self):
        expected_error = ''
        response_data = ''
        error_msg = get_error(response_data)
        self.assertEqual(expected_error, error_msg)

    def test_validate_key_value_ok(self):
        label = {'id': 'id', 'key': 'key', 'value': 'value'}
        validate_key_value(label)
        self.assertTrue(True)

    def test_validate_key_value_failure_case(self):
        label = {'key': 'key'}
        with self.assertRaises(ParameterMissingException):
            validate_key_value(label)
