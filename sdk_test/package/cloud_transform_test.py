# encoding: utf-8

from __future__ import absolute_import
from rapyuta_io import DeviceArch
from rapyuta_io.clients.package import RestartPolicy
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, get_package, add_package, delete_package
import six


class TestCloudTransform(PackageTest):

    TALKER_MANIFEST = 'talker.json'
    LISTENER_MANIFEST = 'listener.json'
    CLOUD_TRANSFORM_MANIFEST = 'cloud-transform.json'

    TALKER_PACKAGE = 'test-cloud-transform-talker'
    LISTENER_PACKAGE = 'test-cloud-transform-listener'
    CLOUD_TRANSFORM_PACKAGE = 'test-cloud-transform-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.TALKER_MANIFEST, cls.TALKER_PACKAGE)
        add_package(cls.LISTENER_MANIFEST, cls.LISTENER_PACKAGE)
        add_package(cls.CLOUD_TRANSFORM_MANIFEST, cls.CLOUD_TRANSFORM_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.TALKER_PACKAGE)
        delete_package(cls.LISTENER_PACKAGE)
        delete_package(cls.CLOUD_TRANSFORM_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        devices = self.config.get_devices(arch=DeviceArch.AMD64, runtime='Preinstalled')
        self.device = devices[0]
        self.routed_network = self.create_cloud_routed_network('cloud_transform_network')

        self.talker_deployment = None
        self.cloud_transform_deployment = None
        self.listener_deployment = None

    def tearDown(self):
        self.deprovision_all_deployments([self.talker_deployment, self.cloud_transform_deployment,
                                          self.listener_deployment])
        self.routed_network.delete()

    def assert_deployment_list_with_device_id(self):
        dev_id = self.device.get('uuid')
        filtered_deployments = self.config.client.get_all_deployments(device_id=dev_id)
        filtered_deployment_ids = map(lambda dep: dep['deploymentId'], filtered_deployments)
        device_deployments = self.device.get_deployments()
        device_deployment_ids = map(lambda dep: dep['io_deployment_id'], device_deployments)
        six.assertCountEqual(self, filtered_deployment_ids, device_deployment_ids, 'both deployments should match')

    def deploy_talker_package(self):
        package = get_package(self.TALKER_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_device('default', self.device, ignore_device_config=['network_interface'])
        provision_config.add_routed_network(self.routed_network)
        self.logger.info('Deploying talker package')
        self.talker_deployment = self.deploy_package(package, provision_config)

    def deploy_cloud_transform_package(self):
        package = get_package(self.CLOUD_TRANSFORM_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_routed_network(self.routed_network)
        provision_config.add_dependent_deployment(self.talker_deployment)
        self.logger.info('Deploying cloud transform package')
        self.cloud_transform_deployment = self.deploy_package(package, provision_config)
        self.assert_dependent_deployment(self.cloud_transform_deployment, [self.talker_deployment])

    def deploy_listener_package(self, restart_policy):
        package = get_package(self.LISTENER_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_device('default', self.device, ignore_device_config=['network_interface'])
        provision_config.add_routed_network(self.routed_network)
        provision_config.add_dependent_deployment(self.cloud_transform_deployment)
        provision_config.add_restart_policy('default', restart_policy)
        self.listener_deployment = self.deploy_package(package, provision_config)
        self.assert_dependent_deployment(self.listener_deployment, [self.cloud_transform_deployment])

    def test_deploy_cloud_transform(self):
        self.deploy_talker_package()
        self.talker_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.talker_deployment)
        self.deploy_cloud_transform_package()
        self.cloud_transform_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.cloud_transform_deployment)
        self.deploy_listener_package(RestartPolicy.Always)
        self.listener_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.listener_deployment)
        listener_provision_config = get_package(self.LISTENER_PACKAGE).get_provision_configuration()
        listener_component_id = listener_provision_config.plan.get_component_id("default")
        component_context = self.listener_deployment.provisionContext.component_context[listener_component_id]
        self.assertEqual(component_context.component_override.restart_policy, RestartPolicy.Always)
        self.assert_deployment_list_with_device_id()
