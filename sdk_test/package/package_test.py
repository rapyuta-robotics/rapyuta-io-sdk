from __future__ import absolute_import

import re
import unittest

import requests

from rapyuta_io import DeploymentStatusConstants, ROSDistro
from rapyuta_io.clients.deployment import Deployment, DeploymentPhaseConstants
from rapyuta_io.clients.persistent_volumes import VolumeInstance, PersistentVolumes, DiskCapacity
from rapyuta_io.utils import to_objdict, RestClient
from rapyuta_io.utils.utils import generate_random_value

DEFAULT_DISK_CAPACITY = DiskCapacity.GiB_32


class PackageTest(unittest.TestCase):

    def setUp(self):
        self.logger = None

    def get_persistent_volume(self):
        persistent_volume = self.config.client.get_persistent_volume()
        self.assertIsNotNone(persistent_volume, 'Persistent volume package should not be empty')
        self.assertTrue(isinstance(persistent_volume, PersistentVolumes),
                        'Object should be instance of PersistanceVolumes class')
        self.assertEqual('io-public-persistent-volume', persistent_volume.packageId,
                         'Package should be same')
        return persistent_volume

    def get_persistent_volume_instance(self, instance_name, disk_capacity=DEFAULT_DISK_CAPACITY):
        self.logger.info('Creating volume instance')
        persistent_volume = self.get_persistent_volume()
        volume_instance = persistent_volume.create_volume_instance(instance_name, disk_capacity)
        self.assertTrue(isinstance(volume_instance, VolumeInstance),
                        'Object should be an instance of VolumeInstance class')
        return volume_instance

    def deploy_package(self, package, provision_config, device=None, ignored_device_configs=None):
        self.logger.info('Started deploying the package %s' % package.packageName)
        deployment_name = generate_random_value()
        deployment = package.provision(deployment_name, provision_config)
        self.assert_deployment(deployment)
        self.assert_deployment_info(deployment_name, deployment, package)
        self.assert_component_parameters(deployment, package.plans[0], device,
                                         ignored_device_configs)
        return deployment

    def assert_deployment(self, deployment):
        self.assertTrue(isinstance(deployment, Deployment),
                        'Object should be an instance of Deployment class')
        self.logger.info('Package (%s) deployed (%s) successfully'
                         % (deployment.packageName, deployment.name))

    def assert_component_parameters(self, deployment, plan, device=None,
                                    ignored_device_configs=None):
        if ignored_device_configs is None:
            ignored_device_configs = []
        if device and device.get_runtime() == device.PRE_INSTALLED:
            ignored_device_configs.append('rosbag_mount_path')
        self.logger.info('Validating component parameters for the deployment: %s' % deployment.name)
        for component in plan.internalComponents:
            component_id = component.componentId
            component_params = deployment.parameters[component_id]
            self.assertEqual(component_params["component_id"], component_id)
            if component.runtime == "device" and device:
                for config_var in device.config_variables:
                    if config_var.key in ignored_device_configs:
                        continue
                    self.assertEqual(component_params[config_var.key], config_var.value)
                self.assertEqual(component_params["device_id"], device.uuid)

    def assert_deployment_info(self, deployment_name, deployment, package):
        self.logger.info('Validating deployment info for the deployment: %s(%s)'
                         % (deployment.name, deployment.packageName))
        self.assertEqual(deployment.name, deployment_name)
        self.assertEqual(deployment.packageId, package.packageId)
        self.assertEqual(deployment.packageName, package.packageName)
        self.assertEqual(deployment.planId, package.plans[0].planId)

    def assert_dependent_deployment(self, deployment, dependent_deployments):
        self.logger.info('Validating dependent deployment info for the deployment: %s(%s)'
                         % (deployment.name, deployment.packageName))
        dependent_deployment_id_list = list()
        for dependent_deployment in deployment.dependentDeployments:
            dependent_deployment_id_list.append(dependent_deployment["dependentDeploymentId"])

        for dependent_deployment in dependent_deployments:
            self.assertIn(dependent_deployment.deploymentId, dependent_deployment_id_list)

    def assert_deployment_status(self, deployment):
        self.logger.info('Checking deployment status')
        deployment_status = deployment.get_status()
        self.assertEqual(deployment_status.status, DeploymentStatusConstants.RUNNING.value)
        self.assertEqual(deployment_status.phase, DeploymentPhaseConstants.SUCCEEDED.value)
        self.logger.info('Deployment %s(%s) started successfully' % (deployment.name,
                                                                     deployment.packageId))

    def assert_endpoint_url(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        self.assertRegexpMatches(url, regex, 'Endpoint should ben an url')

    def assert_static_route(self, url):
        # Asserts that the URL (nginx server) is reachable and is returning a success status code
        response = RestClient(url).execute()
        self.assertEqual(response.status_code, requests.codes.OK)

    def get_service_binding(self, deployment):
        self.logger.info('Sending binding request for the deployment %s' % deployment.name)
        binding = deployment.get_service_binding()
        self.assertIsNotNone(binding)
        self.assertIn('credentials', binding, 'Credentials not found on the binding response')
        if not bool(binding):
            raise AssertionError('binding result should not empty')
        binding_obj = to_objdict(binding)
        return binding_obj

    def deprovision_all_deployments(self, deployments):
        self.logger.info("Tear down!. Stopping all the deployments")
        retry_count = 5
        total_deployments = 0
        success_count = 0
        for deployment in deployments:
            if not deployment:
                continue
            try:
                total_deployments = total_deployments + 1
                if isinstance(deployment, Deployment):
                    deployment.deprovision(retry_count)
                    self.logger.info('Deployment stopped: %s' % deployment.name)
                    success_count = success_count + 1
                elif isinstance(deployment, VolumeInstance):
                    deployment.destroy_volume_instance(retry_count)
                    self.logger.info('Volume instance deleted: %s' % deployment.name)
                    success_count = success_count + 1
            except Exception as err:
                self.logger.error('Failed to stop deployment %s' % deployment.name)
                self.logger.error(err)
        self.logger.info('%d Deployment(s) were stopped out of %d' % (success_count,
                                                                      total_deployments))

    def create_cloud_routed_network(self, name, ros_distro=ROSDistro.KINETIC):
        routed_network = self.config.client.create_cloud_routed_network(name, ros_distro, True)
        routed_network.poll_routed_network_till_ready()
        return routed_network
