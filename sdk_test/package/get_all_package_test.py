from __future__ import absolute_import
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import add_package, delete_package, get_logger
from rapyuta_io.clients.package import Package


class GetAllPackage(PackageTest):

    CLOUD_NON_ROS_MANIFEST = 'cloud-non-ros.json'
    CLOUD_NON_ROS_PACKAGE = 'test-get-all-packages-cloud-non-ros-pkg'
    NGINX_SINGLE_COMPONENT_MANIFEST = 'nginx-single-component.json'
    NGINX_SINGLE_COMPONENT_PACKAGE = 'test-get-all-packages-nginx-single-component-pkg'
    PACKAGE_VERSION = 'v1.0.0'

    @classmethod
    def setUpClass(cls):
        add_package(cls.CLOUD_NON_ROS_MANIFEST, cls.CLOUD_NON_ROS_PACKAGE)
        add_package(cls.NGINX_SINGLE_COMPONENT_MANIFEST, cls.NGINX_SINGLE_COMPONENT_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.CLOUD_NON_ROS_PACKAGE)
        delete_package(cls.NGINX_SINGLE_COMPONENT_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()

    def test_get_all_packages_no_filter_parameters(self):
        packages = self.config.client.get_all_packages()
        for pkg in packages:
            self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
            self.assertTrue(pkg.is_partial)
        self.assertEqual(self.NGINX_SINGLE_COMPONENT_PACKAGE, packages[0].packageName)
        self.assertEqual(self.CLOUD_NON_ROS_PACKAGE, packages[1].packageName)

    def test_get_all_packages_filter_name_only(self):
        name = self.CLOUD_NON_ROS_PACKAGE
        packages = self.config.client.get_all_packages(name=name)
        for pkg in packages:
            self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
            self.assertTrue(pkg.is_partial)
        self.assertEqual(name, packages[0].packageName)

    def test_get_all_packages_filter_version_only(self):
        version = self.PACKAGE_VERSION
        packages = self.config.client.get_all_packages(version=version)
        for pkg in packages:
            self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
            self.assertTrue(pkg.is_partial)
            self.assertEqual(pkg.packageVersion, version)
        self.assertEqual(self.NGINX_SINGLE_COMPONENT_PACKAGE, packages[0].packageName)
        self.assertEqual(self.CLOUD_NON_ROS_PACKAGE, packages[1].packageName)

    def test_get_all_packages_filter_name_filter_version(self):
        name = self.NGINX_SINGLE_COMPONENT_PACKAGE
        version = self.PACKAGE_VERSION
        packages = self.config.client.get_all_packages(name=name, version=version)
        for pkg in packages:
            self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
            self.assertTrue(pkg.is_partial)
        self.assertEqual(name, packages[0].packageName)
        self.assertEqual(version, packages[0].packageVersion)

