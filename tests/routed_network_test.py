from __future__ import absolute_import
import requests
import unittest
import json
from mock import patch, Mock, call
from rapyuta_io.clients.routed_network import RoutedNetwork, Parameters
from rapyuta_io.clients.package import ROSDistro
from rapyuta_io.clients.device import Device
from rapyuta_io.utils import to_objdict, ResourceNotFoundError
from rapyuta_io.utils.error import InvalidParameterException
from rapyuta_io.utils.partials import PartialMixin

from tests.utils.client import get_client, remove_auth_token, add_auth_token, headers
from tests.utils.routed_networks_responses import ROUTED_NETWORK_CREATE_SUCCESS, ROUTED_NETWORK_GET_SUCCESS, \
    ROUTED_NETWORK_LIST_SUCCESS, ROUTED_NETWORK_NOT_FOUND
from six.moves import map
from rapyuta_io.clients.common_models import Limits

class RoutedNetworkTest(unittest.TestCase):

    def setUp(self):
        routed_network = {
            "name": "test-network",
            "guid": "net-testguid",
            "internalDeploymentStatus": {
                "error_code": [],
                "phase": "Succeeded",
                "status": "Running"
            },
        }
        self.routed_network = RoutedNetwork(to_objdict(routed_network))
        add_auth_token(self.routed_network)

    def test_create_cloud_routed_network_invalid_distro(self):
        expected_err_msg = 'ROSDistro must be one of rapyuta_io.clients.package.ROSDistro'

        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_cloud_routed_network('test-network', 'invalid-distro',
                                               True)

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_cloud_routed_network_invalid_parameters(self):
        expected_err_msg = 'parameters must be of type rapyuta_io.clients.routed_network.Parameters'

        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_cloud_routed_network('test-network', ROSDistro.KINETIC,
                                               True, 'invalid parameters')

        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_create_device_noetic_routed_network_success(self, mock_request):
        expected_payload = {
            'name': 'test-network',
            'runtime': 'device',
            'rosDistro': 'noetic',
            'shared': True,
            'parameters': {
                'NETWORK_INTERFACE': 'lo',
                'restart_policy': 'always',
                'device_id': 'test-device-id'
            },
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork'

        mock_create_network = Mock()
        mock_create_network.text = ROUTED_NETWORK_CREATE_SUCCESS
        mock_create_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_network]
        mock_get_network = Mock()
        mock_get_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_get_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_network, mock_get_network]

        client = get_client()
        device = Device._deserialize({'uuid': 'test-device-id', 'ip_interfaces': {'lo': 'ip'},
                                      'config_variables': [], 'labels': [], 'deployments': []})
        routed_network = client.create_device_routed_network('test-network', ROSDistro.NOETIC, True, device, 'lo')

        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-testguid', method='GET', params=None)
        ])
        self.assertEqual(routed_network.guid, 'net-testguid')
        self.assertEqual(routed_network.name, 'test-network')
        self.assertFalse(routed_network.is_partial)

    @patch('requests.request')
    def test_create_device_routed_network_success(self, mock_request):
        expected_payload = {
            'name': 'test-network',
            'runtime': 'device',
            'rosDistro': 'kinetic',
            'shared': True,
            'parameters': {
                'NETWORK_INTERFACE': 'lo',
                'restart_policy': 'always',
                'device_id': 'test-device-id'
            },
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork'

        mock_create_network = Mock()
        mock_create_network.text = ROUTED_NETWORK_CREATE_SUCCESS
        mock_create_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_network]
        mock_get_network = Mock()
        mock_get_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_get_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_network, mock_get_network]

        client = get_client()
        device = Device._deserialize({'uuid': 'test-device-id', 'ip_interfaces': {'lo': 'ip'},
                                      'config_variables': [], 'labels': [], 'deployments': []})
        routed_network = client.create_device_routed_network('test-network', ROSDistro.KINETIC, True, device, 'lo')

        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-testguid', method='GET', params=None)
        ])
        self.assertEqual(routed_network.guid, 'net-testguid')
        self.assertEqual(routed_network.name, 'test-network')
        self.assertFalse(routed_network.is_partial)

    def test_create_device_routed_network_invalid_distro(self):
        expected_err_msg = 'ROSDistro must be one of rapyuta_io.clients.package.ROSDistro'

        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_device_routed_network('test-network', 'invalid-distro',
                                                True, None, None)

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_device_routed_network_without_device(self):
        expected_err_msg = 'device must be of type rapyuta_io.clients.device.Device'

        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_device_routed_network('test-network', ROSDistro.KINETIC,
                                                True, None, None)

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_routed_network_without_network_interface(self):
        expected_err_msg = 'NETWORK_INTERFACE should be in [\'wlp4s0\']'

        client = get_client()
        device = Device._deserialize({'uuid': 'test-device-id', 'ip_interfaces': {'wlp4s0': 'ip'},
                                      'config_variables': [], 'labels': [], 'deployments': []})
        with self.assertRaises(InvalidParameterException) as e:
            client.create_device_routed_network('test-network', ROSDistro.KINETIC,
                                                True, device, 'lo')

        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_create_cloud_noetic_routed_network_success(self, mock_request):
        expected_payload = {
            'name': 'test-network',
            'runtime': 'cloud',
            'rosDistro': 'noetic',
            'shared': True,
            'parameters': {
            },
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork'

        mock_create_network = Mock()
        mock_create_network.text = ROUTED_NETWORK_CREATE_SUCCESS
        mock_create_network.status_code = requests.codes.OK
        mock_get_network = Mock()
        mock_get_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_get_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_network, mock_get_network]
        client = get_client()
        routed_network = client.create_cloud_routed_network('test-network', ROSDistro.NOETIC,
                                                            True)

        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-testguid', method='GET', params=None)
        ])
        self.assertEqual(routed_network.guid, 'net-testguid')
        self.assertEqual(routed_network.name, 'test-network')
        self.assertFalse(routed_network.is_partial)

    @patch('requests.request')
    def test_create_cloud_routed_network_success(self, mock_request):
        expected_payload = {
            'name': 'test-network',
            'runtime': 'cloud',
            'rosDistro': 'kinetic',
            'shared': True,
            'parameters': {
            },
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork'

        mock_create_network = Mock()
        mock_create_network.text = ROUTED_NETWORK_CREATE_SUCCESS
        mock_create_network.status_code = requests.codes.OK
        mock_get_network = Mock()
        mock_get_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_get_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_network, mock_get_network]
        client = get_client()
        routed_network = client.create_cloud_routed_network('test-network', ROSDistro.KINETIC,
                                                            True)

        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-testguid', method='GET', params=None)
        ])
        self.assertEqual(routed_network.guid, 'net-testguid')
        self.assertEqual(routed_network.name, 'test-network')
        self.assertFalse(routed_network.is_partial)

    @patch('requests.request')
    def test_create_cloud_routed_network_with_parameters_success(self, mock_request):
        expected_payload = {
            'name': 'test-network',
            'runtime': 'cloud',
            'rosDistro': 'kinetic',
            'shared': True,
            'parameters': {'limits': {'cpu': 1, 'memory': 1024}},
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork'

        mock_create_network = Mock()
        mock_create_network.text = ROUTED_NETWORK_CREATE_SUCCESS
        mock_create_network.status_code = requests.codes.OK
        mock_get_network = Mock()
        mock_get_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_get_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_network, mock_get_network]
        client = get_client()
        routed_network = client.create_cloud_routed_network('test-network', ROSDistro.KINETIC,
                                                            True, Parameters(limits=Limits(1, 1024)))

        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-testguid', method='GET', params=None)
            ])
        self.assertEqual(routed_network.guid, 'net-testguid')
        self.assertEqual(routed_network.name, 'test-network')
        self.assertFalse(routed_network.is_partial)

    @patch('requests.request')
    def test_get_routed_network(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork/{}'.format('net-testguid')

        mock_get_network = Mock()
        mock_get_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_get_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_network]
        client = get_client()
        routed_network = client.get_routed_network('net-testguid')
        remove_auth_token(routed_network)
        expected_response = json.loads(ROUTED_NETWORK_GET_SUCCESS)
        expected_response['phase'] = "Succeeded"
        expected_response["error_code"] = []
        expected_response["status"] = "Running"
        expected_response[PartialMixin.PARTIAL_ATTR] = False

        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='GET', params=None)
        self.assertEqual(routed_network.guid, 'net-testguid')
        self.assertEqual(routed_network.name, 'test-network')
        self.assertEqual(routed_network.to_dict(), expected_response)
        self.assertFalse(routed_network.is_partial)

    @patch('requests.request')
    def test_list_routed_network(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork'

        mock_list_network = Mock()
        mock_list_network.text = ROUTED_NETWORK_LIST_SUCCESS
        mock_list_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_network]
        client = get_client()
        routed_networks = client.get_all_routed_networks()
        list(map(remove_auth_token, routed_networks))
        expected_response = json.loads(ROUTED_NETWORK_LIST_SUCCESS)
        expected_response[0]['phase'] = "Succeeded"
        expected_response[0]["error_code"] = []

        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='GET', params=None)
        self.assertEqual([routed_networks[0].to_dict()], expected_response)
        for net in routed_networks:
            self.assertTrue(net.is_partial)

    @patch('requests.request')
    def test_routed_network_refresh(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork'

        mock_list_network = Mock()
        mock_list_network.text = ROUTED_NETWORK_LIST_SUCCESS
        mock_list_network.status_code = requests.codes.OK
        mock_get_network = Mock()
        mock_get_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_get_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_network, mock_get_network]
        expected_response = json.loads(ROUTED_NETWORK_GET_SUCCESS)
        expected_response['phase'] = "Succeeded"
        expected_response["error_code"] = []
        expected_response[PartialMixin.PARTIAL_ATTR] = False

        client = get_client()
        routed_networks = client.get_all_routed_networks()
        routed_network = routed_networks[0]
        self.assertTrue(routed_network.is_partial)
        routed_network.refresh()
        remove_auth_token(routed_network)

        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-testguid', method='GET', params={}),
        ])
        self.assertFalse(routed_network.is_partial)
        self.assertEqual(routed_network.guid, 'net-testguid')
        self.assertEqual(routed_network.name, 'test-network')
        self.assertEqual(routed_network.to_dict(), expected_response)

    def test_delete_routed_network_invalid_guid(self):
        expected_err_msg = 'guid needs to be a non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.delete_routed_network(123)
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_delete_routed_network_not_found(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork/{}'.format('network-guid')
        mock_delete_network = Mock()
        mock_delete_network.text = ROUTED_NETWORK_NOT_FOUND
        mock_delete_network.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_delete_network]
        client = get_client()
        with self.assertRaises(ResourceNotFoundError) as e:
            client.delete_routed_network('network-guid')
        mock_request.assert_called_once_with(headers=headers, url=expected_url, json=None,
                                             method='DELETE', params=None)
        self.assertEqual(str(e.exception), 'routed network not found in db')

    @patch('requests.request')
    def test_delete_routed_network_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork/{}'.format('network-guid')
        mock_delete_network = Mock()
        mock_delete_network.text = 'null'
        mock_delete_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_delete_network]
        client = get_client()
        client.delete_routed_network('network-guid')
        mock_request.assert_called_once_with(headers=headers, url=expected_url, json=None,
                                             method='DELETE', params=None)

    @patch('requests.request')
    def test_delete_routed_network_success_with_routed_network_object(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork/{}'.format(self.routed_network.guid)

        mock_delete_network = Mock()
        mock_delete_network.text = 'null'
        mock_delete_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_delete_network]
        self.routed_network.delete()

        mock_request.assert_called_once_with(headers=headers, url=expected_url, json=None,
                                             method='DELETE', params={})

    @patch('requests.request')
    def test_get_status_routed_network(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork/{}'.format(self.routed_network.guid)
        expected_result = self.routed_network.internalDeploymentStatus
        expected_result.errors = [expected_result.error_code]
        mock_delete_network = Mock()
        mock_delete_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_delete_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_delete_network]
        deployment_status = self.routed_network.get_status()

        mock_request.assert_called_once()
        self.assertEqual(mock_request.call_args_list[0][1]['url'], expected_url)
        self.assertEqual(mock_request.call_args_list[0][1]['method'], 'GET')
        self.assertEqual(deployment_status, expected_result)

    @patch('requests.request')
    def test_get_status_routed_network(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork/{}'.format(self.routed_network.guid)
        expected_result = self.routed_network.internalDeploymentStatus
        expected_result.errors = expected_result.error_code
        mock_delete_network = Mock()
        mock_delete_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_delete_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_delete_network]
        deployment_status = self.routed_network.get_status()

        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='GET', params={})
        self.assertEqual(deployment_status, expected_result)

    @patch('requests.request')
    def test_poll_till_ready_routed_network(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/routednetwork/{}'.format(self.routed_network.guid)
        expected_result = self.routed_network.internalDeploymentStatus
        expected_result.errors = expected_result.error_code

        mock_get_network = Mock()
        mock_get_network.text = ROUTED_NETWORK_GET_SUCCESS
        mock_get_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_network]
        deployment_status = self.routed_network.get_status()

        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='GET', params={})
        self.assertEqual(deployment_status, expected_result)
