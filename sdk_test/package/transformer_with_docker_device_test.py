from __future__ import absolute_import
from rapyuta_io import DeviceArch
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, get_package, delete_package, add_package


class TestTransformerWithDockerDevice(PackageTest):

    TALKER_DOCKER_MANIFEST = 'talker-docker.json'
    LISTENER_DOCKER_MANIFEST = 'listener-docker.json'
    CLOUD_TRANSFORM_MANIFEST = 'cloud-transform.json'

    TALKER_DOCKER_PACKAGE = 'test-transformer-talker-docker-pkg'
    LISTENER_DOCKER_PACKAGE = 'test-transformer-listener-docker-pkg'
    CLOUD_TRANSFORM_PACKAGE = 'test-transformer-cloud-transform-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.TALKER_DOCKER_MANIFEST, cls.TALKER_DOCKER_PACKAGE)
        add_package(cls.LISTENER_DOCKER_MANIFEST, cls.LISTENER_DOCKER_PACKAGE)
        add_package(cls.CLOUD_TRANSFORM_MANIFEST, cls.CLOUD_TRANSFORM_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.TALKER_DOCKER_PACKAGE)
        delete_package(cls.LISTENER_DOCKER_PACKAGE)
        delete_package(cls.CLOUD_TRANSFORM_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.device = self.config.get_devices(arch=DeviceArch.AMD64, runtime='Dockercompose')[0]
        self.talker_deployment = None
        self.cloud_transform_deployment = None
        self.listener_deployment = None
        self.routed_network = self.create_cloud_routed_network('transformer_with_docker_device')

    def tearDown(self):
        self.deprovision_all_deployments([self.talker_deployment, self.cloud_transform_deployment,
                                          self.listener_deployment])
        self.routed_network.delete()

    def deploy_talker_package(self, device):
        self.logger.info('Deploying talker package')
        package = get_package(self.TALKER_DOCKER_PACKAGE)
        provision_config = package.get_provision_configuration()
        ignored_device_configs = ['ros_workspace', 'ros_distro']
        provision_config.add_device("default", device, ignored_device_configs)
        provision_config.add_routed_network(self.routed_network)
        self.talker_deployment = self.deploy_package(package, provision_config, device,
                                                     ignored_device_configs)

    def deploy_cloud_transform_package(self):
        package = get_package(self.CLOUD_TRANSFORM_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_dependent_deployment(self.talker_deployment)
        provision_config.add_routed_network(self.routed_network)
        self.logger.info('Deploying cloud transform package')
        self.cloud_transform_deployment = self.deploy_package(package, provision_config)
        self.assert_dependent_deployment(self.cloud_transform_deployment, [self.talker_deployment])

    def deploy_listener_package(self, device):
        package = get_package(self.LISTENER_DOCKER_PACKAGE)
        provision_config = package.get_provision_configuration()
        ignored_device_configs = ['ros_workspace', 'ros_distro']
        provision_config.add_device("default", device, ignored_device_configs)
        provision_config.add_routed_networks([self.routed_network])
        provision_config.add_dependent_deployment(self.cloud_transform_deployment)
        self.listener_deployment = self.deploy_package(package, provision_config, device,
                                                       ignored_device_configs)
        self.assert_dependent_deployment(self.listener_deployment, [self.cloud_transform_deployment])

    def test_deploy_transformer_with_docker_device(self):
        self.logger.info('Started transformer with docker device test case')
        self.deploy_talker_package(self.device)
        self.talker_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.talker_deployment)
        self.deploy_cloud_transform_package()
        self.cloud_transform_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.cloud_transform_deployment)
        self.deploy_listener_package(self.device)
        self.listener_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.listener_deployment)
