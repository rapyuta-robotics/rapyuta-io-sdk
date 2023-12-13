from __future__ import absolute_import
import base64
from http.client import INTERNAL_SERVER_ERROR
import requests
import unittest

from mock import Mock, call, patch

from rapyuta_io.clients.secret import SecretType, \
    SecretConfigDocker, DOCKER_HUB_REGISTRY, Secret
from rapyuta_io.utils import InvalidParameterException, InternalServerError, ResourceNotFoundError
from tests.utils.client import get_client, headers, AUTH_TOKEN
from tests.utils.secrets_responses import SECRET_CREATE_SUCCESS, SECRET_LIST_SUCCESS, SECRET_UPDATE_SUCCESS


class SecretConfigTests(unittest.TestCase):
    def test_bad_secret_config_docker_empty_username(self):
        expected_err_msg = 'username cannot be empty'
        with self.assertRaises(InvalidParameterException) as e:
            SecretConfigDocker(username='', password='password', email='test@example.com')
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_bad_secret_config_docker_empty_password(self):
        expected_err_msg = 'password cannot be empty'
        with self.assertRaises(InvalidParameterException) as e:
            SecretConfigDocker(username='username', password='', email='test@example.com')
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_bad_secret_config_docker_empty_email(self):
        expected_err_msg = 'email cannot be empty'
        with self.assertRaises(InvalidParameterException) as e:
            SecretConfigDocker(username='username', password='password', email='')
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_bad_secret_config_docker_empty_registry(self):
        expected_err_msg = 'registry cannot be empty'
        with self.assertRaises(InvalidParameterException) as e:
            SecretConfigDocker(username='username', password='password', email='test@example.com', registry='')
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_secret_config_docker_default_registry(self):
        secret_config = SecretConfigDocker(username='username', password='password', email='test@example.com')
        docker_config = '{"https://index.docker.io/v1/": {"username": "username", "password": "password", "email": "test@example.com", "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="}}'
        expected_serialize = {'.dockercfg': base64.b64encode(docker_config.encode()).decode()}
        self.assertEqual('username', secret_config.username)
        self.assertEqual('password', secret_config.password)
        self.assertEqual('test@example.com', secret_config.email)
        self.assertEqual(DOCKER_HUB_REGISTRY, secret_config.registry)
        self.assertEqual(SecretType.DOCKER, secret_config.get_type())
        self.assertEqual(expected_serialize, secret_config.serialize())

    def test_secret_config_docker_private_registry(self):
        secret_config = SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io')
        docker_config = '{"quay.io": {"username": "username", "password": "password", "email": "test@example.com", "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="}}'
        expected_serialize = {'.dockercfg': base64.b64encode(docker_config.encode()).decode()}
        self.assertEqual('username', secret_config.username)
        self.assertEqual('password', secret_config.password)
        self.assertEqual('test@example.com', secret_config.email)
        self.assertEqual('quay.io', secret_config.registry)
        self.assertEqual(SecretType.DOCKER, secret_config.get_type())
        self.assertEqual(expected_serialize, secret_config.serialize())


class SecretTests(unittest.TestCase):
    def test_bad_secret_name_length(self):
        expected_err_msg = 'length of name must be between 3 and 253 characters'
        with self.assertRaises(InvalidParameterException) as e:
            Secret(name='a' * 300, secret_config=SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_bad_secret_name_pattern(self):
        expected_err_msg = 'name must consist of lower case alphanumeric characters or - and must start and end with ' \
                           'an alphanumeric character'
        with self.assertRaises(InvalidParameterException) as e:
            Secret(name='-SECRET-', secret_config=SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_bad_secret_name_type(self):
        expected_err_msg = 'name must be a string'
        with self.assertRaises(InvalidParameterException) as e:
            Secret(name=123, secret_config=SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        self.assertEqual(expected_err_msg, str(e.exception))

    @patch('requests.request')
    def test_create_secret_internal_server_error(self, mock_request):
        secret = Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        docker_config = '{"quay.io": {"username": "username", "password": "password", "email": "test@example.com", "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="}}'
        client = get_client()
        expected_payload = {
            'type': str(SecretType.DOCKER),
            'data': {'.dockercfg': base64.b64encode(docker_config.encode()).decode()},
            'name': 'test-secret'
        }
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/create'
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_secret]
        with self.assertRaises(InternalServerError) as e:
            client.create_secret(secret)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params={}),
        ])

    @patch('requests.request')
    def test_create_secret_success(self, mock_request):
        secret = Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        docker_config = '{"quay.io": {"username": "username", "password": "password", "email": "test@example.com", "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="}}'
        client = get_client()
        expected_payload = {
            'type': str(SecretType.DOCKER),
            'data': {'.dockercfg': base64.b64encode(docker_config.encode()).decode()},
            'name': 'test-secret'
        }
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/create'
        mock_secret = Mock()
        mock_secret.text = SECRET_CREATE_SUCCESS
        mock_secret.status_code = requests.codes.OK
        mock_request.side_effect = [mock_secret]
        result = client.create_secret(secret)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params={}),
        ])
        self.assertIsInstance(result, Secret)

    @patch('rapyuta_io.utils.rest_client.DEFAULT_RETRY_COUNT', 0)
    @patch('requests.request')
    def test_get_secret_internal_server_error(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/secret-guid/get'
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_secret]
        with self.assertRaises(InternalServerError):
            client.get_secret('secret-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={}),
        ])

    @patch('requests.request')
    def test_get_secret_not_found(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/secret-guid/get'
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_secret]
        with self.assertRaises(ResourceNotFoundError):
            client.get_secret('secret-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={}),
        ])

    @patch('requests.request')
    def test_get_secret_success(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/secret-guid/get'
        mock_secret = Mock()
        mock_secret.text = SECRET_CREATE_SUCCESS
        mock_secret.status_code = requests.codes.OK
        mock_request.side_effect = [mock_secret]
        result = client.get_secret('secret-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={}),
        ])
        self.assertIsInstance(result, Secret)

    @patch('rapyuta_io.utils.rest_client.DEFAULT_RETRY_COUNT', 0)
    @patch('requests.request')
    def test_list_secret_internal_server_error(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/list'
        mock_secrets = Mock()
        mock_secrets.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_secrets]
        with self.assertRaises(InternalServerError):
            client.list_secrets()
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={})
        ])

    @patch('requests.request')
    def test_list_secret_success(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/list'
        mock_secrets = Mock()
        mock_secrets.status_code = requests.codes.OK
        mock_secrets.text = SECRET_LIST_SUCCESS
        mock_request.side_effect = [mock_secrets]
        secret_list = client.list_secrets()
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={})
        ])
        self.assertIsInstance(secret_list, list)
        for secret in secret_list:
            self.assertIsInstance(secret, Secret)

    @patch('requests.request')
    def test_delete_secret_internal_server_error(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/delete'
        expected_payload = {'guid': 'secret-guid'}
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_secret]
        with self.assertRaises(InternalServerError):
            client.delete_secret('secret-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    @patch('requests.request')
    def test_delete_secret_no_success(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/delete'
        expected_payload = {'guid': 'secret-guid'}
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.OK
        mock_secret.text = '{"success": false, "error": ""}'
        mock_request.side_effect = [mock_secret]
        result = client.delete_secret('secret-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])
        self.assertFalse(result)

    @patch('requests.request')
    def test_delete_secret_success(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/delete'
        expected_payload = {'guid': 'secret-guid'}
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.OK
        mock_secret.text = '{"success": true, "error": ""}'
        mock_request.side_effect = [mock_secret]
        client.delete_secret('secret-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    @patch('requests.request')
    def test_delete_method_internal_server_error(self, mock_request):
        secret = Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com'))
        setattr(secret, '_core_api_host', 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io')
        setattr(secret, '_auth_token', 'Bearer ' + AUTH_TOKEN)
        setattr(secret, '_project', 'test_project')
        setattr(secret, 'guid', 'secret-guid')
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/delete'
        expected_payload = {'guid': 'secret-guid'}
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_secret]
        with self.assertRaises(InternalServerError):
            secret.delete()
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    def test_delete_method_invalid_parameter(self):
        secret = Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com'))
        expected_err_msg = 'Secret must be created first'
        setattr(secret, 'guid', 'secret-guid')
        with self.assertRaises(InvalidParameterException) as e:
            secret.delete()
        self.assertEqual(expected_err_msg, str(e.exception))

    @patch('requests.request')
    def test_delete_method_success(self, mock_request):
        secret = Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        setattr(secret, '_core_api_host', 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io')
        setattr(secret, '_auth_token', 'Bearer ' + AUTH_TOKEN)
        setattr(secret, '_project', 'test_project')
        setattr(secret, 'guid', 'secret-guid')
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/delete'
        expected_payload = {'guid': 'secret-guid'}
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.OK
        mock_secret.text = '{"success": true, "error":""}'
        mock_request.side_effect = [mock_secret]
        secret.delete()
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    @patch('requests.request')
    def test_update_method_success(self, mock_request):
        secret = Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        docker_config = '{"quay.io": {"username": "username", "password": "password", "email": "test@example.com", "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="}}'
        client = get_client()
        expected_payload = {
            'type': str(SecretType.DOCKER),
            'data': {'.dockercfg': base64.b64encode(docker_config.encode()).decode()},
            'name': 'test-secret'
        }
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/secret-guid/update'
        mock_secret = Mock()
        mock_secret.text = SECRET_UPDATE_SUCCESS
        mock_secret.status_code = requests.codes.OK
        mock_request.side_effect = [mock_secret]
        result = client.update_secret('secret-guid', secret)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='PUT', params={}),
        ])
        self.assertIsInstance(result, Secret)
    
    @patch('requests.request')
    def test_update_method_internal_server_error(self, mock_request):
        secret = Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        docker_config = '{"quay.io": {"username": "username", "password": "password", "email": "test@example.com", "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="}}'
        client = get_client()
        expected_payload = {
            'type': str(SecretType.DOCKER),
            'data': {'.dockercfg': base64.b64encode(docker_config.encode()).decode()},
            'name': 'test-secret'
        }
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/secret-guid/update'
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_secret]
        with self.assertRaises(InternalServerError) as e:
            client.update_secret("secret-guid", secret)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='PUT', params={}),
        ])
    
    @patch('requests.request')
    def test_update_method_not_found_error(self, mock_request):
        secret = Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
        docker_config = '{"quay.io": {"username": "username", "password": "password", "email": "test@example.com", "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="}}'
        client = get_client()
        expected_payload = {
            'type': str(SecretType.DOCKER),
            'data': {'.dockercfg': base64.b64encode(docker_config.encode()).decode()},
            'name': 'test-secret'
        }
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/secret/secret-guid/update'
        mock_secret = Mock()
        mock_secret.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_secret]
        with self.assertRaises(ResourceNotFoundError) as e:
            client.update_secret("secret-guid", secret)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='PUT', params={}),
        ])