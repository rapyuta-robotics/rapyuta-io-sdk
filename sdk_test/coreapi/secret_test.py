from __future__ import absolute_import
import unittest

from rapyuta_io import Secret, SecretConfigDocker
from sdk_test.config import Configuration
from sdk_test.util import get_logger


class TestSecret(unittest.TestCase):
    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()

    def tearDown(self):
        if hasattr(self, 'secret'):
            self.config.client.delete_secret(self.secret.guid)

    def assertSecret(self, secret):
        self.assertIsInstance(secret, Secret)
        self.assertIsNotNone(secret.guid)
        self.assertIsNotNone(secret.creator)
        self.assertIsNotNone(secret.created_at)
        self.assertIsNotNone(secret.secret_type)


    def test_create_secret_docker(self):
        self.secret = self.config.client.create_secret(Secret('docker-test', SecretConfigDocker('user','pass', 'email')))
        self.assertSecret(self.secret)

    def test_list_secret_docker(self):
        self.secret = self.config.client.create_secret(Secret('docker-test', SecretConfigDocker('user','pass', 'email')))
        secret_list = self.config.client.list_secrets()
        secret_list = [s for s in secret_list if s.guid == self.secret.guid]
        self.assertEqual(len(secret_list), 1)
    
    def test_update_secret_source_docker(self):
        self.secret = self.config.client.create_secret(Secret('docker-test', SecretConfigDocker('user','pass', 'email')))
        self.secret = self.config.client.update_secret(self.secret.guid, Secret('docker-test', SecretConfigDocker('user1','pass1', 'email1')))
        self.assertSecret(self.secret)

