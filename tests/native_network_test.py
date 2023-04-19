from __future__ import absolute_import
import unittest
import requests
from mock import patch, Mock, call
from rapyuta_io.utils import ResourceNotFoundError

from rapyuta_io.utils.error import InvalidParameterException
from tests.utils.client import get_client, headers, add_auth_token
from rapyuta_io.clients.package import Runtime, ROSDistro, Device
from rapyuta_io.clients.native_network import NativeNetwork, Parameters
from tests.utils.native_network_responses import NATIVE_NETWORK_CREATE_SUCCESS, NATIVE_NETWORK_LIST_SUCCESS, \
    NATIVE_NETWORK_GET_SUCCESS, NATIVE_NETWORK_FAILURE, NATIVE_NETWORK_NOT_FOUND
from rapyuta_io.clients.common_models import Limits

class NativeNetworkTests(unittest.TestCase):
    def setUp(self):
        native_network = {
            "ID": 1,
            "name": "native_network_name",
            "guid": "net-guid",
            "ownerProject": "project-id",
            "creator": "creator-id",
            "runtime": "cloud",
            "rosDistro": "kinetic",
            "internalDeploymentGUID": "dep-id",
            "internalDeploymentStatus": {
                "phase": "Succeeded",
                "status": "Running"
            },
            "parameters": {
                "limits": {
                    "cpu": 1,
                    "memory": 4096
                }
            }
        }
        self.native_network = NativeNetwork.deserialize(native_network)
        add_auth_token(self.native_network)

    def test_create_native_network_name_empty(self):
        expected_err_msg = 'name must be a non-empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_native_network(NativeNetwork('', Runtime.CLOUD, ROSDistro.KINETIC))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_invalid_name(self):
        expected_err_msg = 'name must be a non-empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_native_network(NativeNetwork(1, Runtime.CLOUD, ROSDistro.KINETIC))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_noetic_device_err(self):
        with self.assertRaises(InvalidParameterException) as e:
            NativeNetwork('native_network_name', Runtime.DEVICE, ROSDistro.NOETIC)
        self.assertEqual(str(e.exception), 'device runtime does not support noetic ros_distro yet')

    def test_create_native_network_invalid_runtime(self):
        expected_err_msg = 'runtime must be one of rapyuta_io.clients.package.Runtime'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_native_network(NativeNetwork('native_network_name', 'invalid_runtime', ROSDistro.KINETIC))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_invalid_rosdistro(self):
        expected_err_msg = 'ros_distro must be one of rapyuta_io.clients.package.ROSDistro'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_native_network(NativeNetwork('native_network_name', Runtime.CLOUD, 'invalid rosdistro'))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_invalid_parameters(self):
        expected_err_msg = 'parameters must be of type rapyuta_io.clients.native_network.Parameters'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_native_network(NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.MELODIC,
                                                       'invalid_parameters'))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_device_runtime_parameters_invalid_device(self):
        expected_err_msg = 'device must be of type rapyuta_io.clients.device.Device'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            parameters = Parameters(device='device', network_interface='lo')
            client.create_native_network(
                NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.MELODIC, parameters))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_device_runtime_parameters_empty_device_uuid(self):
        expected_err_msg = 'uuid field must be present in rapyuta_io.clients.device.Device object'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            device = Device('dev-name')
            device.uuid = ''
            device.ip_interfaces = {'lo': '0.0.0.0'}
            parameters = Parameters(device=device, network_interface='lo')
            client.create_native_network(
                NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.MELODIC, parameters))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_device_runtime_parameters_empty_ip_interfaces(self):
        expected_err_msg = 'ip_interfaces field must be present in rapyuta_io.clients.device.Device object'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            device = Device('dev-name')
            device.uuid = 'random'
            parameters = Parameters(device=device, network_interface='lo')
            client.create_native_network(
                NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.MELODIC, parameters))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_device_runtime_parameters_invalid_network_interface(self):
        expected_err_msg = 'NETWORK_INTERFACE should be in [\'lo\']'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            device = Device('dev-name')
            device.uuid = 'random'
            device.ip_interfaces = {'lo': '0.0.0.0'}
            parameters = Parameters(device=device, network_interface='docker0')
            client.create_native_network(
                NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.MELODIC, parameters))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_device_runtime_parameters_invalid_restart_policy(self):
        expected_err_msg = 'RestartPolicy must be one of rapyuta_io.clients.package.RestartPolicy'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            device = Device('dev-name')
            device.uuid = 'random'
            device.ip_interfaces = {'lo': '0.0.0.0'}
            parameters = Parameters(device=device, network_interface='lo', restart_policy='')
            client.create_native_network(
                NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.MELODIC, parameters))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_device_runtime_no_parameters(self):
        expected_err_msg = 'parameters must be present for device runtime'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_native_network(
                NativeNetwork('native_network_name', Runtime.DEVICE, ROSDistro.MELODIC, None))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_device_runtime_no_device_id(self):
        expected_err_msg = 'device_id field must be present in rapyuta_io.clients.' \
                           'native_network.Parameters object for device runtime'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            device = Device('dev-name')
            device.uuid = 'random'
            device.ip_interfaces = {'lo': '0.0.0.0'}
            parameters = Parameters(device=device, network_interface='lo')
            parameters.device_id = ''
            client.create_native_network(
                NativeNetwork('native_network_name', Runtime.DEVICE, ROSDistro.MELODIC, parameters))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_device_runtime_no_network_interface(self):
        expected_err_msg = 'network_interface must be present in rapyuta_io.clients.' \
                           'native_network.Parameters object for device runtime'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            device = Device('dev-name')
            device.uuid = 'random'
            device.ip_interfaces = {'lo': '0.0.0.0'}
            parameters = Parameters(device=device, network_interface='lo')
            parameters.network_interface = ''
            client.create_native_network(
                NativeNetwork('native_network_name', Runtime.DEVICE, ROSDistro.MELODIC, parameters))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_native_network_object_invalid_native_network_payload_object(self):
        expected_err_msg = 'native_network must be non-empty and of type ' \
                           'rapyuta_io.clients.native_network.NativeNetwork'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_native_network(1)
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_create_noetic_native_network_success(self, mock_request):
        expected_payload = {
            "name": "native_network_name",
            "runtime": 'cloud',
            "rosDistro": 'noetic'
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork'
        mock_create_native_network = Mock()
        mock_create_native_network.text = NATIVE_NETWORK_CREATE_SUCCESS
        mock_create_native_network.status_code = requests.codes.OK
        mock_get_native_network = Mock()
        mock_get_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_get_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_native_network, mock_get_native_network]

        client = get_client()
        native_network_parameters = None
        native_network_payload = NativeNetwork("native_network_name", Runtime.CLOUD, ROSDistro.NOETIC,
                                               native_network_parameters)
        native_network_response = client.create_native_network(native_network_payload)
        print(headers, expected_payload, expected_url, 'POST', None)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-guid', method='GET', params=None)
        ])
        self.assertEqual(native_network_response.guid, 'net-guid')
        self.assertEqual(native_network_response.name, 'native_network_name')
        self.assertFalse(native_network_response.is_partial)

    @patch('requests.request')
    def test_create_native_network_success(self, mock_request):
        expected_payload = {
            "name": "native_network_name",
            "runtime": 'cloud',
            "rosDistro": 'kinetic',
            "parameters": {"limits": {"cpu": 1, "memory": 1024}}
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork'
        mock_create_native_network = Mock()
        mock_create_native_network.text = NATIVE_NETWORK_CREATE_SUCCESS
        mock_create_native_network.status_code = requests.codes.OK
        mock_get_native_network = Mock()
        mock_get_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_get_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_native_network, mock_get_native_network]

        client = get_client()
        native_network_parameters = Parameters(limits=Limits(1,1024))
        native_network_payload = NativeNetwork("native_network_name", Runtime.CLOUD, ROSDistro.KINETIC,
                                               native_network_parameters)
        native_network_response = client.create_native_network(native_network_payload)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-guid', method='GET', params=None)
        ])
        self.assertEqual(native_network_response.guid, 'net-guid')
        self.assertEqual(native_network_response.name, 'native_network_name')
        self.assertFalse(native_network_response.is_partial)

    @patch('requests.request')
    def test_create_native_network_success_without_parameters(self, mock_request):
        expected_payload = {
            "name": "native_network_name",
            "runtime": 'cloud',
            "rosDistro": 'kinetic'
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork'
        mock_create_native_network = Mock()
        mock_create_native_network.text = NATIVE_NETWORK_CREATE_SUCCESS
        mock_create_native_network.status_code = requests.codes.OK
        mock_get_native_network = Mock()
        mock_get_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_get_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_native_network, mock_get_native_network]

        client = get_client()
        native_network_payload = NativeNetwork("native_network_name", Runtime.CLOUD, ROSDistro.KINETIC)
        native_network_response = client.create_native_network(native_network_payload)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-guid', method='GET', params=None)
        ])
        self.assertEqual(native_network_response.guid, 'net-guid')
        self.assertEqual(native_network_response.name, 'native_network_name')

    @patch('requests.request')
    def test_create_device_native_network_success(self, mock_request):
        expected_payload = {
            "name": "native_network_name",
            "runtime": 'device',
            "rosDistro": 'melodic',
            "parameters": {"device_id": "random", "NETWORK_INTERFACE": "lo"}
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork'
        mock_create_native_network = Mock()
        mock_create_native_network.text = NATIVE_NETWORK_CREATE_SUCCESS
        mock_create_native_network.status_code = requests.codes.OK
        mock_get_native_network = Mock()
        mock_get_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_get_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_native_network, mock_get_native_network]

        client = get_client()
        device = Device('dev-name')
        device.uuid = 'random'
        device.ip_interfaces = {'lo': '0.0.0.0'}
        parameters = Parameters(device=device, network_interface='lo')
        native_network_payload = NativeNetwork("native_network_name", Runtime.DEVICE, ROSDistro.MELODIC,
                                               parameters)
        native_network_response = client.create_native_network(native_network_payload)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-guid', method='GET', params=None)
        ])
        self.assertEqual(native_network_response.guid, 'net-guid')
        self.assertEqual(native_network_response.name, 'native_network_name')
        self.assertFalse(native_network_response.is_partial)

    def test_get_native_network_invalid_guid(self):
        expected_err_msg = 'guid needs to be a non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.get_native_network(None)
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_get_native_network_guid_empty(self):
        expected_err_msg = 'guid needs to be a non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.get_native_network('')
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_get_native_network_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork/{}'.format('net-guid')
        mock_get_native_network = Mock()
        mock_get_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_get_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_native_network]

        client = get_client()
        native_network = client.get_native_network('net-guid')
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params=None)
        self.assertEqual(native_network.name, 'native_network_name')
        self.assertEqual(native_network.runtime, 'cloud')
        self.assertEqual(native_network.ros_distro, 'kinetic')
        self.assertEqual(native_network.parameters.limits.cpu, 1)
        self.assertEqual(native_network.parameters.limits.memory, 4096)
        self.assertEqual(native_network.updated_at, '2021-02-05T13:16:08.736362Z')
        self.assertEqual(native_network.guid, 'net-guid')
        self.assertEqual(native_network.owner_project, 'project-id')
        self.assertEqual(native_network.creator, 'creator-id')
        self.assertEqual(native_network.internal_deployment_guid, 'dep-id')
        self.assertEqual(native_network.internal_deployment_status.phase, 'Succeeded')
        self.assertFalse(native_network.is_partial)

    @patch('requests.request')
    def test_list_native_network_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork'
        mock_list_native_network = Mock()
        mock_list_native_network.text = NATIVE_NETWORK_LIST_SUCCESS
        mock_list_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_native_network]

        client = get_client()
        native_network_list = client.list_native_networks()
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params=None)
        self.assertEqual(native_network_list[0].name, 'native_network_name')
        self.assertEqual(native_network_list[0].runtime, 'cloud')
        self.assertEqual(native_network_list[0].ros_distro, 'kinetic')
        self.assertEqual(native_network_list[0].parameters.limits.cpu, 1)
        self.assertEqual(native_network_list[0].parameters.limits.memory, 4096)
        self.assertEqual(native_network_list[0].updated_at, '2021-02-05T13:16:08.736362Z')
        self.assertEqual(native_network_list[0].guid, 'net-guid')
        self.assertEqual(native_network_list[0].owner_project, 'project-id')
        self.assertEqual(native_network_list[0].creator, 'creator-id')
        self.assertEqual(native_network_list[0].internal_deployment_guid, 'dep-id')
        self.assertEqual(native_network_list[0].internal_deployment_status.phase, 'Succeeded')
        for net in native_network_list:
            self.assertTrue(net.is_partial)

    @patch('requests.request')
    def test_native_network_refresh_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork'
        mock_list_native_network = Mock()
        mock_list_native_network.text = NATIVE_NETWORK_LIST_SUCCESS
        mock_list_native_network.status_code = requests.codes.OK
        mock_get_native_network = Mock()
        mock_get_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_get_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_native_network, mock_get_native_network]

        client = get_client()
        native_network_list = client.list_native_networks()
        self.assertTrue(native_network_list[0].is_partial)
        native_network_list[0].refresh()
        self.assertFalse(native_network_list[0].is_partial)

        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params=None),
            call(headers=headers, json=None, url=expected_url + '/net-guid', method='GET', params={}),
        ])
        self.assertEqual(native_network_list[0].name, 'native_network_name')
        self.assertEqual(native_network_list[0].runtime, 'cloud')
        self.assertEqual(native_network_list[0].ros_distro, 'kinetic')
        self.assertEqual(native_network_list[0].parameters.limits.cpu, 1)
        self.assertEqual(native_network_list[0].parameters.limits.memory, 4096)
        self.assertEqual(native_network_list[0].updated_at, '2021-02-05T13:16:08.736362Z')
        self.assertEqual(native_network_list[0].guid, 'net-guid')
        self.assertEqual(native_network_list[0].owner_project, 'project-id')
        self.assertEqual(native_network_list[0].creator, 'creator-id')
        self.assertEqual(native_network_list[0].internal_deployment_guid, 'dep-id')
        self.assertEqual(native_network_list[0].internal_deployment_status.phase, 'Succeeded')
        self.assertEqual(native_network_list[0].internal_deployment_status.status, 'Running')

    def test_delete_native_network_invalid_guid(self):
        expected_err_msg = 'guid needs to be a non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.delete_native_network(None)
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_delete_native_network_guid_empty(self):
        expected_err_msg = 'guid needs to be a non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.delete_native_network('')
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_delete_native_network_not_found(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork/{}'.format('net-guid')
        mock_delete_native_network = Mock()
        mock_delete_native_network.text = NATIVE_NETWORK_NOT_FOUND
        mock_delete_native_network.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_delete_native_network]
        client = get_client()
        with self.assertRaises(ResourceNotFoundError) as e:
            client.delete_native_network('net-guid')
        mock_request.assert_called_once_with(headers=headers, url=expected_url, json=None,
                                             method='DELETE', params=None)
        self.assertEqual(str(e.exception), 'native network not found in db')

    @patch('requests.request')
    def test_delete_native_network_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork/{}'.format('net-guid')
        mock_delete_native_network = Mock()
        mock_delete_native_network.text = 'null'
        mock_delete_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_delete_native_network]

        client = get_client()
        client.delete_native_network('net-guid')
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='DELETE',
                                             params=None)

    @patch('requests.request')
    def test_delete_native_network_success_with_native_network_object(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork/{}'.format('net-guid')
        mock_get_native_network = Mock()
        mock_get_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_get_native_network.status_code = requests.codes.OK
        mock_delete_native_network = Mock()
        mock_delete_native_network.text = 'null'
        mock_delete_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_native_network, mock_delete_native_network]

        client = get_client()
        native_network = client.get_native_network('net-guid')
        native_network.delete()
        mock_request.assert_called_with(headers=headers,
                                        json=None,
                                        url=expected_url,
                                        method='DELETE',
                                        params={})
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.request')
    def test_get_status_native_network_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork/{}'.format('net-guid')
        internal_deployment_status_expected = self.native_network.internal_deployment_status

        mock_get_status_native_network = Mock()
        mock_get_status_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_get_status_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_status_native_network]

        internal_deployment_status_actual = self.native_network.get_status()
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params={})
        self.assertEqual(internal_deployment_status_expected.phase, internal_deployment_status_actual.phase)
        self.assertEqual(internal_deployment_status_expected.status, internal_deployment_status_actual.status)

    @patch('requests.request')
    def test_create_native_network_failure(self, mock_request):
        expected_payload = {
            "name": "native_network_name",
            "runtime": 'cloud',
            "rosDistro": 'kinetic'
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork'
        mock_create_native_network = Mock()
        mock_create_native_network.text = NATIVE_NETWORK_FAILURE
        mock_create_native_network.status_code = requests.codes.OK
        mock_get_native_network = Mock()
        mock_get_native_network.text = NATIVE_NETWORK_FAILURE
        mock_get_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_native_network, mock_get_native_network]

        mock_request.side_effect = [mock_create_native_network, mock_get_native_network]

        client = get_client()
        native_network_payload = NativeNetwork("native_network_name", Runtime.CLOUD, ROSDistro.KINETIC)
        native_network_response = client.create_native_network(native_network_payload)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_url + '/' + 'net-guid', method='GET', params=None)
        ])
        self.assertEqual(native_network_response.internal_deployment_status.error_code[0], "DEP_E209")
        self.assertEqual(native_network_response.internal_deployment_status.phase, "Failed to start")

    @patch('requests.request')
    def test_poll_native_network_till_ready(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/nativenetwork/{}'.format('net-guid')
        internal_deployment_status_expected = self.native_network.internal_deployment_status

        mock_poll_native_network = Mock()
        mock_poll_native_network.text = NATIVE_NETWORK_GET_SUCCESS
        mock_poll_native_network.status_code = requests.codes.OK
        mock_request.side_effect = [mock_poll_native_network]

        internal_deployment_status_actual = self.native_network.poll_native_network_till_ready()
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params={})
        self.assertEqual(internal_deployment_status_expected.phase,
                         internal_deployment_status_actual.internal_deployment_status.phase)
        self.assertEqual(internal_deployment_status_expected.status,
                         internal_deployment_status_actual.internal_deployment_status.status)
