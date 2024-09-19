from __future__ import absolute_import
import unittest

from rapyuta_io.clients.organization import Organization, Country, OrganizationState
from rapyuta_io.clients.project import User, UserState
from sdk_test.config import Configuration
from sdk_test.util import get_logger


class TestUser(unittest.TestCase):
    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()

    def test_get_authenticated_user_details(self):
        self.user = self.config.client.get_authenticated_user()
        
        self.assertIsInstance(self.user, User)
        self.assertIsInstance(self.user.organization, Organization)
        self.assertIsInstance(self.user.organization.country, Country)

        self.assertTrue(len(self.user.projects))

        self.assertIsNotNone(self.user.guid)
        for project in self.user.projects:
            self.assertIsNotNone(project.guid)
        self.assertIsNotNone(self.user.organization.guid)

        self.assertEqual(self.user.state, UserState.ACTIVATED)
        self.assertEqual(self.user.organization.state, OrganizationState.ACTIVATED)

        self.assertTrue(len(self.user.organizations))
        for org in self.user.organizations:
            self.assertIsNotNone(org.guid)
            self.assertIsInstance(org, Organization)

    def test_get_user_organizations(self):
        self.organizations = self.config.client.get_user_organizations()
        for org in self.organizations:
            self.assertIsNotNone(org.guid)
            self.assertIsInstance(org, Organization)
