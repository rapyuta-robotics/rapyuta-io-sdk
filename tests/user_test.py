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
                                             url=expected_get_user_url, method='GET', params={})

        self.assertIsInstance(user, User)
        for project in user.projects:
            self.assertIsInstance(project, Project)
        self.assertIsInstance(user.organization, Organization)
        self.assertIsInstance(user.organization.country, Country)

        self.assertTrue(len(user.projects))

        self.assertIsNotNone(user.guid)
        for project in user.projects:
            self.assertIsNotNone(project.guid)
        self.assertIsNotNone(user.organization.guid)

        self.assertEqual(user.state, UserState.ACTIVATED)
        self.assertEqual(user.organization.state, OrganizationState.ACTIVATED)
