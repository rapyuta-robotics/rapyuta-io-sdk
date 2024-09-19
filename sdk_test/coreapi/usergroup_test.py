import unittest

from rapyuta_io import UserGroup

from sdk_test.config import Configuration


class TestUserGroup(unittest.TestCase):
    USERGROUP_NAME = 'sdk_test_usergroup'
    USERGROUP_DESCRIPTION = 'Sample usergroup for SDK tests'
    PROJECT_NAME = 'test-project'

    @classmethod
    def setUpClass(cls):
        cls.usergroup_create_payload = {
            'name': cls.USERGROUP_NAME,
            'description': cls.USERGROUP_DESCRIPTION,
            'members': [],
            'admins': [],
            'projects': []
        }
        cls.usergroup_upload_payload = {
            'name': cls.USERGROUP_NAME,
            'description': '',
            'guid': '',
            'update': {
                'members': {'add': [], 'remove': []},
                'projects': {'add': [], 'remove': []},
                'admins': {'add': [], 'remove': []},
            }
        }

    def setUp(self):
        self.config = Configuration()

    def tearDown(self):
        if hasattr(self, 'usergroup'):
            self.config.client.delete_usergroup(self.config.organization_guid, self.usergroup.guid)
        if hasattr(self, 'project'):
            self.config.client.delete_project(self.project.guid)

    def assertUserGroup(self, usergroup):
        self.assertIsInstance(usergroup, UserGroup)
        self.assertIsNotNone(usergroup.guid)
        self.assertIsNotNone(usergroup.members)
        self.assertIsNotNone(usergroup.admins)

    def test_create_usergroup(self):
        payload = self.usergroup_create_payload
        self.usergroup = self.config.client.create_usergroup(self.config.organization_guid, payload)

        self.assertUserGroup(self.usergroup)
        self.assertIsNone(self.usergroup.projects)
        self.assertEqual(self.usergroup.name, self.USERGROUP_NAME)
        self.assertEqual(len(self.usergroup.admins), 1)
        self.assertEqual(len(self.usergroup.members), 1)

    def test_list_usergroup(self):
        payload = self.usergroup_create_payload
        self.usergroup = self.config.client.create_usergroup(self.config.organization_guid, payload)
        usergroup_list = self.config.client.list_usergroups(self.config.organization_guid)

        self.assertGreaterEqual(len(usergroup_list), 1)

        self.assertEqual(usergroup_list[0].description, self.USERGROUP_DESCRIPTION)
        self.assertIsNone(self.usergroup.projects)
        self.assertEqual(len(usergroup_list[0].admins), 1)
        self.assertEqual(len(usergroup_list[0].members), 1)

    def test_create_and_fetch_usergroup(self):
        payload = self.usergroup_create_payload
        self.usergroup = self.config.client.create_usergroup(self.config.organization_guid, payload)
        fetched_usergroup = self.config.client.get_usergroup(self.config.organization_guid, self.usergroup.guid)

        self.assertEqual(self.usergroup.guid, fetched_usergroup.guid)
        self.assertEqual(len(self.usergroup.members), len(fetched_usergroup.members))
        self.assertEqual(len(self.usergroup.admins), len(fetched_usergroup.admins))
        self.assertIsNone(self.usergroup.projects)
        self.assertIsNone(fetched_usergroup.projects)

    def test_update_usergroup(self):
        payload = self.usergroup_create_payload
        self.usergroup = self.config.client.create_usergroup(self.config.organization_guid, payload)

        self.project_guid = self.config.v2_client.create_project({
            'metadata': {
                'name': self.PROJECT_NAME,
                'organizationGUID': self.config.organization_guid
            },
        })

        upload_payload = self.usergroup_upload_payload
        upload_payload['update']['projects']['add'].append({
            'guid': self.project_guid
        })

        self.usergroup = self.config.client.update_usergroup(self.config.organization_guid, self.usergroup.guid,
                                                             upload_payload)

        self.assertEqual(len(self.usergroup.projects), 1)
        self.assertEqual(len(self.usergroup.admins), 1)
        self.assertEqual(len(self.usergroup.members), 1)
