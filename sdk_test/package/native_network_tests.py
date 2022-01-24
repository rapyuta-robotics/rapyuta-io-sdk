from __future__ import absolute_import
from rapyuta_io import DeploymentStatusConstants, DeviceArch
from rapyuta_io.clients.deployment import DeploymentPhaseConstants
from rapyuta_io.clients.native_network import NativeNetwork, NativeNetworkLimits, Parameters
from rapyuta_io.clients.package import Runtime, ROSDistro
from rapyuta_io.utils.utils import generate_random_value
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, get_package, add_package, delete_package

NETWORK_INTERFACE = 'network_interface'

class NativeNetworkTest(PackageTest, DeviceTest):

    native_network = None

    TALKER_CLOUD_MANIFEST = 'talker-cloud.json'
    TALKER_CLOUD_PACKAGE = 'test-native-network-talker-cloud-pkg'
    TALKER_DEVICE_MANIFEST = 'talker-docker.json'
    TALKER_DEVICE_PACKAGE = 'test-native-network-talker-device-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.TALKER_CLOUD_MANIFEST, cls.TALKER_CLOUD_PACKAGE)
        add_package(cls.TALKER_DEVICE_MANIFEST, cls.TALKER_DEVICE_PACKAGE)
    @classmethod
    def tearDownClass(cls):
        delete_package(cls.TALKER_CLOUD_PACKAGE)
        delete_package(cls.TALKER_DEVICE_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.name = 'net-' + generate_random_value()
        self.ros_distro = ROSDistro.MELODIC
        self.runtime = Runtime.CLOUD
        self.parameters = Parameters(NativeNetworkLimits.SMALL)
        self.device_runtime = Runtime.DEVICE
        self.docker_device = self.config.get_devices(arch=DeviceArch.AMD64, runtime='Dockercompose')[0]
        self.docker_device.refresh()
        self.arm_device = self.config.get_devices(arch=DeviceArch.ARM32V7, runtime='Dockercompose')[0]
        self.arm_device.refresh()
        self.device_parameters = Parameters(limits=None, device=self.docker_device, network_interface='docker0')

    def add_network_interface_config_variable(self, device):
        self.logger.info('Adding network interface config variable')
        config_vars = device.get_config_variables()
        for config_var in config_vars:
            if config_var.key == NETWORK_INTERFACE:
                config_var.value = 'docker0'
                device.update_config_variable(config_var)
                return
        device.add_config_variable(NETWORK_INTERFACE, 'docker0')
        self.logger.info('Added network interface config variable')

    def delete_network_interface_config_variable(self, device):
        self.logger.info('Removing network interface config variable')
        config_vars = device.get_config_variables()
        for config_var in config_vars:
            if config_var.key == NETWORK_INTERFACE:
                device.delete_config_variable(config_id=config_var.id)
                break
        self.logger.info('Removed network interface config variable')

    def assert_native_network_status(self):
        self.logger.info('Checking the deployment status of the native network {}'.format(self.name))
        status = self.native_network.get_status()
        self.assertEqual(status.status, DeploymentStatusConstants.RUNNING.value)
        self.assertEqual(status.phase, DeploymentPhaseConstants.SUCCEEDED.value)
        self.logger.info('native network %s(%s) started successfully' % (self.native_network.name,
                                                                         self.native_network.guid))

    def assert_native_network_fields(self, native_network):
        self.logger.info('comparing the details the native network {} just fetched'.format(self.name))
        self.assertEqual(self.native_network.name, native_network.name)
        self.assertEqual(self.native_network.runtime, native_network.runtime)
        self.assertEqual(self.native_network.ros_distro, native_network.ros_distro)
        self.assertEqual(self.native_network.parameters.limits.cpu, native_network.parameters.limits.cpu)
        self.assertEqual(self.native_network.parameters.limits.memory, native_network.parameters.limits.memory)
        self.assertEqual(self.native_network.created_at, native_network.created_at)
        self.assertEqual(self.native_network.updated_at, native_network.updated_at)
        self.assertEqual(self.native_network.guid, native_network.guid)
        self.assertEqual(self.native_network.owner_project, native_network.owner_project)
        self.assertEqual(self.native_network.creator, native_network.creator)
        self.assertEqual(self.native_network.internal_deployment_guid,
                         native_network.internal_deployment_guid)
        self.assertEqual(self.native_network.internal_deployment_status.phase,
                         native_network.internal_deployment_status.phase)
        self.logger.info('successfully checked the contents of the native network'.format(self.name))

    def assert_native_network_present_in_list(self, all_native_network):
        self.logger.info('Checking the presence of native network {}'.format(self.name))
        guid = self.native_network.guid
        native_network_list = list(filter(lambda network: network.guid == guid, all_native_network))
        self.logger.info('Checking if only one native native network with id {} is present'
                         .format(self.native_network.guid))
        native_network = native_network_list[0]
        self.assertEqual(len(native_network_list), 1)
        self.assertEqual(self.native_network.name, native_network.name)
        self.logger.info('native network {} present'.format(self.name))

    def assert_native_network_stopped(self):
        self.logger.info('Checking if the native network {} stopped'.format(self.name))
        guid = self.native_network.guid
        all_native_network = self.config.client.list_native_networks()
        native_network = list(filter(lambda network: network.guid == guid, all_native_network))[0]
        self.assertEqual(native_network.internal_deployment_status.phase,
                         DeploymentPhaseConstants.DEPLOYMENT_STOPPED.value)
        self.logger.info('native network {} stopped'.format(self.name))

    def validate_refresh(self, guid):
        partial_net = [n for n in self.config.client.list_native_networks() if n.guid == guid][0]
        self.assertTrue(partial_net.is_partial)
        self.assertFalse(partial_net.internal_deployment_status.status)
        partial_net.refresh()
        self.assertFalse(partial_net.is_partial)
        self.assertTrue(partial_net.internal_deployment_status.status)

    def test_01_create_native_network(self):
        self.logger.info('creating native network {}'.format(self.name))
        native_network_payload = NativeNetwork(self.name, self.runtime, self.ros_distro, self.parameters)
        self.native_network = self.config.client.create_native_network(native_network_payload)
        self.logger.info('polling till the native network {} is ready'.format(self.name))
        self.native_network.poll_native_network_till_ready()
        self.__class__.native_network = self.config.client.get_native_network(self.native_network.guid)
        self.assert_native_network_status()
        self.validate_refresh(self.native_network.guid)

    def test_02_get_native_network(self):
        self.logger.info('fetching the native network {} just created'.format(self.name))
        guid = self.native_network.guid
        native_network = self.config.client.get_native_network(guid)
        self.assert_native_network_fields(native_network)

    def test_03_list_native_networks(self):
        self.logger.info('fetching the list of all the native networks')
        all_native_network = self.config.client.list_native_networks()
        self.assert_native_network_present_in_list(all_native_network)

    def test_04_add_native_network_to_package(self):
        self.logger.info('Started creating package talker component')
        app_package = get_package(self.TALKER_CLOUD_PACKAGE)
        prov_config = app_package.get_provision_configuration()
        self.logger.info('adding the native network {} to the provision configuration of the package'.format(self.name))
        prov_config.add_native_network(self.native_network)
        guid = self.native_network.guid
        self.assertEqual(prov_config.context['nativeNetworks'], [{"guid": guid}])
        self.logger.info('creating deployment')
        deployment = app_package.provision("test_deployment", prov_config)
        self.logger.info('polling till deployment is ready')
        deployment.poll_deployment_till_ready()
        self.logger.info('deployment is ready')
        deployment.deprovision()
        self.logger.info('de-provisioning the deployment')

    def test_05_delete_native_network(self):
        self.logger.info('deleting the native network {}'.format(self.name))
        guid = self.native_network.guid
        self.config.client.delete_native_network(guid)
        self.assert_native_network_stopped()


    def test_06_create_device_native_network(self):
        self.add_network_interface_config_variable(self.docker_device)
        self.logger.info('Started creating device native network')
        native_network_payload = NativeNetwork(self.name, Runtime.DEVICE, self.ros_distro, self.device_parameters)
        self.native_network  = self.config.client.create_native_network(native_network_payload)
        guid = self.native_network.guid
        self.logger.info('polling till the native network {} is ready'.format(self.name))
        self.native_network.poll_native_network_till_ready()
        self.__class__.native_network = self.config.client.get_native_network(guid)
        self.assert_native_network_status()
        self.validate_refresh(guid)
        self.assertEqual(self.native_network.runtime, self.device_runtime)

        self.add_network_interface_config_variable(self.arm_device)
        self.logger.info('Started creating package talker component')
        app_package = get_package(self.TALKER_DEVICE_PACKAGE)
        prov_config = app_package.get_provision_configuration()
        prov_config.add_device('default', self.arm_device)
        prov_config.add_native_network(self.native_network, 'docker0')
        self.assertEqual(prov_config.context['nativeNetworks'], [{"guid": guid, "bindParameters":
            {"NETWORK_INTERFACE": 'docker0'}}])
        self.logger.info('creating deployment')
        ignored_device_configs = ['ros_workspace', 'ros_distro']
        deployment = self.deploy_package(app_package, prov_config, device=self.arm_device,
                                         ignored_device_configs=ignored_device_configs)
        self.logger.info('polling till deployment is ready')
        deployment.poll_deployment_till_ready(retry_count=50)
        self.logger.info('deployment is ready')
        deployment.deprovision()
        self.logger.info('deprovisioned the deployment')
        self.delete_network_interface_config_variable(self.arm_device)

        self.logger.info('Delete routed network with guid : %s' % guid)
        self.config.client.delete_native_network(guid)
        self.assert_native_network_stopped()
        self.delete_network_interface_config_variable(self.docker_device)
