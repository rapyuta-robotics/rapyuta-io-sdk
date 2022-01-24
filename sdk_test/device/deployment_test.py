from __future__ import absolute_import
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, add_package, delete_package, get_package
from rapyuta_io import DeviceArch
from rapyuta_io.utils import DeploymentRunningException


class TestDeployment(DeviceTest, PackageTest):
    TALKER_DOCKER_MANIFEST = 'talker-docker.json'
    TALKER_DOCKER_PACKAGE = 'test-deployment-talker-docker-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.TALKER_DOCKER_MANIFEST, cls.TALKER_DOCKER_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.TALKER_DOCKER_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        # Assumption: We only have one Arm32 device with Docker runtime.
        devices = self.config.get_devices(arch=DeviceArch.ARM32V7, runtime='Dockercompose')
        self.device = devices[0]

    def tearDown(self):
        pass

    def assert_get_deployments(self, deployment_id):
        self.logger.info('Asserting if some deployment is present')
        deployments = self.device.get_deployments()
        self.assertGreater(len(deployments), 0)
        deployment_exists = False
        for deployment in deployments:
            if deployment_id == deployment['io_deployment_id']:
                deployment_exists = True
                break
        self.assertTrue(deployment_exists, 'Current deployment should be present')

    def test_get_deployment(self):
        self.routed_network = self.create_cloud_routed_network('talker-routed-network')
        self.package = get_package(self.TALKER_DOCKER_PACKAGE)
        self.provision_config = self.package.get_provision_configuration()
        self.provision_config.add_device('default', self.device)
        self.provision_config.add_routed_network(self.routed_network)

        self.logger.info('Deploying talker package')
        self.talker_deployment = self.deploy_package(self.package, self.provision_config)
        self.talker_deployment.poll_deployment_till_ready(sleep_interval=20, retry_count=10)
        self.assert_get_deployments(self.talker_deployment.deploymentId)

        self.deprovision_all_deployments([self.talker_deployment])
        self.routed_network.delete()
        self.package = None

    def test_device_refresh(self):
        partial_device = [d for d in self.config.client.get_all_devices() if d.uuid == self.device.uuid][0]
        self.assertTrue(partial_device.is_partial)
        with self.assertRaises(AttributeError):
            partial_device.host
        partial_device.refresh()
        self.assertFalse(partial_device.is_partial)
        self.assertTrue(partial_device.host)
