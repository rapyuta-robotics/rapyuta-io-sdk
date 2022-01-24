from __future__ import absolute_import
import requests
import unittest

from mock import patch, MagicMock, Mock, call, ANY
from requests import Response

from rapyuta_io import DeploymentPhaseConstants, DiskType
from rapyuta_io.clients.persistent_volumes import DiskCapacity
from rapyuta_io.utils import InvalidParameterException
from rapyuta_io.utils.rest_client import HttpMethod
from tests.utils.client import get_client, headers
from tests.utils.package_responses import DEPLOYMENT_LIST
from tests.utils.persistent_volume_responses import GET_PACKAGE_SUCCESS, PROVISION_CLIENT_SUCCESS, \
    GET_VOLUME_INSTANCE_SUCCESS, GET_DISK_SUCCESS, GET_DISK_LIST_SUCCESS
from tests.utils.scoped_targeted_responses import SCOPED_TARGETED_PACKAGE

PERSISTENT_VOLUME = 'io-public-persistent-volume'


class PersistentVolumeTest(unittest.TestCase):

    @patch('requests.request')
    def test_get_volume_deployments_without_phase(self, mock_request):
        expected_url_get_package = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/status?' \
                                   'package_uid=io-public-persistent-volume'
        expected_url_list_disk = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/disk'
        expected_get_volume_instance = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceinstance/dep-lblpkngqrhdrefhvnvulaioq'
        mock_get_package = Mock()
        mock_get_package.text = GET_PACKAGE_SUCCESS
        mock_get_package.status_code = requests.codes.OK

        mock_list_disk = Mock()
        mock_list_disk.status_code = 200
        mock_list_disk.text = GET_DISK_LIST_SUCCESS
        mock_get_volume_instance = Mock()
        mock_get_volume_instance.status_code = 200
        mock_get_volume_instance.text = GET_VOLUME_INSTANCE_SUCCESS
        mock_request.side_effect = [mock_get_package, mock_list_disk, mock_get_volume_instance]
        client = get_client()

        volume = client.get_persistent_volume()
        volume_instances = volume.get_all_volume_instances()
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url_get_package, method='GET', params=None),
            call(headers=headers, json=None, url=expected_url_list_disk, method='GET', params={}),
            call(headers=headers, json=None, url=expected_get_volume_instance, method='GET', params=None),
        ])
        for vol in volume_instances:
            self.assertTrue(vol.is_partial)
            self.assertEqual(vol['name'], 'test-volume')
            self.assertEqual(vol['parameters']['io-pv']['capacity'], 32)
            self.assertEqual(vol['parameters']['io-pv']['diskType'], DiskType.SSD.value)

    @patch('requests.request')
    def test_get_volume_deployments_with_phase(self, mock_request):
        expected_url_get_package = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/status?' \
                                   'package_uid=io-public-persistent-volume'
        expected_url_list_disk = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/disk'
        expected_get_volume_instance = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceinstance/dep-lblpkngqrhdrefhvnvulaioq'
        mock_get_package = Mock()
        mock_get_package.text = GET_PACKAGE_SUCCESS
        mock_get_package.status_code = requests.codes.OK

        mock_list_disk = Mock()
        mock_list_disk.status_code = 200
        mock_list_disk.text = GET_DISK_LIST_SUCCESS
        mock_get_volume_instance = Mock()
        mock_get_volume_instance.status_code = 200
        mock_get_volume_instance.text = GET_VOLUME_INSTANCE_SUCCESS
        mock_request.side_effect = [mock_get_package, mock_list_disk, mock_get_volume_instance]
        client = get_client()

        volume = client.get_persistent_volume()
        volume_instances = volume.get_all_volume_instances(phases=['In Progress'])
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url_get_package, method='GET', params=None),
            call(headers=headers, json=None, url=expected_url_list_disk, method='GET', params={}),
            call(headers=headers, json=None, url=expected_get_volume_instance, method='GET', params=None),
        ])
        for vol in volume_instances:
            self.assertTrue(vol.is_partial)
            self.assertEqual(vol['name'], 'test-volume')
            self.assertEqual(vol['parameters']['io-pv']['capacity'], 32)
            self.assertEqual(vol['parameters']['io-pv']['diskType'], DiskType.SSD.value)

    @patch('requests.request')
    def test_create_volume_instance_invalid_disk_type(self, mock_request):
        expected_err_msg = 'disk_type must be of rapyuta_io.clients.persistent_volumes.DiskType'
        mock_get_package = Mock()
        mock_get_package.text = GET_PACKAGE_SUCCESS
        mock_get_package.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_package]
        client = get_client()
        persistent_volume = client.get_persistent_volume()
        with self.assertRaises(InvalidParameterException) as e:
            persistent_volume.create_volume_instance(name='test-volume', capacity=DiskCapacity.GiB_32,
                                                     disk_type='invalid_disk_type')
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_create_volume_instance_invalid_disk_capacity(self, mock_request):
        expected_err_msg = 'capacity must be one of rapyuta_io.clients.persistent_volumes.DiskCapacity'
        mock_get_package = Mock()
        mock_get_package.text = GET_PACKAGE_SUCCESS
        mock_get_package.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_package]
        client = get_client()
        persistent_volume = client.get_persistent_volume()
        with self.assertRaises(InvalidParameterException) as e:
            persistent_volume.create_volume_instance(name='test-volume', capacity='invalid_capacity',
                                                     disk_type=DiskType.SSD)
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_create_volume_instance_with_integer_capacity_success(self, mock_request):
        expected_url_create_disk = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/disk'
        expected_url_get_disk = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/disk/disk-guid'
        expected_url_provision_client = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceinstance/dep-guid'
        expected_url_get_package = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/status?' \
                                   'package_uid=io-public-persistent-volume'
        mock_get_package = Mock()
        mock_get_package.text = GET_PACKAGE_SUCCESS
        mock_get_package.status_code = requests.codes.OK
        mock_client_provision = Mock()
        mock_client_provision.text = PROVISION_CLIENT_SUCCESS
        mock_client_provision.status_code = requests.codes.OK
        mock_client_get_disk = Mock()
        mock_client_get_disk.text = GET_DISK_SUCCESS
        mock_client_get_disk.status_code = requests.codes.OK
        mock_get_volume_instance = Mock()
        mock_get_volume_instance.text = GET_VOLUME_INSTANCE_SUCCESS
        mock_get_volume_instance.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_package, mock_client_provision, mock_client_get_disk, mock_get_volume_instance]
        client = get_client()
        persistent_volume = client.get_persistent_volume()
        volume_instance = persistent_volume.create_volume_instance(name='test-volume', capacity=32,
                                                                   disk_type=DiskType.SSD)
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url_get_package, method='GET', params=None),
            call(headers=headers, json=ANY, url=expected_url_create_disk, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url_get_disk, method='GET', params=None),
            call(headers=headers, json=None, url=expected_url_provision_client, method='GET', params=None)
        ])
        self.assertEqual(volume_instance['name'], 'test-volume')
        self.assertEqual(volume_instance['parameters']['io-pv']['capacity'], 32)
        self.assertEqual(volume_instance['parameters']['io-pv']['diskType'], DiskType.SSD.value)
