from __future__ import absolute_import
import requests
import unittest
from mock import patch, Mock
from tests.utils.client import get_client, headers
from tests.utils.user_response import GET_USER_RESPONSE
from rapyuta_io.clients.project import Project, User, UserState
from rapyuta_io.clients.organization import Organization, OrganizationState, Country


class UserTests(unittest.TestCase):

    @patch('requests.request')
    def test_get_authenticated_user_details_success(self, mock_request):
        expected_get_user_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/user/me/get'

        mock_get_user_request = Mock()
        mock_get_user_request.text = GET_USER_RESPONSE
        mock_get_user_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_user_request]

        client = get_client()
        user = client.get_authenticated_user()
        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_get_user_url, method='GET', params={},
                                             timeout=(30, 150))

        self.assertIsInstance(user, User)
        self.assertIsNotNone(user.guid)
        self.assertEqual(user.state, UserState.ACTIVATED)

        for project in user.projects:
            self.assertIsInstance(project, Project)
            self.assertIsNotNone(project.guid)
        self.assertTrue(len(user.projects))

        self.assertIsInstance(user.organization, Organization)
        self.assertIsInstance(user.organization.country, Country)
        self.assertIsNotNone(user.organization.guid)
        self.assertEqual(user.organization.state, OrganizationState.ACTIVATED)

        self.assertTrue(hasattr(user, 'organizations'))
        self.assertTrue(len(user.organizations))

    @patch('requests.request')
    def test_get_user_organizations_success(self, mock_request):
        expected_get_user_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/user/me/get'

        mock_get_user_request = Mock()
        mock_get_user_request.text = GET_USER_RESPONSE
        mock_get_user_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_user_request]

        client = get_client()
        organizations = client.get_user_organizations()
        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_get_user_url, method='GET', params={},
                                             timeout=(30, 150))

        self.assertTrue(len(organizations))
        for org in organizations:
            self.assertIsInstance(org, Organization)
            self.assertIsNotNone(org.guid)

