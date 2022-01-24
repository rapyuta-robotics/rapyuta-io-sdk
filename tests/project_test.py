from __future__ import absolute_import
import requests
import unittest

from mock import patch, call, Mock

from rapyuta_io.clients.project import Project
from rapyuta_io.utils import InvalidParameterException, InternalServerError
from tests.utils.client import get_client, headers, AUTH_TOKEN
from tests.utils.projects_responses import PROJECT_CREATE_SUCCESS, PROJECT_GET_SUCCESS, PROJECT_LIST_SUCCESS


class ProjectTests(unittest.TestCase):
    def test_bad_names_length(self):
        expected_err_msg = 'length of name must be between 3 and 15 characters'
        with self.assertRaises(InvalidParameterException) as e:
            Project('a')
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_bad_names_type(self):
        expected_err_msg = 'name must be a string'
        with self.assertRaises(InvalidParameterException) as e:
            Project(name=123)
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_bad_names_invalid_characters(self):
        expected_err_msg = 'name can have alphabets, numbers or - only'
        with self.assertRaises(InvalidParameterException) as e:
            Project('4@#1$')
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_create_project_invalid_project_type(self):
        expected_err_msg = 'project must be non-empty and of type rapyuta_io.clients.project.Project'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_project('invalid-project-type')

        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_create_project_success(self, mock_request):
        project = Project('test-project')
        client = get_client()
        expected_payload = {'name': 'test-project'}
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/create'
        mock_project = Mock()
        mock_project.text = PROJECT_CREATE_SUCCESS
        mock_project.status_code = requests.codes.OK
        mock_request.side_effect = [mock_project]
        result = client.create_project(project)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params={}),
        ])
        self.assertIsInstance(result, Project)
        self.assertTrue(hasattr(result, 'guid'))

    @patch('requests.request')
    def test_create_project_server_error(self, mock_request):
        project = Project('test-project')
        client = get_client()
        expected_payload = {'name': 'test-project'}
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/create'
        mock_project = Mock()
        mock_project.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_project]
        with self.assertRaises(InternalServerError) as e:
            client.create_project(project)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params={}),
        ])

    @patch('requests.request')
    def test_get_project_success(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/project-guid/get'
        mock_project = Mock()
        mock_project.status_code = requests.codes.OK
        mock_project.text = PROJECT_GET_SUCCESS
        mock_request.side_effect = [mock_project]
        result = client.get_project('project-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={})
        ])
        self.assertIsInstance(result, Project)
        self.assertTrue(hasattr(result, 'guid'))

    @patch('rapyuta_io.utils.rest_client.DEFAULT_RETRY_COUNT', 0)
    @patch('requests.request')
    def test_get_project_server_error(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/project-guid/get'
        mock_project = Mock()
        mock_project.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_project]
        with self.assertRaises(InternalServerError):
            client.get_project('project-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={})
        ])

    @patch('requests.request')
    def test_list_projects_success(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/list'
        mock_projects = Mock()
        mock_projects.status_code = requests.codes.OK
        mock_projects.text = PROJECT_LIST_SUCCESS
        mock_request.side_effect = [mock_projects]
        proj_list = client.list_projects()
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={})
        ])
        self.assertIsInstance(proj_list, list)
        for proj in proj_list:
            self.assertIsInstance(proj, Project)
            self.assertTrue(hasattr(proj, 'guid'))

    @patch('rapyuta_io.utils.rest_client.DEFAULT_RETRY_COUNT', 0)
    @patch('requests.request')
    def test_list_projects_server_error(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/list'
        mock_projects = Mock()
        mock_projects.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_projects]
        with self.assertRaises(InternalServerError):
            client.list_projects()
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params={})
        ])

    @patch('requests.request')
    def test_delete_project_from_client_success(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/delete'
        expected_payload = {'guid': 'project-guid'}
        mock_project = Mock()
        mock_project.status_code = requests.codes.OK
        mock_project.text = '{"success": true, "error": ""}'
        mock_request.side_effect = [mock_project]
        client.delete_project('project-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    @patch('requests.request')
    def test_delete_project_from_client_no_success(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/delete'
        expected_payload = {'guid': 'project-guid'}
        mock_project = Mock()
        mock_project.status_code = requests.codes.OK
        mock_project.text = '{"success": false, "error": ""}'
        mock_request.side_effect = [mock_project]
        result = client.delete_project('project-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])
        self.assertFalse(result)

    @patch('requests.request')
    def test_delete_project_from_client_sever_error(self, mock_request):
        client = get_client()
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/delete'
        expected_payload = {'guid': 'project-guid'}
        mock_project = Mock()
        mock_project.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_project]
        with self.assertRaises(InternalServerError):
            client.delete_project('project-guid')
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    @patch('requests.request')
    def test_delete_method_success(self, mock_request):
        proj = Project('test-project')
        setattr(proj, '_core_api_host', 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io')
        setattr(proj, '_auth_token', 'Bearer ' + AUTH_TOKEN)
        setattr(proj, 'guid', 'test_project')
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/delete'
        expected_payload = {'guid': 'test_project'}
        mock_project = Mock()
        mock_project.status_code = requests.codes.OK
        mock_project.text = '{"success": true, "error": ""}'
        mock_request.side_effect = [mock_project]
        proj.delete()
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    @patch('requests.request')
    def test_delete_method_server_error(self, mock_request):
        proj = Project('test-project')
        setattr(proj, '_core_api_host', 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io')
        setattr(proj, '_auth_token', 'Bearer ' + AUTH_TOKEN)
        setattr(proj, 'guid', 'test_project')
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/delete'
        expected_payload = {'guid': 'test_project'}
        mock_project = Mock()
        mock_project.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_project]
        with self.assertRaises(InternalServerError):
            proj.delete()
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    def test_delete_local_project_error(self):
        proj = Project('test-project')
        expected_err_msg = 'Project must be created first'
        with self.assertRaises(InvalidParameterException) as e:
            proj.delete()
        self.assertEqual(expected_err_msg, str(e.exception))

    @patch('requests.request')
    def test_add_user_to_project_no_success(self, mock_request):
        client = get_client()
        dummy_project_guid = 'dummy-project-guid'
        user_guid = 'user-guid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/{}/adduser'.format(
            dummy_project_guid)
        expected_payload = {'userGUID': user_guid}
        mock_add_user_to_project = Mock()
        mock_add_user_to_project.status_code = requests.codes.OK
        mock_add_user_to_project.text = '{"success": false, "error": "project not found"}'
        mock_request.side_effect = [mock_add_user_to_project]
        client.add_user_to_project(project_guid=dummy_project_guid, user_guid=user_guid)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='PUT', params={})
        ])

    @patch('requests.request')
    def test_add_user_to_project_server_error(self, mock_request):
        client = get_client()
        project_guid = 'project-guid'
        user_guid = 'user-guid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/{}/adduser'.format(
            project_guid)
        expected_payload = {'userGUID': user_guid}
        mock_add_user_to_project = Mock()
        mock_add_user_to_project.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_add_user_to_project]
        with self.assertRaises(InternalServerError):
            client.add_user_to_project(project_guid=project_guid, user_guid=user_guid)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='PUT', params={})
        ])

    @patch('requests.request')
    def test_add_user_to_project_success(self, mock_request):
        client = get_client()
        project_guid = 'project-guid'
        user_guid = 'user-guid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/{}/adduser'.format(
            project_guid)
        expected_payload = {'userGUID': user_guid}
        mock_add_user_to_project = Mock()
        mock_add_user_to_project.status_code = requests.codes.OK
        mock_add_user_to_project.text = '{"success": true, "error": ""}'
        mock_request.side_effect = [mock_add_user_to_project]
        client.add_user_to_project(project_guid=project_guid, user_guid=user_guid)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='PUT', params={})
        ])

    @patch('requests.request')
    def test_remove_user_from_project_no_success(self, mock_request):
        client = get_client()
        dummy_project_guid = 'dummy-project-guid'
        user_guid = 'user-guid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/{}/removeuser'.format(
            dummy_project_guid)
        expected_payload = {'userGUID': user_guid}
        mock_remove_user_from_project = Mock()
        mock_remove_user_from_project.status_code = requests.codes.OK
        mock_remove_user_from_project.text = '{"success": false, "error": "project not found"}'
        mock_request.side_effect = [mock_remove_user_from_project]
        client.remove_user_from_project(project_guid=dummy_project_guid, user_guid=user_guid)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    @patch('requests.request')
    def test_remove_user_from_project_server_error(self, mock_request):
        client = get_client()
        project_guid = 'project-guid'
        user_guid = 'user-guid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/{}/removeuser'.format(
            project_guid)
        expected_payload = {'userGUID': user_guid}
        mock_remove_user_from_project = Mock()
        mock_remove_user_from_project.status_code = requests.codes.INTERNAL_SERVER_ERROR
        mock_request.side_effect = [mock_remove_user_from_project]
        with self.assertRaises(InternalServerError):
            client.remove_user_from_project(project_guid=project_guid, user_guid=user_guid)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])

    @patch('requests.request')
    def test_remove_user_from_project_success(self, mock_request):
        client = get_client()
        project_guid = 'project-guid'
        user_guid = 'user-guid'
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/project/{}/removeuser'.format(
            project_guid)
        expected_payload = {'userGUID': user_guid}
        mock_remove_user_from_project = Mock()
        mock_remove_user_from_project.status_code = requests.codes.OK
        mock_remove_user_from_project.text = '{"success": true, "error": ""}'
        mock_request.side_effect = [mock_remove_user_from_project]
        client.remove_user_from_project(project_guid=project_guid, user_guid=user_guid)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='DELETE', params={})
        ])
