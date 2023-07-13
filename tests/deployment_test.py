from __future__ import absolute_import
import requests
import unittest
import json

from mock import Mock, patch, MagicMock, call
from requests import Response

from rapyuta_io import DeploymentPhaseConstants
from rapyuta_io.utils import InternalServerError, RetriesExhausted, InvalidParameterException
from rapyuta_io.utils.rest_client import HttpMethod
from sdk_test.util import get_manifest_file
from tests.utils.client import get_client, headers
from tests.utils.package_responses import DEPLOYMENT_INFO, \
    DEPLOYMENT_STATUS_RUNNING, DEPLOYMENT_BINDING_OK, DEPLOYMENT_LIST, DEPLOYMENT_STATUS_PENDING, \
    DEPLOYMENT_STATUS_RUNNING_PHASE_PROVISIONING, UPDATE_DEPLOYMENT


class DeploymentTest(unittest.TestCase):

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_package_bindable(self, rest_mock, deployment_info_rseponse):
        deployment_info_rseponse.text = DEPLOYMENT_INFO
        deployment_info_rseponse.status_code = requests.codes.OK
        binding_response = deployment_info_rseponse()
        binding_response.text = DEPLOYMENT_BINDING_OK
        binding_response.status_code = requests.codes.OK
        rest_mock.side_effect = [deployment_info_rseponse, binding_response]
        client = get_client()
        deployment = client.get_deployment('deploment_id')
        binding_result = deployment.get_service_binding('binding_id')
        self.assertIsNotNone(binding_result, 'binding response should not be empty')
        self.assertIn('credentials', binding_result, 'Credentials should not be empty')
        self.assertEqual(rest_mock.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_deployment_status_ok(self, rest_mock, deployment_info_response):
        deployment_info_response.text = DEPLOYMENT_INFO
        deployment_info_response.status_code = requests.codes.OK
        deployment_status_response = deployment_info_response()
        deployment_status_response.text = DEPLOYMENT_STATUS_RUNNING
        deployment_status_response.status_code = requests.codes.OK
        rest_mock.side_effect = [deployment_info_response, deployment_status_response]
        client = get_client()
        deployment = client.get_deployment('deployment_id')
        self.assertFalse(deployment.is_partial)
        deployment_status = deployment.get_status()
        self.assertEqual(deployment_status.packageId, 'package_id')
        self.assertEqual(deployment_status.planId, 'test-plan')
        self.assertEqual(deployment_status.status, 'Running')
        self.assertEqual(deployment_status.phase, 'Succeeded')
        self.assertEqual(rest_mock.call_count, 2)

    @patch('requests.request')
    def test_poll_deployment_till_ready_ok(self, mock_request):
        deployment_info_response = MagicMock(spec=Response)
        deployment_info_response.text = DEPLOYMENT_INFO
        deployment_info_response.status_code = requests.codes.OK
        first_deployment_status_response = MagicMock(spec=Response)
        first_deployment_status_response.text = DEPLOYMENT_STATUS_PENDING
        first_deployment_status_response.status_code = requests.codes.OK
        second_deployment_status_response = MagicMock(spec=Response)
        second_deployment_status_response.text = DEPLOYMENT_STATUS_RUNNING
        second_deployment_status_response.status_code = requests.codes.OK
        mock_request.side_effect = [deployment_info_response, first_deployment_status_response,
                                    second_deployment_status_response]
        deployment = get_client().get_deployment('deployment_id')
        deployment_status = deployment.poll_deployment_till_ready(retry_count=2, sleep_interval=0)

        self.assertEqual(deployment_status.packageId, 'package_id')
        self.assertEqual(deployment_status.planId, 'test-plan')
        self.assertEqual(deployment_status.status, 'Running')
        self.assertEqual(deployment_status.phase, 'Succeeded')
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_poll_deployment_till_ready_retries_exhausted(self, mock_request):
        deployment_info_response = MagicMock(spec=Response)
        deployment_info_response.text = DEPLOYMENT_INFO
        deployment_info_response.status_code = requests.codes.OK
        first_deployment_status_response = MagicMock(spec=Response)
        first_deployment_status_response.text = DEPLOYMENT_STATUS_PENDING
        first_deployment_status_response.status_code = requests.codes.OK
        second_deployment_status_response = MagicMock(spec=Response)
        second_deployment_status_response.text = DEPLOYMENT_STATUS_RUNNING_PHASE_PROVISIONING
        second_deployment_status_response.status_code = requests.codes.OK
        mock_request.side_effect = [deployment_info_response, first_deployment_status_response,
                                    second_deployment_status_response]

        deployment = get_client().get_deployment('deployment_id')
        regexp = 'Retries exhausted: Tried 2 times with 0s interval. Deployment: phase=Provisioning status=Running' + \
                 ' errors=None'
        with self.assertRaisesRegex(RetriesExhausted, regexp):
            deployment.poll_deployment_till_ready(retry_count=2, sleep_interval=0)
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_package_deprovision_api_error(self, rest_mock, deployment_info_response):
        deployment_info_response.text = DEPLOYMENT_INFO
        deployment_info_response.status_code = requests.codes.OK
        deprovision_response = deployment_info_response()
        deprovision_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        rest_mock.side_effect = [deployment_info_response, deprovision_response]
        client = get_client()
        deployment = client.get_deployment('deployment_id')
        with self.assertRaises(InternalServerError):
            deployment.deprovision()
        self.assertEqual(rest_mock.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_package_bindable_api_error(self, rest_mock, deployment_info_response):
        deployment_info_response.text = DEPLOYMENT_INFO
        deployment_info_response.status_code = requests.codes.OK
        binding_response = deployment_info_response()
        binding_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        rest_mock.side_effect = [deployment_info_response, binding_response]
        client = get_client()
        deployment = client.get_deployment('deployment_id')
        with self.assertRaises(InternalServerError):
            deployment.get_service_binding()
        self.assertEqual(rest_mock.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_deployment_status_api_error(self, rest_mock, deployment_info_response):
        deployment_info_response.text = DEPLOYMENT_INFO
        deployment_info_response.status_code = requests.codes.OK
        deployment_status_response = deployment_info_response()
        deployment_status_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
        rest_mock.side_effect = [deployment_info_response, deployment_status_response]
        client = get_client()
        deployment = client.get_deployment('deployment_id')
        with self.assertRaises(InternalServerError):
            deployment.get_status()
        self.assertEqual(rest_mock.call_count, 2)

    @patch('rapyuta_io.clients.catalog_client.CatalogClient._execute')
    def test_get_deployment_list_ok(self, catalog_mock_execute):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/deployment/list'
        expected_query_param = {'phase': ['Succeeded', 'Provisioning']}
        catalog_mock_execute.return_value = MagicMock()
        catalog_mock_execute.return_value.status_code = 200
        catalog_mock_execute.return_value.text = DEPLOYMENT_LIST
        phases = [DeploymentPhaseConstants.SUCCEEDED, DeploymentPhaseConstants.PROVISIONING]
        deployments = get_client().get_all_deployments(phases=phases)

        catalog_mock_execute.assert_called_once_with(expected_url, HttpMethod.GET, 0,
                                                     query_params=expected_query_param)
        for dep in deployments:
            self.assertTrue(dep.is_partial)

    @patch('rapyuta_io.clients.catalog_client.CatalogClient._execute')
    def test_get_deployment_list_without_query_param(self, catalog_mock_execute):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/deployment/list'
        catalog_mock_execute.return_value = MagicMock()
        catalog_mock_execute.return_value.status_code = 200
        catalog_mock_execute.return_value.text = DEPLOYMENT_LIST
        get_client().get_all_deployments()
        catalog_mock_execute.assert_called_once_with(expected_url, HttpMethod.GET, 0, query_params={})

    @patch('rapyuta_io.clients.catalog_client.CatalogClient._execute')
    def test_get_deployment_list_with_phase_query_param(self, catalog_mock_execute):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/deployment/list'
        expected_query_param = {'phase': ['Succeeded', 'Provisioning']}
        catalog_mock_execute.return_value = MagicMock()
        catalog_mock_execute.return_value.status_code = 200
        catalog_mock_execute.return_value.text = DEPLOYMENT_LIST
        get_client().get_all_deployments(phases=[DeploymentPhaseConstants.SUCCEEDED, DeploymentPhaseConstants.PROVISIONING])
        catalog_mock_execute.assert_called_once_with(expected_url, HttpMethod.GET, 0, query_params=expected_query_param)

    @patch('requests.request')
    def test_get_bad_request_error_with_invalid_device_id(self, mock_request):
        expected_err_msg = 'invalid deviceID'
        with self.assertRaises(InvalidParameterException) as e:
            get_client().get_all_deployments(device_id=1234)

        self.assertEqual(str(e.exception), expected_err_msg)
        self.assertEqual(mock_request.call_count, 0)

    @patch('requests.request')
    def test_get_filtered_deployment_list_with_valid_device_id(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/deployment/list'
        expected_query_param = {'device_uid': 'test-device-id'}
        client = get_client()
        mock_get_filtered_deployment = Mock()
        mock_get_filtered_deployment.status_code = 200
        mock_get_filtered_deployment.text = DEPLOYMENT_LIST
        mock_request.side_effect = [mock_get_filtered_deployment]
        client.get_all_deployments(device_id='test-device-id')
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params=expected_query_param)
        self.assertEqual(mock_get_filtered_deployment.status_code, 200)

    @patch('requests.request')
    def test_deployment_refresh_ok(self, mock_request):
        deployment_list = Mock()
        deployment_list.text = DEPLOYMENT_LIST
        deployment_list.status_code = requests.codes.OK
        get_deployment = Mock()
        get_deployment.text = DEPLOYMENT_STATUS_RUNNING
        get_deployment.status_code = requests.codes.OK
        mock_request.side_effect = [deployment_list, get_deployment]

        client = get_client()
        deployments = client.get_all_deployments()
        self.assertTrue(deployments[0].is_partial)
        deployments[0].refresh()
        self.assertFalse(deployments[0].is_partial)
        self.assertEqual(deployments[0].packageId, 'package_id')
        self.assertEqual(deployments[0].planId, 'test-plan')
        self.assertEqual(deployments[0].status, 'Running')
        self.assertEqual(deployments[0].phase, 'Succeeded')
        self.assertEqual(mock_request.call_count, 2)

    @patch('rapyuta_io.clients.catalog_client.CatalogClient._execute')
    def test_update_deployment_success(self, catalog_mock_execute):
        catalog_mock_execute.return_value = MagicMock()
        catalog_mock_execute.return_value.status_code = 200
        catalog_mock_execute.return_value.text = UPDATE_DEPLOYMENT
        payload = json.loads(UPDATE_DEPLOYMENT)
        get_client().update_deployment(payload, 0)
        catalog_mock_execute.assert_has_calls([call(
            'https://gacatalog.apps.okd4v2.prod.rapyuta.io/v2/service_instances/dep-xyiwwwfongcfhpkhqlohtbee',
            HttpMethod.PATCH, 0,
            payload=payload)])
