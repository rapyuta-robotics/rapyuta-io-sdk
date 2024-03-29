from __future__ import absolute_import

import unittest

from rapyuta_io import Client, Project, Secret, SecretConfigDocker
from rapyuta_io.utils import BadRequestError
from rapyuta_io.utils.utils import generate_random_value
from sdk_test.config import Configuration
from sdk_test.util import get_logger


class TestProject(unittest.TestCase):
    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()

    def tearDown(self):
        if hasattr(self, 'project'):
            self.config.client.delete_project(self.project.guid)

    def test_create_project(self):
        p = Project(
            'test-{}'.format(generate_random_value(5)),
            organization_guid=self.config.organization_guid
        )
        self.project = self.config.client.create_project(p)
        self.assertIsInstance(self.project, Project)
        self.assertIsNotNone(self.project.guid)
        self.assertIsNotNone(self.project.creator)
        self.assertIsNotNone(self.project.created_at)
        self.assertIsNotNone(self.project.users)

    def test_list_project(self):
        p = Project(
            'test-{}'.format(generate_random_value(5)),
            organization_guid=self.config.organization_guid
        )
        self.project = self.config.client.create_project(p)
        project_list = self.config.client.list_projects()
        project_list = [p for p in project_list if p.guid == self.project.guid]
        self.assertEqual(len(project_list), 1)

    def test_client_without_project(self):
        auth = self.config.get_auth_token()
        client = Client(auth)
        self.assertRaises(
            BadRequestError,
            lambda: client.create_secret(
                Secret('test-secret', SecretConfigDocker(username='username', password='password', email='test@example.com',
                                           registry='quay.io'))
            )
        )
