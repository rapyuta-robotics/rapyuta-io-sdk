from __future__ import absolute_import
import json

from rapyuta_io.utils import RestClient
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, add_package, delete_package, get_package


class TestCloudNonRosWithEndpoint(PackageTest):
    ENDPOINT_NAME = 'ep1'

    CLOUD_NON_ROS_MANIFEST = 'cloud-non-ros.json'
    CLOUD_NON_ROS_PACKAGE = 'test-cloud-non-ros-with-endpoint'

    @classmethod
    def setUpClass(cls):
        add_package(cls.CLOUD_NON_ROS_MANIFEST, cls.CLOUD_NON_ROS_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.CLOUD_NON_ROS_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.package = get_package(self.CLOUD_NON_ROS_PACKAGE)
        self.provision_config = self.package.get_provision_configuration()
        self.cnr_deployment = None

    def tearDown(self):
        self.deprovision_all_deployments([self.cnr_deployment])

    def validate_service_endpoint(self, endpoint_name, endpoint):
        self.logger.info('Checking the status of endpoint(%s) - %s' % (endpoint_name, endpoint))
        self.assert_endpoint_url(endpoint)
        self.logger.info('%s: Valid endpoint url' % endpoint)
        endpoint = endpoint + '/status'
        response = RestClient(endpoint).execute()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.text)['status'], 'running')
        self.logger.info('Endpoint %s returns status running' % endpoint)

    def test_cloud_non_ros(self):
        self.logger.info('Testing cloud non ros with endpoint and replicas')
        self.cnr_deployment = self.deploy_package(self.package, self.provision_config)
        self.cnr_deployment.poll_deployment_till_ready()

        binding_obj = self.get_service_binding(self.cnr_deployment)

        for internal_component in self.package.plans[0].internalComponents:
            component_id = internal_component.componentId
            component = binding_obj.credentials.components.get(component_id)
            if component:
                self.logger.info('Getting network endpoints from service binding')
                network_endpoints = component.networkEndpoints
                self.logger.info('Fetching the status of "%s" endpoint' % self.ENDPOINT_NAME)
                endpoint = network_endpoints.get(self.ENDPOINT_NAME)
                self.validate_service_endpoint(self.ENDPOINT_NAME, endpoint)

        self.validate_package_refresh()
        self.validate_deployment_refresh()

    def validate_package_refresh(self):
        partial_package = [p for p in self.config.client.get_all_packages() if p.packageId == self.package.packageId][0]
        self.assertTrue(partial_package.is_partial)
        with self.assertRaises(AttributeError):
            partial_package.ownerProject
        partial_package.refresh()
        self.assertFalse(partial_package.is_partial)
        self.assertTrue(partial_package.ownerProject)

    def validate_deployment_refresh(self):
        partial_deployment = [d for d in self.config.client.get_all_deployments()
                              if d.deploymentId == self.cnr_deployment.deploymentId][0]
        self.assertTrue(partial_deployment.is_partial)
        with self.assertRaises(AttributeError):
            partial_deployment.parameters
        partial_deployment.refresh()
        self.assertFalse(partial_deployment.is_partial)
        self.assertTrue(partial_deployment.parameters)
