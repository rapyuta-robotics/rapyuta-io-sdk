# encoding: utf-8
from __future__ import absolute_import

import unittest
from copy import deepcopy

import requests
from mock import patch, MagicMock, Mock
from requests import Response

from rapyuta_io import DeviceStatus, DeploymentPhaseConstants
from rapyuta_io.clients.device import Device
from rapyuta_io.clients.native_network import NativeNetwork, Parameters
from rapyuta_io.clients.package import RestartPolicy, Runtime, ROSDistro, ExecutableMount
from rapyuta_io.clients.rosbag import ROSBagJob, ROSBagOptions, UploadOptions
from rapyuta_io.clients.routed_network import RoutedNetwork
from rapyuta_io.utils import InternalServerError
from rapyuta_io.utils.error import OperationNotAllowedError, PlanNotFound, \
    InvalidParameterException, ParameterMissingException, DuplicateAliasException, \
    ConflictError, BadRequestError, ResourceNotFoundError
from rapyuta_io.utils.rest_client import HttpMethod
from tests.utils.client import get_client, headers
from tests.utils.device_respones import DEVICE_INFO, CONFIG_VARIABLES, DOCKER_CONFIG_VARIABLES, \
    DOCKER_DEVICE, DOCKER_EMPTY_ROSBAG_CONFIG_VARIABLES, GET_DOCKERCOMPOSE_DEVICE_SUCCESS, \
    DOCKER_CONFIG_VARIABLE_WITH_ROSBAG_VARIABLES, PREINSTALLED_DEVICE_WITH_NEW_RUNTIME
from .utils.package_responses import PACKAGE_OK_VALIDATE, PACKAGE_OK_VALIDATE_DEVICE, \
    DEPLOYMENT_INFO, PACKAGE_OK_NO_VALIDATE, DEPLOYMENT_STATUS_RUNNING, DEPLOYMENT_STATUS_STOPPED, \
    PROVISION_OK, DEPLOYMENT_LIST, CREATE_PACKAGE, MANIFEST, PACKAGE_OK_VALIDATE_DEVICE_DOCKER, \
    PACKAGE_NOT_FOUND, PACKAGE_OK_NON_ROS_VALIDATE, PACKAGES_LIST, PACKAGE_OK_VALIDATE_ROSBAG_JOB, \
    DEPLOYMENT_INFO_ROSBAG_JOB, PACKAGE_OK_VALIDATE_DEVICE_ROSBAG_JOB, DEPLOYMENT_INFO_DEVICE_ROSBAG_JOB,\
    GET_VOLUME_INSTANCE_OK

from .utils.scoped_targeted_responses import SCOPED_TARGETED_PACKAGE, CAN_BE_TARGETED, \
    SCOPED_TARGETABLE_DEPEPNDANT_DEPLOY, SCOPED_CLOUD_PACKAGE
from .utils.static_route_responses import STATIC_ROUTE_RESPONSE


class PackageTests(unittest.TestCase):

    @patch('requests.request')
    def test_package_provision_on_device_ok(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable, provision,
                                    deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        device.status = DeviceStatus.OFFLINE
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        ignore_device_config = ['ros_workspace']
        provision_config.add_device('ros-talker', device, ignore_device_config)
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        deployment = pkg.provision('test_deployment_name', provision_config)
        # this is not scoped or targeted
        self.assertNotIn("bridge_params",
                         provision_config.parameters["jakmybngjupwdjjdqztmcrjq"])
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 5)

    @patch('requests.request')
    def test_package_provision_on_device_with_set_comonent_alias_false_ok(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable, provision,
                                    deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        ignore_device_config = ['ros_workspace']
        provision_config.add_device('ros-talker', device, ignore_device_config, set_component_alias=False)
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'ros-talker')
        deployment = pkg.provision('test_deployment_name', provision_config)
        # this is not scoped or targeted
        self.assertNotIn("bridge_params",
                         provision_config.parameters["jakmybngjupwdjjdqztmcrjq"])
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 5)

    @patch('requests.request')
    def test_package_provision_with_rosbag_preinstalled_device(self, mock_request):
        expected_err = 'ROSBag on Device does not support Preinstalled devices'
        get_device = Mock()
        get_device.status_code = requests.codes.OK
        get_device.text = DEVICE_INFO
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable, provision,
                                    deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        ignore_device_config = ['ros_workspace']
        provision_config.add_device('ros-talker', device, ignore_device_config)
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        provision_config.add_rosbag_job('ros-talker', ROSBagJob('test-job', ROSBagOptions(all_topics=True)))
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        with self.assertRaises(InvalidParameterException) as e:
            pkg.provision('test_deployment_name', provision_config)

        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_package_provision_with_rosbag_device_without_rosbag_mount_path(self, mock_request):
        expected_err = 'This device does not have ROSBag components installed. Please re-onboard the device to use ROSBag features'
        get_device = Mock()
        get_device.text = DOCKER_DEVICE
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = DOCKER_CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable, provision,
                                    deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_device('ros-talker', device)
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        provision_config.add_rosbag_job('ros-talker', ROSBagJob('test-job', ROSBagOptions(all_topics=True)))
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        with self.assertRaises(InvalidParameterException) as e:
            pkg.provision('test_deployment_name', provision_config)

        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_package_provision_with_rosbag_device_with_empty_rosbag_mount_path(self, mock_request):
        expected_err = 'This device does not have ROSBag components installed. Please re-onboard the device to use ROSBag features'
        get_device = Mock()
        get_device.text = DOCKER_DEVICE
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = DOCKER_EMPTY_ROSBAG_CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable, provision,
                                    deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_device('ros-talker', device)
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        provision_config.add_rosbag_job('ros-talker', ROSBagJob('test-job', ROSBagOptions(all_topics=True)))
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        with self.assertRaises(InvalidParameterException) as e:
            pkg.provision('test_deployment_name', provision_config)

        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_package_provision_on_cloud_ok(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE
        get_package.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, provision, deployment_info]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        deployment = pkg.provision('test_deployment_name', provision_config)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_package_provision_on_cloud_with_rosbag_job_ok(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_ROSBAG_JOB
        get_package.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO_ROSBAG_JOB
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, provision, deployment_info]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        deployment = pkg.provision('test_deployment_name', provision_config)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 3)
        self.assertEqual(
            deployment.provisionContext.component_context['gpzxcgjynhulepjjcyglgepl'].ros_bag_job_defs[0].name, 'rbag')
        self.assertEqual(
            deployment.provisionContext.component_context['gpzxcgjynhulepjjcyglgepl'].ros_bag_job_defs[
                0].recordOptions.topics, ['/telemetry'])

    @patch('requests.request')
    def test_package_provision_on_device_with_rosbag_job_ok(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_ROSBAG_JOB
        get_package.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        get_device = Mock()
        get_device.text = GET_DOCKERCOMPOSE_DEVICE_SUCCESS
        get_device.status_code = requests.codes.OK
        get_device_configs = Mock()
        get_device_configs.text = DOCKER_CONFIG_VARIABLE_WITH_ROSBAG_VARIABLES
        get_device_configs.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO_DEVICE_ROSBAG_JOB
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_device, get_device_configs, provision, deployment_info]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        device = client.get_device('test_device_id')
        provision_config.add_device('ros-talker', device=device, ignore_device_config=['ros_workspace'],
                                    set_component_alias=False)
        deployment = pkg.provision('test_deployment_name', provision_config)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 5)
        self.assertEqual(
            deployment.provisionContext.component_context['gpzxcgjynhulepjjcyglgepl'].ros_bag_job_defs[0].name, 'rbag')
        self.assertEqual(
            deployment.provisionContext.component_context['gpzxcgjynhulepjjcyglgepl'].ros_bag_job_defs[
                0].recordOptions.topics, ['/telemetry'])
        self.assertEqual(
            deployment.provisionContext.component_context['gpzxcgjynhulepjjcyglgepl'].ros_bag_job_defs[
                0].uploadOptions.maxUploadRate, 1048576)

    @patch('requests.request')
    def test_package_provision_plan_not_found_failure(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        with self.assertRaises(PlanNotFound):
            pkg.get_provision_configuration('test-plan1')
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_package_provision_empty_ros_workspace_failure(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException):
            provision_config.add_device('ros-talker', device)
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_add_device_remove_ros_workspace_docker_device(self, rest_mock):
        component_id = "jakmybngjupwdjjdqztmcrjq"
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package_response.status_code = requests.codes.OK
        get_device_response = MagicMock()
        get_device_response.text = DOCKER_DEVICE
        get_device_response.status_code = requests.codes.OK
        config_variable_response = MagicMock()
        config_variable_response.text = DOCKER_CONFIG_VARIABLES
        config_variable_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_device_response, get_package_response, config_variable_response]
        client = get_client()
        device = client.get_device('test_device_id')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_device('ros-talker', device)
        self.assertTrue('ros_workspace' not in provision_config.parameters.get(component_id),
                        'ros_workspace should be present for docker runtime')

    @patch('requests.request')
    def test_package_provision_empty_add_label_failure(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(ParameterMissingException):
            provision_config.add_label('', '')
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_package_provision_empty_deployment_name(self, rest_mock):
        mock_response = MagicMock()
        mock_response.text = PACKAGE_OK_VALIDATE
        mock_response.status_code = 200
        rest_mock.return_value = mock_response
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            pkg.provision('', provision_config)
        self.assertEqual("deployment_name must be a non-empty string", str(e.exception))
        self.assertEqual(rest_mock.call_count, 1)

    @patch('requests.request')
    def test_package_provision_incorrect_provision_configuration_type(self, rest_mock):
        mock_response = MagicMock()
        mock_response.text = PACKAGE_OK_VALIDATE
        mock_response.status_code = 200
        rest_mock.return_value = mock_response
        client = get_client()
        pkg = client.get_package('my_package')
        with self.assertRaises(InvalidParameterException) as e:
            pkg.provision('dep1', '')
        self.assertEqual("provision_configuration must be of type ProvisionConfiguration", str(e.exception))
        self.assertEqual(rest_mock.call_count, 1)

    @patch('requests.request')
    def test_package_provision_component_not_mapped_with_device_failure(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = 200
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(OperationNotAllowedError):
            pkg.provision('test_deployment_name', provision_config)
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_package_provision_api_error(self, mock_request):
        response = Mock()
        response.text = PACKAGE_OK_VALIDATE
        response.status_code = 200
        response2 = response()
        response2.status_code = 500
        mock_request.side_effect = [response, response2]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InternalServerError):
            pkg.provision('test_package_name', provision_config)
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.request')
    def test_package_provision_component_parameter_invalid_value_failure(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_NO_VALIDATE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException):
            provision_config.add_parameter('ros-talker', 'invalid-value', 123)

    @patch('requests.request')
    def test_package_provision_component_parameter_empty_component_name_failure(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_NO_VALIDATE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException):
            provision_config.add_parameter('', 'invalid-value', 123)

    @patch('requests.request')
    def test_package_provision_component_parameter_empty_failure(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_NO_VALIDATE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        ignore_device_config = ['ros_workspace']
        provision_config.add_device('ros-talker', device, ignore_device_config)
        with self.assertRaises(InvalidParameterException):
            pkg.provision('test_deployment_name', provision_config)
        self.assertEqual(mock_request.call_count, 3)

    def test_create_executable_mount_invalid_executable_name(self):
        with self.assertRaises(InvalidParameterException) as e:
            mount = ExecutableMount(1, '/mountPath', '/subPath')
        self.assertEqual("exec_name must be a non-empty string", str(e.exception))

    def test_create_executable_mount_invalid_mount_path(self):
        with self.assertRaises(InvalidParameterException) as e:
            mount = ExecutableMount('exec-name', 1, '/subPath')
        self.assertEqual("mount_path must be a non-empty string", str(e.exception))

    def test_create_executable_mount_invalid_sub_path(self):
        with self.assertRaises(InvalidParameterException) as e:
            mount = ExecutableMount('exec-name', '/mountPath', 1)
        self.assertEqual("sub_path must be a non-empty string", str(e.exception))

    @patch('requests.request')
    def test_provision_config_add_mount_volume_both_mount_path_and_executable_mounts_none_error(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        get_volume_instance = Mock()
        get_volume_instance.text = GET_VOLUME_INSTANCE_OK
        get_volume_instance.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_volume_instance, get_volume_instance]
        client = get_client()
        pkg = client.get_package('my_package')
        volume_instance = client.get_volume_instance('test-id')
        prov_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            prov_config.mount_volume('ros-talker', volume=volume_instance, mount_path=None, executable_mounts=None)
        self.assertEqual("One of mount_path or executable_mounts should be present", str(e.exception))
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_provision_config_add_mount_volume_invalid_executable_mounts(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        get_volume_instance = Mock()
        get_volume_instance.text = GET_VOLUME_INSTANCE_OK
        get_volume_instance.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_volume_instance, get_volume_instance]
        client = get_client()
        pkg = client.get_package('my_package')
        volume_instance = client.get_volume_instance('test-id')
        prov_config = pkg.get_provision_configuration('test-plan')
        executable_mounts = ["invalid mount"]
        with self.assertRaises(InvalidParameterException) as e:
            prov_config.mount_volume('ros-talker', volume=volume_instance, mount_path=None, executable_mounts=executable_mounts)
        self.assertEqual("executable_mounts must be a list of rapyuta_io.clients.package.ExecutableMount", str(e.exception))
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_package_add_mount_volume_to_provision_config_ok(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        get_volume_instance = Mock()
        get_volume_instance.text = GET_VOLUME_INSTANCE_OK
        get_volume_instance.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_volume_instance, get_volume_instance]
        client = get_client()
        pkg = client.get_package('my_package')
        volume_instance = client.get_volume_instance('test-id')
        prov_config = pkg.get_provision_configuration('test-plan')
        executable_mounts = [ExecutableMount(exec_name='ros-talker', mount_path='/test_path', sub_path='data')]
        prov_config.mount_volume('ros-talker', volume=volume_instance, mount_path=None, executable_mounts=executable_mounts)
        self.assertEqual(
            prov_config.context['dependentDeployments'][0]['config']['mountPaths']['ros-talker']['mountPath'],
            '/test_path')
        self.assertEqual(
            prov_config.context['dependentDeployments'][0]['config']['mountPaths']['ros-talker']['subPath'], 'data')

    @patch('requests.request')
    def test_package_add_volume_to_provision_config_both_present(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        prov_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            prov_config.mount_volume('ros-talker', volume='random', device='random', mount_path=None, executable_mounts=None)
        self.assertEqual("both volume and device parameter cannot be present", str(e.exception))
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_package_add_volume_to_provision_config_both_absent(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        prov_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            prov_config.mount_volume('ros-talker', mount_path=None, executable_mounts=None)
        self.assertEqual("either a volume or device parameter must be present", str(e.exception))
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_package_add_device_volume_to_provision_config_invalid_volume(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        prov_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            prov_config.mount_volume('ros-talker', volume='invalid', mount_path=None, executable_mounts=None)
        self.assertEqual("volume must be of type rapyuta_io.clients.persistent_volumes.VolumeInstance", str(e.exception))
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_package_add_device_volume_to_provision_config_invalid_device(self, mock_request):
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('my_package')
        prov_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            prov_config.mount_volume('ros-talker', device='invalid', mount_path=None, executable_mounts=None)
        self.assertEqual("device must be of type Device", str(e.exception))
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_package_add_device_volume_to_provision_config_invalid_exec_mount(self, mock_request):
        get_device = Mock()
        get_device.text = DOCKER_DEVICE
        get_device.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = DOCKER_CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_device, config_variable]
        client = get_client()
        pkg = client.get_package('my_package')
        device = client.get_device('test-dev')
        prov_config = pkg.get_provision_configuration('test-plan')
        prov_config.add_device('ros-talker', device, ['ros_workspace'])
        executable_mounts = ["invalid"]
        with self.assertRaises(InvalidParameterException) as e:
            prov_config.mount_volume('ros-talker', device=device, mount_path=None, executable_mounts=executable_mounts)
        self.assertEqual("executable_mounts must be a list of rapyuta_io.clients.package.ExecutableMount", str(e.exception))
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_package_add_device_volume_to_provision_config_preinstalled_runtime(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_device, config_variable]
        client = get_client()
        pkg = client.get_package('my_package')
        device = client.get_device('test-dev')
        prov_config = pkg.get_provision_configuration('test-plan')
        prov_config.add_device('ros-talker', device, ['ros_workspace'])
        executable_mounts = [ExecutableMount(exec_name='ros-talker', mount_path='/test_path', sub_path='/data')]
        with self.assertRaises(OperationNotAllowedError) as e:
            prov_config.mount_volume('ros-talker', device=device, mount_path=None, executable_mounts=executable_mounts)
        self.assertEqual("Device must be a dockercompose device", str(e.exception))
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_package_add_device_volume_to_provision_config_with_new_preinstalled_runtime(self, mock_request):
        get_device = Mock()
        get_device.text = PREINSTALLED_DEVICE_WITH_NEW_RUNTIME
        get_device.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_device, config_variable]
        client = get_client()
        pkg = client.get_package('my_package')
        device = client.get_device('test-dev')
        prov_config = pkg.get_provision_configuration('test-plan')
        prov_config.add_device('ros-talker', device, ['ros_workspace'])
        executable_mounts = [ExecutableMount(exec_name='ros-talker', mount_path='/test_path', sub_path='/data')]
        with self.assertRaises(OperationNotAllowedError) as e:
            prov_config.mount_volume('ros-talker', device=device, mount_path=None, executable_mounts=executable_mounts)
        self.assertEqual("Device must be a dockercompose device", str(e.exception))
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_package_add_device_volume_to_provision_config_not_added_device(self, mock_request):
        get_device = Mock()
        get_device.text = DOCKER_DEVICE
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_device]
        client = get_client()
        pkg = client.get_package('my_package')
        device = client.get_device('test-dev')
        prov_config = pkg.get_provision_configuration('test-plan')
        executable_mounts = [ExecutableMount(exec_name='ros-talker', mount_path='/test_path', sub_path='/data')]
        with self.assertRaises(OperationNotAllowedError) as e:
            prov_config.mount_volume('ros-talker', device=device, mount_path=None, executable_mounts=executable_mounts)
        self.assertEqual("Device must be added to the component", str(e.exception))
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.request')
    def test_package_add_device_volume_to_provision_config_ok(self, mock_request):
        get_device = Mock()
        get_device.text = DOCKER_DEVICE
        get_device.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = DOCKER_CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE_DOCKER
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, get_device, config_variable]
        client = get_client()
        pkg = client.get_package('my_package')
        device = client.get_device('test-dev')
        device.status = DeviceStatus.OFFLINE.value
        prov_config = pkg.get_provision_configuration('test-plan')
        prov_config.add_device('ros-talker', device, ['ros_workspace'])
        executable_mounts = [ExecutableMount(exec_name='ros-talker', mount_path='/test_path', sub_path='/data')]
        prov_config.mount_volume('ros-talker', device=device, mount_path=None, executable_mounts=executable_mounts)
        self.assertEqual(
            prov_config.context['diskMountInfo'][0]['diskResourceId'],
            device.deviceId)
        self.assertEqual(
            prov_config.context['diskMountInfo'][0]['config']['mountPaths']['ros-talker']['mountPath'],
            '/test_path')
        self.assertEqual(
            prov_config.context['diskMountInfo'][0]['config']['mountPaths']['ros-talker']['subPath'], '/data')

    @patch('requests.request')
    def test_package_provision_dependent_deployment_ok(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        deployment_status = Mock()
        deployment_status.text = DEPLOYMENT_STATUS_RUNNING
        deployment_status.status_code = requests.codes.OK
        provision = Mock()
        provision.text = '''{"operation": "deployment_id"}'''
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = 200
        mock_request.side_effect = [get_device, get_package, config_variable, deployment_status,
                                    deployment_status, provision, deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_device('ros-talker', device, ['ros_workspace'])
        dep_deployment = client.get_deployment('deployment_id')
        provision_config.add_dependent_deployment(dep_deployment)
        deployment = pkg.provision('test_deployment_name', provision_config)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 7)
        self.assertFalse(deployment.is_partial)

    @patch('requests.request')
    def test_package_provision_dependent_deployment_with_partial_package_and_deployment_ok(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        all_packages = Mock()
        all_packages.text = PACKAGES_LIST
        all_packages.status_code = requests.codes.OK
        get_package1 = Mock()
        get_package1.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package1.status_code = requests.codes.OK
        get_package2 = Mock()
        get_package2.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package2.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        all_deployments = Mock()
        all_deployments.text = DEPLOYMENT_LIST
        all_deployments.status_code = requests.codes.OK
        deployment_status = Mock()
        deployment_status.text = DEPLOYMENT_STATUS_RUNNING
        deployment_status.status_code = requests.codes.OK
        provision = Mock()
        provision.text = '''{"operation": "deployment_id"}'''
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = 200
        mock_request.side_effect = [get_device, all_packages, get_package1, config_variable, all_deployments,
                                    deployment_status, get_package2, provision, deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkgs = client.get_all_packages()
        partial_pkg = deepcopy(pkgs[0])
        self.assertTrue(pkgs[0].is_partial)
        provision_config = pkgs[0].get_provision_configuration('test-plan')
        self.assertFalse(pkgs[0].is_partial)
        provision_config.add_device('ros-talker', device, ['ros_workspace'])
        deployments = client.get_all_deployments()
        self.assertTrue(deployments[0].is_partial)
        provision_config.add_dependent_deployment(deployments[0])
        self.assertTrue(partial_pkg.is_partial)
        deployment = partial_pkg.provision('test_deployment_name', provision_config)
        self.assertFalse(partial_pkg.is_partial)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 9)
        self.assertFalse(deployments[0].is_partial)

    @patch('requests.request')
    def test_provision_dependent_deployment_failure(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        deployment_status = Mock()
        deployment_status.text = DEPLOYMENT_STATUS_STOPPED
        deployment_status.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable,
                                    deployment_status, deployment_status]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_device('ros-talker', device, ['ros_workspace'])
        dep_deployment = client.get_deployment('deployment_id')
        with self.assertRaises(OperationNotAllowedError):
            provision_config.add_dependent_deployment(dep_deployment)
        self.assertEqual(mock_request.call_count, 5)

    @patch('requests.request')
    def test_package_provision_with_same_provision_configuration_failed(self, rest_mock):
        get_device_response = MagicMock()
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package_response.status_code = requests.codes.OK
        config_variable_response = MagicMock()
        config_variable_response.text = CONFIG_VARIABLES
        config_variable_response.status_code = requests.codes.OK
        provision_response = MagicMock()
        provision_response.text = '''{"operation": "deployment_id"}'''
        provision_response.status_code = requests.codes.OK
        deployment_info = MagicMock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = 200
        rest_mock.side_effect = [get_device_response, get_package_response,
                                 config_variable_response, provision_response,
                                 deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_device('ros-talker', device, ['ros_workspace'])
        deployment = pkg.provision('test_deployment_name-1', provision_config)
        self.assertTrue(deployment.deploymentId)
        with self.assertRaises(InvalidParameterException) as e:
            pkg.provision('test_deployment_name-2', provision_config)
        self.assertEqual("cannot reuse this ProvisionConfiguration for provisioning", str(e.exception))
        self.assertEqual(rest_mock.call_count, 5)

    @patch('requests.request')
    def test_scoped_package_provision_defaulting(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = SCOPED_TARGETED_PACKAGE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable, provision,
                                    deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('C2DPingMaxST2')
        provision_config = pkg.get_provision_configuration('basicplan')
        ignore_device_config = ['ros_workspace']
        provision_config.add_device('devicepong', device, ignore_device_config)
        self.assertEqual(provision_config.parameters["dev-comp"]["bridge_params"]["alias"], 'D239-Device')
        self.assertEqual(provision_config.parameters["cloud-comp"]["bridge_params"]["alias"], 'cloudping')
        deployment = pkg.provision('test_deployment_name', provision_config)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 5)

    @patch('requests.request')
    def test_scoped_package_provision_clash(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = SCOPED_TARGETED_PACKAGE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable, provision,
                                    deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('C2DPingMaxST2')
        provision_config = pkg.get_provision_configuration('basicplan')
        ignore_device_config = ['ros_workspace']
        provision_config.add_device('devicepong', device, ignore_device_config)
        provision_config.validate()
        provision_config.set_component_alias("cloudping", "samename")
        provision_config.set_component_alias("devicepong", "samename")
        with self.assertRaises(DuplicateAliasException):
            pkg.provision('test_deployment_name', provision_config)
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_scoped_package_provision_empty_component_name(self, mock_request):
        expected_err = "component_name must be a non-empty string"
        get_package = MagicMock()
        get_package.text = SCOPED_CLOUD_PACKAGE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('C2DPingMaxST2')
        provision_config = pkg.get_provision_configuration('basicplan')
        provision_config.validate()
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.set_component_alias("", "samename")
        self.assertEqual(str(e.exception), expected_err)
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_scoped_package_provision_invalid_component_name(self, mock_request):
        expected_err = "component_name must be a non-empty string"
        get_package = MagicMock()
        get_package.text = SCOPED_CLOUD_PACKAGE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('C2DPingMaxST2')
        provision_config = pkg.get_provision_configuration('basicplan')
        provision_config.validate()
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.set_component_alias(True, "samename")
        self.assertEqual(str(e.exception), expected_err)
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_scoped_package_provision_invalid_alias(self, mock_request):
        expected_err = "alias must be a string"
        get_package = MagicMock()
        get_package.text = SCOPED_CLOUD_PACKAGE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('C2DPingMaxST2')
        provision_config = pkg.get_provision_configuration('basicplan')
        provision_config.validate()
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.set_component_alias("cloudping", True)
        self.assertEqual(str(e.exception), expected_err)
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_scoped_package_provision_invalid_ros_namespace_flag(self, mock_request):
        expected_err = "set_ros_namespace must be a boolean"
        get_package = MagicMock()
        get_package.text = SCOPED_CLOUD_PACKAGE
        get_package.status_code = requests.codes.OK
        mock_request.side_effect = [get_package]
        client = get_client()
        pkg = client.get_package('C2DPingMaxST2')
        provision_config = pkg.get_provision_configuration('basicplan')
        provision_config.validate()
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.set_component_alias("cloudping", "alias", "true")
        self.assertEqual(str(e.exception), expected_err)
        self.assertEqual(mock_request.call_count, 1)

    @patch('requests.request')
    def test_scoped_package_provision_on_cloud_ok(self, mock_request):
        get_package = Mock()
        get_package.text = SCOPED_CLOUD_PACKAGE
        get_package.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = SCOPED_TARGETABLE_DEPEPNDANT_DEPLOY
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, provision, deployment_info]
        client = get_client()
        pkg = client.get_package('C2DPingMaxST2')
        provision_config = pkg.get_provision_configuration('basicplan')
        provision_config.validate()
        provision_config.set_component_alias("cloudping", "parent", True)
        deployment = pkg.provision('test_deployment_name', provision_config)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(deployment.parameters.sszyzwycqdgsnmgezoyaqydy.bridge_params.alias, "parent")
        self.assertEqual(deployment.parameters.sszyzwycqdgsnmgezoyaqydy.bridge_params.setROSNamespace, True)
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_package_canbetargeted_ok(self, mock_request):
        get_package = Mock()
        get_package.text = CAN_BE_TARGETED
        get_package.status_code = requests.codes.OK
        provision = Mock()
        provision.text = PROVISION_OK
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = DEPLOYMENT_INFO
        deployment_info.status_code = requests.codes.OK
        mock_request.side_effect = [get_package, provision, deployment_info]
        client = get_client()
        pkg = client.get_package('canbetargeted')
        provision_config = pkg.get_provision_configuration('basicplan')
        self.assertEqual(provision_config.parameters["compid"]["bridge_params"]["alias"], 'comp')
        deployment = pkg.provision('test_deployment_name', provision_config)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 3)

    @patch('requests.request')
    def test_package_provision_normal_package_dependent_deployment_with_scoped_and_targeted(self, mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        deployment_status = Mock()
        deployment_status.text = SCOPED_TARGETABLE_DEPEPNDANT_DEPLOY
        deployment_status.status_code = requests.codes.OK
        provision = Mock()
        provision.text = '''{"operation": "deployment_id"}'''
        provision.status_code = requests.codes.OK
        deployment_info = Mock()
        deployment_info.text = SCOPED_TARGETABLE_DEPEPNDANT_DEPLOY
        deployment_info.status_code = 200
        mock_request.side_effect = [get_device, get_package, config_variable,
                                    deployment_status, deployment_status, provision, deployment_info]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_device('ros-talker', device, ['ros_workspace'])
        dep_deployment = client.get_deployment('deployment_id')
        provision_config.add_dependent_deployment(dep_deployment)
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        deployment = pkg.provision('test_deployment_name', provision_config)
        self.assertTrue(deployment.deploymentId)
        self.assertEqual(mock_request.call_count, 7)

    @patch('requests.request')
    def test_package_provision_normal_package_dependent_deployment_with_scoped_and_targeted_alias_clash(self,
                                                                                                        mock_request):
        get_device = Mock()
        get_device.text = DEVICE_INFO
        get_device.status_code = requests.codes.OK
        get_package = Mock()
        get_package.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package.status_code = requests.codes.OK
        config_variable = Mock()
        config_variable.text = CONFIG_VARIABLES
        config_variable.status_code = requests.codes.OK
        dep_deployment_info = Mock()
        dep_deployment_info.text = SCOPED_TARGETABLE_DEPEPNDANT_DEPLOY
        dep_deployment_info.status_code = requests.codes.OK
        deployment_status = Mock()
        deployment_status.text = SCOPED_TARGETABLE_DEPEPNDANT_DEPLOY
        deployment_status.status_code = requests.codes.OK
        provision = Mock()
        provision.text = '''{"operation": "deployment_id"}'''
        provision.status_code = requests.codes.OK
        mock_request.side_effect = [get_device, get_package, config_variable, dep_deployment_info,
                                    deployment_status, provision]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_device('ros-talker', device, ['ros_workspace'])
        dep_deployment = client.get_deployment('deployment_id')
        provision_config.add_dependent_deployment(dep_deployment)
        self.assertEqual(provision_config.parameters["jakmybngjupwdjjdqztmcrjq"]["bridge_params"]["alias"],
                         'D239-Device')
        provision_config.set_component_alias("ros-talker", "parent")
        with self.assertRaises(DuplicateAliasException):
            pkg.provision('test_deployment_name', provision_config)
        self.assertEqual(mock_request.call_count, 5)

    @patch('rapyuta_io.clients.provision_client.ProvisionClient._execute_api')
    @patch('requests.request')
    def test_package_deployments_without_phase(self, mock_rest_client, mock_execute):
        mock_get_package = Mock()
        mock_get_package.text = SCOPED_TARGETED_PACKAGE
        mock_get_package.status_code = requests.codes.OK
        mock_rest_client.side_effect = [mock_get_package]
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.status_code = 200
        mock_execute.return_value.text = DEPLOYMENT_LIST
        client = get_client()
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/deployment/list'
        package = client.get_package('pkg-abcdefg')
        deployments = package.deployments()
        mock_execute.assert_called_once_with(expected_url, HttpMethod.GET,
                                             query_params={'package_uid': 'pkg-abcdefg'}, retry_limit=0)
        for deployment in deployments:
            self.assertTrue(deployment.is_partial)

    @patch('rapyuta_io.clients.provision_client.ProvisionClient._execute_api')
    @patch('requests.request')
    def test_package_deployments_with_phase(self, mock_rest_client, mock_execute):
        get_package = Mock()
        get_package.text = SCOPED_TARGETED_PACKAGE
        get_package.status_code = requests.codes.OK
        mock_rest_client.side_effect = [get_package]
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.status_code = 200
        mock_execute.return_value.text = DEPLOYMENT_LIST
        client = get_client()
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/deployment/list'
        package = client.get_package('pkg-abcdefg')
        deployments = package.deployments(phases=[DeploymentPhaseConstants.SUCCEEDED, DeploymentPhaseConstants.PROVISIONING])
        mock_execute.assert_called_once_with(expected_url, HttpMethod.GET,
                                             query_params={'package_uid': 'pkg-abcdefg', 'phase':
                                                 [DeploymentPhaseConstants.SUCCEEDED.value,
                                                  DeploymentPhaseConstants.PROVISIONING.value]},
                                             retry_limit=0)
        for deployment in deployments:
            self.assertTrue(deployment.is_partial)

    @patch('rapyuta_io.clients.provision_client.ProvisionClient._execute_api')
    @patch('requests.request')
    def test_package_deployments_with_phase_and_retry(self, mock_rest_client, mock_execute):
        get_package = Mock()
        get_package.text = SCOPED_TARGETED_PACKAGE
        get_package.status_code = requests.codes.OK
        mock_rest_client.side_effect = [get_package]
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.status_code = 200
        mock_execute.return_value.text = DEPLOYMENT_LIST
        client = get_client()
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/deployment/list'
        package = client.get_package('pkg-abcdefg')
        package.deployments(phases=[DeploymentPhaseConstants.SUCCEEDED, DeploymentPhaseConstants.PROVISIONING],
                            retry_limit=2)
        mock_execute.assert_called_once_with(expected_url, HttpMethod.GET,
                                             query_params={'package_uid': 'pkg-abcdefg', 'phase':
                                                 [DeploymentPhaseConstants.SUCCEEDED.value,
                                                  DeploymentPhaseConstants.PROVISIONING.value]},
                                             retry_limit=2)

    @patch('requests.request')
    def test_create_package(self, mock_request):
        mock_response = MagicMock(spec=Response)
        mock_response.text = CREATE_PACKAGE
        mock_response.status_code = requests.codes.OK
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/add'
        mock_request.return_value = mock_response
        get_client().create_package(MANIFEST)
        mock_request.assert_called_once_with(headers=headers,
                                             json=MANIFEST,
                                             method='POST',
                                             url=expected_url,
                                             params=None)

    @patch('requests.request')
    def test_create_package_package_with_same_exists(self, mock_request):
        mock_response = MagicMock(spec=Response)
        mock_response.text = CREATE_PACKAGE
        mock_response.status_code = requests.codes.CONFLICT
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/add'
        mock_request.return_value = mock_response
        with self.assertRaises(ConflictError):
            get_client().create_package(MANIFEST)
        mock_request.assert_called_once_with(headers=headers,
                                             json=MANIFEST,
                                             method='POST',
                                             url=expected_url,
                                             params=None)

    @patch('requests.request')
    def test_create_package_package_with_bad_request(self, mock_request):
        mock_response = MagicMock(spec=Response)
        mock_response.text = CREATE_PACKAGE
        mock_response.status_code = requests.codes.BAD_REQUEST
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/add'
        mock_request.return_value = mock_response
        with self.assertRaises(BadRequestError):
            get_client().create_package(MANIFEST)
        mock_request.assert_called_once_with(headers=headers,
                                             json=MANIFEST,
                                             method='POST',
                                             url=expected_url,
                                             params=None)

    @patch('rapyuta_io.rio_client.Client._get_manifest_from_file')
    @patch('requests.request')
    def test_create_package_from_manifest(self, mock_request, mock_get_manifest_path):
        mock_response = MagicMock()
        mock_response.text = CREATE_PACKAGE
        mock_response.status_code = requests.codes.OK
        mock_request.return_value = mock_response
        mock_get_manifest_path.return_value = MANIFEST
        manifest_filepath = '/path/to/listener.json'
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/add'
        get_client().create_package_from_manifest(manifest_filepath)
        mock_request.assert_called_once_with(headers=headers,
                                             json=MANIFEST,
                                             method='POST',
                                             url=expected_url,
                                             params=None)
        mock_get_manifest_path.assert_called_once_with(manifest_filepath)

    @patch('rapyuta_io.rio_client.Client._get_manifest_from_file')
    @patch('requests.request')
    def test_create_package_from_manifest_package_with_same_exists(self, mock_request,
                                                                   mock_get_manifest_path):
        mock_response = MagicMock()
        mock_response.text = CREATE_PACKAGE
        mock_response.status_code = requests.codes.CONFLICT
        mock_request.return_value = mock_response
        mock_get_manifest_path.return_value = MANIFEST
        manifest_filepath = '/path/to/listener.json'
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/add'
        with self.assertRaises(ConflictError):
            get_client().create_package_from_manifest(manifest_filepath)
        mock_request.assert_called_once_with(headers=headers,
                                             json=MANIFEST,
                                             method='POST',
                                             url=expected_url,
                                             params=None)
        mock_get_manifest_path.assert_called_once_with(manifest_filepath)

    @patch('rapyuta_io.rio_client.Client._get_manifest_from_file')
    @patch('requests.request')
    def test_create_package_from_manifest_package_with_bad_request(self, mock_request,
                                                                   mock_get_manifest_path):
        mock_response = MagicMock()
        mock_response.text = CREATE_PACKAGE
        mock_response.status_code = requests.codes.BAD_REQUEST
        mock_request.return_value = mock_response
        mock_get_manifest_path.return_value = MANIFEST
        manifest_filepath = '/path/to/listener.json'
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/add'
        with self.assertRaises(BadRequestError):
            get_client().create_package_from_manifest(manifest_filepath)
        mock_request.assert_called_once_with(headers=headers,
                                             json=MANIFEST,
                                             method='POST',
                                             url=expected_url,
                                             params=None)
        mock_get_manifest_path.assert_called_once_with(manifest_filepath)

    @patch('requests.request')
    def test_add_rosbag_job_success(self, rest_mock):
        component_id = 'jakmybngjupwdjjdqztmcrjq'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        rosbag_options = ROSBagOptions(all_topics=True)
        job = ROSBagJob(name='job', rosbag_options=rosbag_options)
        provision_config.add_rosbag_job('ros-talker', job)
        self.assertEqual(provision_config['context']['component_context'][component_id]
                         ['ros_bag_job_defs'][0]['name'], job.name)
        self.assertEqual(provision_config['context']['component_context'][component_id]
                         ['ros_bag_job_defs'][0]['recordOptions'], rosbag_options.serialize())

    @patch('requests.request')
    def test_add_rosbag_job_invalid_rosbag_job(self, rest_mock):
        expected_err = 'rosbag_job needs to a ROSBagJob object'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.add_rosbag_job('ros-talker', 'invalid')

        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_add_rosbag_job_to_device_component(self, rest_mock):
        component_id = 'jakmybngjupwdjjdqztmcrjq'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        job = ROSBagJob(name='job', rosbag_options=ROSBagOptions(all_topics=True),
                        upload_options=UploadOptions())
        provision_config.add_rosbag_job('ros-talker', job)
        self.assertEqual(provision_config['context']['component_context'][component_id]
                         ['ros_bag_job_defs'][0]['name'], job.name)
        self.assertEqual(provision_config['context']['component_context'][component_id]
                         ['ros_bag_job_defs'][0]['recordOptions'], job.rosbag_options.serialize())
        self.assertEqual(provision_config['context']['component_context'][component_id]
                         ['ros_bag_job_defs'][0]['uploadOptions'], job.upload_options.serialize())

    @patch('requests.request')
    def test_add_rosbag_jobs_with_same_name(self, rest_mock):
        expected_err = 'rosbag job with same name already exists'
        component_id = 'jakmybngjupwdjjdqztmcrjq'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE_DEVICE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        job1 = ROSBagJob(name='job', rosbag_options=ROSBagOptions(all_topics=True),
                        upload_options=UploadOptions())
        provision_config.add_rosbag_job('ros-talker', job1)
        job2 = ROSBagJob(name='job', rosbag_options=ROSBagOptions(all_topics=True),
                         upload_options=UploadOptions())
        with self.assertRaises(OperationNotAllowedError) as e:
            provision_config.add_rosbag_job('ros-talker', job2)
        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_add_rosbag_job_to_non_ros_component(self, rest_mock):
        expected_err = 'rosbag job is only supported for ros components'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_NON_ROS_VALIDATE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        job = ROSBagJob(name='job', rosbag_options=ROSBagOptions(all_topics=True))
        with self.assertRaises(OperationNotAllowedError) as e:
            provision_config.add_rosbag_job('ros-talker', job)

        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_remove_rosbag_job_from_device_component(self, rest_mock):
        component_id = 'jakmybngjupwdjjdqztmcrjq'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE_ROSBAG_JOB
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        self.assertEqual(provision_config.plan.components.components[0].rosBagJobDefs[0].name, 'rbag')
        provision_config.remove_rosbag_job('ros-talker', 'rbag')
        self.assertEqual(len(provision_config['context']['component_context'][component_id]['rosBagJobDefs']), 0)

    @patch('requests.request')
    def test_add_restart_policy_success(self, rest_mock):
        component_id = 'jakmybngjupwdjjdqztmcrjq'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_NO_VALIDATE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_restart_policy('ros-talker', RestartPolicy.Always)
        self.assertEqual(provision_config['context']['component_context'][component_id]
                         ['component_override']['restart_policy'],
                         RestartPolicy.Always.value)

    @patch('requests.request')
    def test_add_routed_networks_to_provision_config_invalid_routed_network(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        routed_network = str('invalid object')

        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.add_routed_networks([routed_network])
        self.assertEqual(str(e.exception), 'routed networks must be of type RoutedNetwork')

    @patch('requests.request')
    def test_add_routed_network_invalid_routed_network(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.add_routed_network('invalid', 'lo')
        self.assertEqual(str(e.exception),
                         'routed networks must be of type RoutedNetwork')

    @patch('requests.request')
    def test_add_routed_network_cloud_runtime_with_network_interface(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        routed_network = RoutedNetwork({'guid': 'test-network-id', 'runtime': 'cloud'})
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(OperationNotAllowedError) as e:
            provision_config.add_routed_network(routed_network, 'docker0')
        self.assertEqual(str(e.exception),
                         'cloud routed network does not bind to network interface')

    @patch('requests.request')
    def test_add_routed_network_to_provision_config_device_runtime(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        routed_network = RoutedNetwork({'guid': 'test-network-id', 'runtime': 'device',
                                        'parameters': {'NETWORK_INTERFACE': 'lo'}})
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_routed_network(routed_network, 'docker0')
        self.assertEqual(provision_config['context']['routedNetworks'],
                         [{'bindParameters': {'NETWORK_INTERFACE': 'docker0'}, 'guid': 'test-network-id'}])

    @patch('requests.request')
    def test_add_routed_network_to_provision_config_device(self, rest_mock):
        '''
        adding network interface to device routed network which is already present
        '''
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        routed_network = RoutedNetwork({'guid': 'test-network-id', 'runtime': 'device',
                                        'parameters': {'NETWORK_INTERFACE': 'lo'}})
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config['context']['routedNetworks'] = [{'guid': 'test-network-id'}]
        self.assertEqual(provision_config['context']['routedNetworks'],
                         [{'guid': 'test-network-id'}])
        provision_config.add_routed_network(routed_network, 'docker0')
        self.assertEqual(provision_config['context']['routedNetworks'],
                         [{'bindParameters': {'NETWORK_INTERFACE': 'docker0'}, 'guid': 'test-network-id'}])

    @patch('requests.request')
    def test_add_routed_network_to_provision_config_cloud(self, rest_mock):
        '''
        adding network interface to cloud routed network which is already added
        '''
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        routed_network = RoutedNetwork({'guid': 'test-network-id', 'runtime': 'device'})
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config['context']['routedNetworks'] = [{'guid': 'test-network-id'}]
        self.assertEqual(provision_config['context']['routedNetworks'],
                         [{'guid': 'test-network-id'}])
        provision_config.add_routed_network(routed_network)
        self.assertEqual(provision_config['context']['routedNetworks'],
                         [{'guid': 'test-network-id'}])

    @patch('requests.request')
    def test_add_routed_network_to_provision_config_device_runtime_with_diff_interface(self, rest_mock):
        '''
        The network interface value gets updated each time you call the function
        '''
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        routed_network = RoutedNetwork({'guid': 'test-network-id', 'runtime': 'device',
                                        'parameters': {'NETWORK_INTERFACE': 'lo'}})
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_routed_network(routed_network, 'docker0')
        self.assertEqual(provision_config['context']['routedNetworks'],
                         [{'bindParameters': {'NETWORK_INTERFACE': 'docker0'}, 'guid': 'test-network-id'}])
        provision_config.add_routed_network(routed_network, 'lo')
        self.assertEqual(provision_config['context']['routedNetworks'],
                         [{'bindParameters': {'NETWORK_INTERFACE': 'lo'}, 'guid': 'test-network-id'}])

    @patch('requests.request')
    def test_add_routed_network_to_provision_config_cloud_runtime(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        routed_network = RoutedNetwork({'guid': 'test-network-id', 'runtime': 'cloud'})
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_routed_network(routed_network)
        self.assertEqual(provision_config['context']['routedNetworks'],
                         [{'guid': 'test-network-id'}])

    @patch('requests.request')
    def test_add_routed_networks_to_provision_config(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        routed_network = RoutedNetwork({'guid': 'test-network-id', 'runtime': 'cloud'})
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_routed_networks([routed_network])
        self.assertEqual(provision_config['context']['routedNetworks'], [{'guid': 'test-network-id'}])

    @patch('requests.request')
    def test_add_native_networks_invalid_native_network(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        native_network = str('invalid object')

        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.add_native_networks([native_network])
        self.assertEqual(str(e.exception), 'native network must be of type NativeNetwork')

    @patch('requests.request')
    def test_add_native_network_invalid_native_network(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException) as e:
            provision_config.add_native_network('invalid native_network','lo')
        self.assertEqual(str(e.exception),
                         'native network must be of type NativeNetwork')

    @patch('requests.request')
    def test_add_native_network_cloud_runtime_with_network_interface(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        native_network = NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.KINETIC)
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(OperationNotAllowedError) as e:
            provision_config.add_native_network(native_network, 'docker0')
        self.assertEqual(str(e.exception),
                         'cloud native network does not bind to network interface')

    @patch('requests.request')
    def test_add_native_networks_to_provision_config_cloud_success(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        native_network = NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.KINETIC)
        native_network.guid = 'test-network-id'
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_native_networks([native_network])
        self.assertEqual(provision_config['context']['nativeNetworks'], [{'guid': 'test-network-id'}])

    @patch('requests.request')
    def test_add_native_networks_to_provision_config_device_success(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        device = Device('dev-name')
        device.uuid = 'random'
        device.ip_interfaces = {'lo': '0.0.0.0'}
        parameters = Parameters(device=device, network_interface='lo')
        native_network = NativeNetwork('native_network_name', Runtime.DEVICE, ROSDistro.KINETIC, parameters)
        native_network.guid = 'test-network-id'
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_native_network(native_network, 'lo')
        self.assertEqual(provision_config['context']['nativeNetworks'],
                         [{'bindParameters': {'NETWORK_INTERFACE': 'lo'}, 'guid': 'test-network-id'}])
        provision_config.add_native_network(native_network, 'docker0')
        self.assertEqual(provision_config['context']['nativeNetworks'],
                         [{'bindParameters': {'NETWORK_INTERFACE': 'docker0'}, 'guid': 'test-network-id'}])

    @patch('requests.request')
    def test_add_static_route(self, rest_mock):
        endpoint_name = 'test'
        static_route_name = 'test_route'
        component_id = 'jakmybngjupwdjjdqztmcrjq'
        component_name = 'ros-talker'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_NO_VALIDATE
        get_package_response.status_code = requests.codes.OK
        static_route_response = MagicMock()
        static_route_response.text = STATIC_ROUTE_RESPONSE
        static_route_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response, static_route_response]
        client = get_client()
        pkg = client.get_package('my_package')
        static_route = client.create_static_route(static_route_name)
        provision_config = pkg.get_provision_configuration('test-plan')
        provision_config.add_static_route(component_name, endpoint_name, static_route)
        self.assertEqual(
            provision_config['context']['component_context'][component_id]['static_route_config'][endpoint_name],
            static_route.guid)

    @patch('requests.request')
    def test_add_static_route_with_type_error(self, rest_mock):
        endpoint_name = 'test'
        component_name = 'ros-talker'
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_NO_VALIDATE
        get_package_response.status_code = requests.codes.OK
        static_route_response = MagicMock()
        static_route_response.text = STATIC_ROUTE_RESPONSE
        static_route_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response, static_route_response]
        client = get_client()
        pkg = client.get_package('my_package')
        static_route = {'key': 'not a static route'}
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(TypeError):
            provision_config.add_static_route(component_name, endpoint_name, static_route)

    @patch('requests.request')
    def test_get_static_route_by_name_name_not_found(self, rest_mock):
        static_route_response = MagicMock()
        static_route_response.text = None
        static_route_response.status_code = requests.codes.NOT_FOUND
        rest_mock.side_effect = [static_route_response]
        client = get_client()
        sr = client.get_static_route_by_name('test')
        self.assertIsNone(sr)

    @patch('requests.request')
    def test_delete_static_route_failure_invalid_route_guid(self, rest_mock):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/staticroute/delete'
        expected_payload = {'guid': 'invalid-route-guid'}
        static_route_response = MagicMock()
        static_route_response.text = '{"success":false,"error":"unable to find the resource from db: record not found"}'
        static_route_response.status_code = requests.codes.NOT_FOUND
        rest_mock.side_effect = [static_route_response]
        client = get_client()
        expected_err_msg = 'unable to find the resource from db: record not found'
        with self.assertRaises(ResourceNotFoundError) as e:
            client.delete_static_route('invalid-route-guid')
        rest_mock.assert_called_once_with(headers=headers, json=expected_payload, url=expected_url, method='DELETE',
                                          params={})
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_delete_static_route_success_valid_route_guid(self, rest_mock):
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/staticroute/delete'
        expected_payload = {'guid': 'valid-route-guid'}
        static_route_response = MagicMock()
        static_route_response.text = '{"success":true,"error":""}'
        static_route_response.status_code = requests.codes.OK
        rest_mock.side_effect = [static_route_response]
        client = get_client()
        client.delete_static_route('valid-route-guid')
        rest_mock.assert_called_once_with(headers=headers, json=expected_payload, url=expected_url, method='DELETE',
                                          params={})

    @patch('requests.request')
    def test_add_restart_policy_invalid_policy(self, rest_mock):
        get_package_response = MagicMock()
        get_package_response.text = PACKAGE_OK_NO_VALIDATE
        get_package_response.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response]
        client = get_client()
        pkg = client.get_package('my_package')
        provision_config = pkg.get_provision_configuration('test-plan')
        with self.assertRaises(InvalidParameterException):
            provision_config.add_restart_policy('ros-talker', 'forever')

    @patch('requests.request')
    def test_delete_package_success(self, rest_mock):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/serviceclass/delete?package_uid={}'.format('pkg-guid')
        mock_delete_package = Mock()
        mock_delete_package.text = 'null'
        mock_delete_package.status_code = requests.codes.OK
        rest_mock.side_effect = [mock_delete_package]
        client = get_client()
        client.delete_package('pkg-guid')
        rest_mock.assert_called_once_with(headers=headers, json=None,
                                          url=expected_url, method='DELETE',
                                          params=None)

    @patch('requests.request')
    def test_delete_package_with_package_object_success(self, rest_mock):
        get_package_response = MagicMock(spec=Response)
        get_package_response.text = PACKAGE_OK_VALIDATE
        get_package_response.status_code = requests.codes.OK
        mock_delete_package = Mock()
        mock_delete_package.text = 'null'
        mock_delete_package.status_code = requests.codes.OK
        rest_mock.side_effect = [get_package_response, mock_delete_package]
        client = get_client()
        pkg = client.get_package('pkg-guid')
        pkg.delete()

    @patch('requests.request')
    def test_delete_package_invalid_package_id(self, rest_mock):
        mock_delete_package = Mock()
        mock_delete_package.status_code = requests.codes.UNPROCESSABLE_ENTITY
        rest_mock.side_effect = [mock_delete_package]
        client = get_client()
        expected_err_msg = 'package_id must be a non-empty string'
        with self.assertRaises(InvalidParameterException) as e:
            client.delete_package(123)
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_delete_package_package_not_found(self, rest_mock):
        mock_delete_package = Mock()
        mock_delete_package.text = PACKAGE_NOT_FOUND
        mock_delete_package.status_code = requests.codes.NOT_FOUND
        rest_mock.side_effect = [mock_delete_package]
        client = get_client()
        with self.assertRaises(ResourceNotFoundError) as e:
            client.delete_package('pkg-guid')
        expected_err_msg = 'Package not found'
        self.assertEqual(str(e.exception), expected_err_msg)
