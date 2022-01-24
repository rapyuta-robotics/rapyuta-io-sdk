from __future__ import absolute_import

from rapyuta_io import DeviceArch
from rapyuta_io.clients.package import ExecutableMount, Runtime, RestartPolicy
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, delete_package, add_package, get_package

MOUNT_PATH = "/data"


class TestVolume(PackageTest):

    PV_READER_MANIFEST = 'pv-reader.json'
    PV_READER_PACKAGE = 'test-volume-pv-reader-pkg'
    DEVICE_VOLUME_MANIFEST = 'device-volume.json'
    DEVICE_VOLUME_PACKAGE = 'test-device-volume-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.PV_READER_MANIFEST, cls.PV_READER_PACKAGE)
        add_package(cls.DEVICE_VOLUME_MANIFEST, cls.DEVICE_VOLUME_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.PV_READER_PACKAGE)
        delete_package(cls.DEVICE_VOLUME_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.volume_instance = None
        self.deployment = None
        self.package = get_package(self.PV_READER_PACKAGE)
        self.device_package = get_package(self.DEVICE_VOLUME_PACKAGE)
        self.docker_device = self.config.get_devices(arch=DeviceArch.AMD64, runtime='Dockercompose')[0]
        self.docker_device.refresh()

    def tearDown(self):
        self.deprovision_all_deployments([self.deployment, self.volume_instance])

    def test_01_persistent_volume_as_dependent_deployment(self):
        self.logger.info("Started persistent volume as dependent deployment")
        self.volume_instance = self.get_persistent_volume_instance(instance_name='volume_instance')
        self.volume_instance.poll_deployment_till_ready()
        provision_configuration = self.package.get_provision_configuration()
        self.logger.info('Adding persistent volume as dependent deployment')
        provision_configuration.add_dependent_deployment(self.volume_instance)
        provision_configuration.mount_volume("default", volume=self.volume_instance, mount_path=MOUNT_PATH)
        self.deployment = self.deploy_package(self.package, provision_configuration)
        self.deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.deployment)
        self.validate_refresh()

    def test_02_persistent_volume_as_dependent_deployment_with_executable_mounts(self):
        self.logger.info("Started persistent volume as dependent deployment")
        self.volume_instance = self.get_persistent_volume_instance(instance_name='test_executable_mounts')
        self.volume_instance.poll_deployment_till_ready()
        provision_configuration = self.package.get_provision_configuration()
        self.logger.info('Adding persistent volume as dependent deployment')
        provision_configuration.add_dependent_deployment(self.volume_instance)
        executable_mounts = [
            ExecutableMount(exec_name='CompReaderExec', mount_path='/test_path', sub_path='test_subpath')]
        provision_configuration.mount_volume("default", volume=self.volume_instance, mount_path=None,
                                             executable_mounts=executable_mounts)
        self.deployment = self.deploy_package(self.package, provision_configuration)
        self.deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.deployment)

    def test_03_device_volume_with_executable_mounts(self):
        self.logger.info("Started device volume")
        self.volume_instance = None
        provision_configuration = self.device_package.get_provision_configuration()
        self.logger.info('Adding device to component')
        provision_configuration.add_device('default', self.docker_device)
        exec_mounts = [ExecutableMount('nginx', '/tmp/', '/home/rapyuta/Downloads/')]
        self.logger.info('Adding mount paths to device volume')
        provision_configuration.mount_volume('default', device=self.docker_device, mount_path=None, executable_mounts=exec_mounts)
        self.deployment = self.deploy_package(self.device_package, provision_configuration)
        self.deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.deployment)

    def validate_refresh(self):
        partial_volume = [v for v in self.get_persistent_volume().get_all_volume_instances()
                          if v.deploymentId == self.volume_instance.deploymentId][0]
        self.assertTrue(partial_volume.is_partial)
        partial_volume.refresh()
        self.assertFalse(partial_volume.is_partial)
        self.assertTrue(partial_volume.parameters)
