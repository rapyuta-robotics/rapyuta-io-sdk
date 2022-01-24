# encoding: utf-8
from __future__ import absolute_import
import requests
import unittest

from mock import patch, Mock
from requests import Response

from rapyuta_io.clients.package import Package
from rapyuta_io.clients.persistent_volumes import PersistentVolumes
from rapyuta_io.clients.plan import Plan
from rapyuta_io.utils.error import APIError, PackageNotFound, PlanNotFound, InternalServerError,\
    InvalidParameterException
from tests.utils.client import get_client
from tests.utils.package_responses import PACKAGE_OK_VALIDATE, PACKAGES_LIST, PERSISTENT_VOLUME_INFO


class ClientPackageTests(unittest.TestCase):

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_package_ok(self, rest_mock, response):
        response.text = PACKAGE_OK_VALIDATE
        response.status_code = requests.codes.OK
        rest_mock.return_value = response
        client = get_client()
        pkg = client.get_package('test_package_id')
        rest_mock.assert_called_once()
        self.assertIsInstance(pkg, Package)
        self.assertEqual(pkg.packageId, 'test_package_id')
        self.assertEqual(pkg.packageName, 'test-1.0')
        self.assertEqual(pkg._auth_token, 'Bearer test_auth_token')
        self.assertFalse(pkg.is_partial)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_package_no_plan(self, rest_mock, response):
        response.text = PACKAGE_OK_VALIDATE
        response.status_code = requests.codes.OK
        rest_mock.return_value = response
        client = get_client()
        pkg = client.get_package('my_package')
        with self.assertRaises(PlanNotFound):
            pkg.get_plan_by_id('test_plan_id')
        rest_mock.assert_called_once()

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_package_no_pkg_info(self, rest_mock, response):
        response.text = '{}'
        response.status_code = requests.codes.OK
        rest_mock.return_value = response
        client = get_client()
        with self.assertRaises(APIError):
            client.get_package('test_package_id')
        rest_mock.assert_called_once()

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_package_no_service_id(self, rest_mock, response):
        response.text = '{}'
        response.status_code = requests.codes.NOT_FOUND
        rest_mock.return_value = response
        client = get_client()
        with self.assertRaises(PackageNotFound):
            client.get_package('test_package_id')
        rest_mock.assert_called_once()

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_package_api_error(self, rest_mock, response):
        response.text = '{}'
        response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        rest_mock.return_value = response
        client = get_client()
        with self.assertRaises(InternalServerError):
            client.get_package('test_package_id')
        rest_mock.assert_called_once()

    def test_get_all_packages_failure_invalid_filter_name(self):
        invalid_filter_name = 25
        expected_err_msg = 'name must be a string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.get_all_packages(name=invalid_filter_name)
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_get_all_packages_failure_invalid_filter_version(self):
        invalid_filter_version = 1.0
        expected_err_msg = 'version must be a string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.get_all_packages(version=invalid_filter_version)
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_all_packages_success_no_filter_parameters(self, rest_mock, response):
        response.text = PACKAGES_LIST
        response.status_code = requests.codes.OK
        rest_mock.return_value = response
        rest_mock.side_effect = [response]
        client = get_client()
        pkg_list = client.get_all_packages()
        rest_mock.assert_called_once()
        self.assertEqual(len(pkg_list), 2)
        for pkg in pkg_list:
            self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
            self.assertTrue(pkg.is_partial)
        self.assertEqual(pkg_list[0].packageName, 'test_package')
        self.assertEqual(pkg_list[0].packageId, 'package_id')

    @patch('requests.request')
    def test_get_all_packages_success_filter_name_only(self, rest_mock):
        filter_name = 'test'
        all_packages = Mock()
        all_packages.text = PACKAGES_LIST
        all_packages.status_code = requests.codes.OK
        rest_mock.side_effect = [all_packages]
        client = get_client()
        pkgs = client.get_all_packages(name=filter_name)
        self.assertEqual(rest_mock.call_count, 1)
        self.assertEqual(len(pkgs), 1)
        for pkg in pkgs:
            self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
            self.assertTrue(pkg.is_partial)
        self.assertIn(filter_name, pkgs[0].packageName)

    @patch('requests.request')
    def test_get_all_packages_success_filter_version_only(self, rest_mock):
        filter_version = 'v1.0'
        all_packages = Mock()
        all_packages.text = PACKAGES_LIST
        all_packages.status_code = requests.codes.OK
        rest_mock.side_effect = [all_packages]
        client = get_client()
        pkgs = client.get_all_packages(version=filter_version)
        self.assertEqual(rest_mock.call_count, 1)
        self.assertEqual(len(pkgs), 2)
        for pkg in pkgs:
            self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
            self.assertTrue(pkg.is_partial)
        self.assertEqual(filter_version, pkgs[0].packageVersion)

    @patch('requests.request')
    def test_get_all_packages_success_filter_name_filter_version(self, rest_mock):
        filter_version = 'v1.0'
        filter_name = 'test'
        all_packages = Mock()
        all_packages.text = PACKAGES_LIST
        all_packages.status_code = requests.codes.OK
        rest_mock.side_effect = [all_packages]
        client = get_client()
        pkgs = client.get_all_packages(name=filter_name, version=filter_version)
        self.assertEqual(rest_mock.call_count, 1)
        self.assertEqual(len(pkgs), 1)
        for pkg in pkgs:
            self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
            self.assertTrue(pkg.is_partial)
        self.assertIn(filter_name, pkgs[0].packageName)
        self.assertEqual(filter_version, pkgs[0].packageVersion)

    @patch('requests.request')
    def test_get_all_packages_success_no_data_filter_name_filter_version(self, rest_mock):
        filter_version = 'v1.1'
        filter_name = 'test'
        all_packages = Mock()
        all_packages.text = PACKAGES_LIST
        all_packages.status_code = requests.codes.OK
        rest_mock.side_effect = [all_packages]
        client = get_client()
        pkgs = client.get_all_packages(name=filter_name, version=filter_version)
        self.assertEqual(rest_mock.call_count, 1)
        self.assertEqual(len(pkgs), 0)

    @patch('requests.request')
    def test_package_refresh_ok(self, rest_mock):
        package_list = Mock()
        package_list.text = PACKAGES_LIST
        package_list.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE
        get_package.status_code = requests.codes.OK
        rest_mock.side_effect = [package_list, get_package]
        client = get_client()
        pkg_list = client.get_all_packages()
        pkg = pkg_list[0]
        self.assertTrue(pkg.is_partial)
        pkg.refresh()
        self.assertFalse(pkg.is_partial)
        self.assertIsInstance(pkg, Package, 'pkg should be instance of Package class')
        self.assertEqual(pkg_list[0].packageName, 'test-1.0')
        self.assertEqual(pkg_list[0].packageId, 'pkg-xlhpyvigqoorhnomeryjfjqx')
        self.assertEqual(rest_mock.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_all_packages_api_error(self, rest_mock, response):
        response.text = {}
        response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        rest_mock.return_value = response
        client = get_client()
        with self.assertRaises(InternalServerError):
            client.get_all_packages()
        rest_mock.assert_called_once()

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_persistent_volume_ok(self, rest_mock, response):
        response.text = PERSISTENT_VOLUME_INFO
        response.status_code = requests.codes.OK
        rest_mock.return_value = response
        client = get_client()
        persistent_volume = client.get_persistent_volume()
        self.assertIsInstance(persistent_volume, PersistentVolumes,
                              'object should be instance of PersitentVolumes class')
        self.assertEqual(persistent_volume.packageId, 'io-public-persistent-volume')
        self.assertEqual(persistent_volume.packageName, 'Rapyuta IO Persistent Volume')
        for plan in persistent_volume.plans:
            self.assertIsInstance(plan, Plan, 'Object should be instance of class Plan')
        rest_mock.assert_called_once()
