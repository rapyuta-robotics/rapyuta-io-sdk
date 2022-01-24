from __future__ import absolute_import
from unittest import TestCase

import os
import hashlib

from tempfile import mkdtemp
from shutil import rmtree, copyfile

from sdk_test.config import Configuration


class ConfigurationTestCase(TestCase):
    def setUp(self):
        self.config = Configuration()
        self.tmp_dir = mkdtemp()
        self.download_tmp_dir = mkdtemp()
        self.config_dir = 'test_files'
        self.config_dir_path = os.path.join(os.path.dirname(__file__), '..', self.config_dir)
        self.tree_names = ['warehouse']
        self.files = (
            'warehouse',
            'warehouse/device.yaml',
            'warehouse/lena.png',
            'warehouse/robot_type',
            'warehouse/robot_type/magni',
            'warehouse/robot_type/magni/lena.png',
            'warehouse/robot_type/magni/device.yaml',
        )

    def tearDown(self):
        rmtree(self.tmp_dir)
        rmtree(self.download_tmp_dir)

    def setup_local_configuration_structure(self):
        for file in self.files:
            if '.' not in file:
                os.mkdir(os.path.join(self.tmp_dir, file))
            else:
                filename = os.path.basename(file)
                src_file = os.path.join(self.config_dir_path, filename)
                dst_file = os.path.join(self.tmp_dir, os.path.dirname(file), filename)
                copyfile(src_file, dst_file)

    @staticmethod
    def list_flatten_dir(tmp_dir):
        flatten_file_struct = set()
        for root, dirs, files in os.walk(tmp_dir):
            dir_name = root[len(tmp_dir)+1:]
            if dir_name:
                flatten_file_struct.add(dir_name)
            for filename in files:
                flatten_file_struct.add(os.path.join(dir_name, filename))
        return flatten_file_struct

    def assert_checksum(self, src_file, dst_file):
        with open(src_file, mode='rb') as f:
            src_hash = hashlib.md5(f.read())
            src_hex_digest = src_hash.hexdigest()
        with open(dst_file, mode='rb') as f:
            dst_hash = hashlib.md5(f.read())
            dst_hex_digest = dst_hash.hexdigest()
        self.assertEqual(src_hex_digest, dst_hex_digest)

    def assert_files(self):
        upload_file_structure = set(self.files)
        download_file_structure = self.list_flatten_dir(self.download_tmp_dir)
        self.assertEqual(upload_file_structure, download_file_structure)
        files = [x for x in self.files if '.' in x]
        for filename in files:
            self.assert_checksum(os.path.join(self.tmp_dir, filename), os.path.join(self.download_tmp_dir, filename))

    def test_upload_configuration(self):
        self.setup_local_configuration_structure()
        self.config.client.upload_configurations(self.tmp_dir, self.tree_names, delete_existing_trees=True)
        self.config.client.download_configurations(self.download_tmp_dir, self.tree_names)
        self.assert_files()
