from __future__ import absolute_import
import unittest

from rapyuta_io import Secret, SecretConfigSourceSSHAuth, SecretConfigSourceBasicAuth, \
    SecretConfigDocker
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

    def test_create_secret_source_ssh_auth(self):
        self.secret = self.config.client.create_secret(Secret('ssh-auth-test', SecretConfigSourceSSHAuth('test-ssh-key')))
        self.assertSecret(self.secret)

    def test_create_secret_source_http_auth(self):
        self.secret = self.config.client.create_secret(Secret('basic-auth-test', SecretConfigSourceBasicAuth('user', 'pass')))
        self.assertSecret(self.secret)

    def test_create_secret_docker(self):
        self.secret = self.config.client.create_secret(Secret('docker-test', SecretConfigDocker('user','pass', 'email')))
        self.assertSecret(self.secret)

    def test_list_secret_docker(self):
        self.secret = self.config.client.create_secret(Secret('ssh-auth-test', SecretConfigSourceSSHAuth('test-ssh-key')))
        secret_list = self.config.client.list_secrets()
        secret_list = [s for s in secret_list if s.guid == self.secret.guid]
        self.assertEqual(len(secret_list), 1)

