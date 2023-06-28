import unittest
from unittest.mock import patch, Mock

import requests

from tests.utils.client import get_client, headers
from tests.utils.user_group_responses import USER_GROUP_LIST_SUCCESS, USER_GROUP_GET_SUCCESS, \
    USER_GROUP_DELETE_SUCCESS, USER_GROUP_DELETE_FAILURE


class UserGroupTests(unittest.TestCase):
    def setUp(self):
        self.organization = 'org-guid'
        self.group = 'group-guid'

    @patch('requests.request')
    def test_list_usergroups_success(self, mock_request):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/group/list'

        mock_response = Mock()
        mock_response.text = USER_GROUP_LIST_SUCCESS
        mock_response.status_code = requests.codes.OK
        mock_request.side_effect = [mock_response]

        client = get_client()
        user_groups = client.list_usergroups(self.organization)

        new_headers = dict(headers)
        new_headers['organization'] = self.organization

        mock_request.assert_called_once_with(headers=new_headers, json=None, url=expected_url, method='GET', params={})
        self.assertIsInstance(user_groups, list)

    @patch('requests.request')
    def test_get_usergroup_success(self, mock_request):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/group/group-guid/get'

        mock_response = Mock()
        mock_response.text = USER_GROUP_GET_SUCCESS
        mock_response.status_code = requests.codes.OK
        mock_request.side_effect = [mock_response]

        client = get_client()
        user_group = client.get_usergroup(self.organization, self.group)

        new_headers = dict(headers)
        new_headers['organization'] = self.organization

        mock_request.assert_called_once_with(headers=new_headers, json=None, url=expected_url, method='GET', params={})
        self.assertIsInstance(user_group, object)

    @patch('requests.request')
    def test_delete_usergroup_success(self, mock_request):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/group/delete'

        mock_response = Mock()
        mock_response.text = USER_GROUP_DELETE_SUCCESS
        mock_response.status_code = requests.codes.OK
        mock_request.side_effect = [mock_response]

        client = get_client()
        resp = client.delete_usergroup(self.organization, self.group)

        new_headers = dict(headers)
        new_headers['organization'] = self.organization

        mock_request.assert_called_once_with(headers=new_headers, json={'guid': self.group}, url=expected_url,
                                             method='DELETE', params={})
        self.assertTrue(resp['success'])

    @patch('requests.request')
    def test_delete_usergroup_failure_group_not_found(self, mock_request):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/group/delete'

        mock_response = Mock()
        mock_response.text = USER_GROUP_DELETE_FAILURE
        mock_response.status_code = requests.codes.OK
        mock_request.side_effect = [mock_response]

        client = get_client()
        resp = client.delete_usergroup(self.organization, self.group)

        new_headers = dict(headers)
        new_headers['organization'] = self.organization

        mock_request.assert_called_once_with(headers=new_headers, json={'guid': self.group}, url=expected_url,
                                             method='DELETE', params={})
        self.assertFalse(resp['success'])

