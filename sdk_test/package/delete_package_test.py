from __future__ import absolute_import
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from rapyuta_io.utils.error import PackageNotFound
from sdk_test.util import add_package, get_package


class DeletePackage(PackageTest):

    DELETE_MANIFEST = 'delete-package.json'
    DELETE_PACKAGE = 'test-delete-package'

    def setUp(self):
        self.config = Configuration()
        add_package(self.DELETE_MANIFEST, self.DELETE_PACKAGE)

    def test_delete_package_using_package_object(self):
        package = get_package(self.DELETE_PACKAGE)
        packageId = package.packageId
        package.delete()
        expected_err_msg = 'Package not found'
        with self.assertRaises(PackageNotFound) as e:
            self.config.client.get_package(packageId)
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_delete_package_using_client(self):
        package = get_package(self.DELETE_PACKAGE)
        packageId = package.packageId
        self.config.client.delete_package(package_id=packageId)
        expected_err_msg = 'Package not found'
        with self.assertRaises(PackageNotFound) as e:
            self.config.client.get_package(packageId)
        self.assertEqual(str(e.exception), expected_err_msg)
