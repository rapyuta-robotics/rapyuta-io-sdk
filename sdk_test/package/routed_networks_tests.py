from __future__ import absolute_import
from rapyuta_io import DeploymentStatusConstants, DeviceArch
from rapyuta_io.clients.deployment import DeploymentPhaseConstants
from rapyuta_io.clients.package import Runtime, ROSDistro, RestartPolicy
from rapyuta_io.utils.utils import generate_random_value
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, add_package, delete_package, get_package
from rapyuta_io.clients.routed_network import Parameters, RoutedNetworkLimits


class RoutedNetworkTest(PackageTest, DeviceTest):

    LISTENER_MANIFEST = 'listener.json'
    LISTENER_PACKAGE = 'test-routed-network-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.LISTENER_MANIFEST, cls.LISTENER_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.LISTENER_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.name = 'net-' + generate_random_value()
        self.routed_network = None
        self.ros_distro = ROSDistro.MELODIC
        self.shared = True
        self.routed_network = None
        self.docker_device = self.config.get_devices(arch=DeviceArch.AMD64, runtime='Dockercompose')[0]
        self.supervisor_device = self.config.get_devices(arch=DeviceArch.AMD64, runtime='Preinstalled')[0]
        self.parameters = Parameters(RoutedNetworkLimits.SMALL)

    def create_routed_network(self, runtime, parameters):
        if runtime == Runtime.CLOUD:
            self.routed_network = self.config.client.create_cloud_routed_network(
                self.name, self.ros_distro, self.shared)
        else:
            device = self.config.client.get_device(parameters['device_id'])
            self.routed_network = self.config.client.create_device_routed_network(
                self.name, self.ros_distro, self.shared, device,
                parameters['NETWORK_INTERFACE'], parameters['restart_policy'])
        self.routed_network.poll_routed_network_till_ready()

    def assert_deployment_status(self, routed_network):
        self.logger.info('Checking network status')
        status = routed_network.get_status()
        self.assertEqual(status.status, DeploymentStatusConstants.RUNNING.value)
        self.assertEqual(status.phase, DeploymentPhaseConstants.SUCCEEDED.value)
        self.logger.info('network %s(%s) started successfully' % (routed_network.name,
                                                                  routed_network.guid))

    def assert_routed_network_present_in_list(self, guid):
        all_routed_network = self.config.client.get_all_routed_networks()
        routed_network = list(filter(lambda network: network.guid == guid, all_routed_network))[0]
        self.assertEqual(routed_network.name, self.routed_network.name)

    def assert_routed_network_stopped(self, guid):
        all_routed_network = self.config.client.get_all_routed_networks()
        routed_network = list(filter(lambda network: network.guid == guid, all_routed_network))[0]
        self.assertEqual(routed_network.internalDeploymentStatus.phase,
                         DeploymentPhaseConstants.DEPLOYMENT_STOPPED.value)

    def validate_refresh(self, guid):
        partial_net = [n for n in self.config.client.get_all_routed_networks() if n.guid == guid][0]
        self.assertTrue(partial_net.is_partial)
        with self.assertRaises(AttributeError):
            partial_net.internalDeploymentStatus.status
        partial_net.refresh()
        self.assertFalse(partial_net.is_partial)
        self.assertTrue(partial_net.internalDeploymentStatus.status)

    def test_add_device_routed_network(self):
        self.logger.info('Started creating device routed network')
        self.create_routed_network(Runtime.DEVICE, {'device_id': self.docker_device.deviceId,
                                                    'NETWORK_INTERFACE': 'lo',
                                                    'restart_policy': RestartPolicy.OnFailure})

        self.logger.info('getting device routed network')
        self.routed_network = self.config.client.get_routed_network(self.routed_network.guid)
        self.assertEqual(self.routed_network.runtime, 'device')
        self.assertEqual(self.routed_network.guid, self.routed_network.guid)
        self.assertEqual(self.routed_network.parameters, {'device_id': self.docker_device.deviceId,
                                                          'NETWORK_INTERFACE': 'lo',
                                                          'restart_policy': RestartPolicy.OnFailure})
        self.assert_deployment_status(self.routed_network)
        self.assert_routed_network_present_in_list(self.routed_network.guid)

        self.logger.info('Started creating package listener component')
        app_package = get_package(self.LISTENER_PACKAGE)
        prov_config = app_package.get_provision_configuration()
        ignore_device_config = ['network_interface']
        prov_config.add_device('default', self.supervisor_device, ignore_device_config=ignore_device_config)
        prov_config.add_routed_network(self.routed_network, 'docker0')
        guid = self.routed_network.guid
        self.assertEqual(prov_config.context['routedNetworks'], [{"guid": guid, "bindParameters":
            {"NETWORK_INTERFACE": 'docker0'}}])
        self.logger.info('creating deployment')
        deployment = self.deploy_package(app_package, prov_config, device=self.supervisor_device,
                                         ignored_device_configs=ignore_device_config)
        deployment.poll_deployment_till_ready()
        deployment.deprovision()

        self.logger.info('Delete routed network with guid : %s' % guid)
        self.routed_network.delete()
        self.assert_routed_network_stopped(guid)

    def test_create_cloud_routed_network(self):
        self.logger.info('Started creating cloud routed network')
        self.create_routed_network(Runtime.CLOUD, {})
        routed_network = self.config.client.get_routed_network(self.routed_network.guid)
        self.assertEqual(self.routed_network.runtime, 'cloud')
        self.assertEqual(routed_network.guid, self.routed_network.guid)
        self.assertEqual(routed_network.parameters, self.parameters.to_dict())
        self.assert_deployment_status(routed_network)
        self.assert_routed_network_present_in_list(routed_network.guid)
        guid = self.routed_network.guid
        self.logger.info('Delete routed network with guid : %s' % guid)
        routed_network.delete()
        self.assert_routed_network_stopped(guid)

    def test_create_cloud_routed_network_with_parameters(self):
        self.logger.info('Started creating cloud routed network with parameters')
        self.create_routed_network(Runtime.CLOUD, Parameters(RoutedNetworkLimits.SMALL))
        routed_network = self.config.client.get_routed_network(self.routed_network.guid)
        self.assertEqual(self.routed_network.runtime, 'cloud')
        self.assertEqual(routed_network.guid, self.routed_network.guid)
        self.assertEqual(routed_network.parameters, self.parameters.to_dict())
        self.assert_deployment_status(routed_network)
        self.assert_routed_network_present_in_list(routed_network.guid)
        guid = self.routed_network.guid
        self.validate_refresh(guid)
        self.logger.info('Delete routed network with guid : %s' % guid)
        self.config.client.delete_routed_network(guid)
        self.assert_routed_network_stopped(guid)

    def test_create_device_routed_network(self):
        self.logger.info('Started creating device routed network')
        self.create_routed_network(Runtime.DEVICE, {'device_id': self.docker_device.deviceId,
                                                    'NETWORK_INTERFACE': 'docker0',
                                                    'restart_policy': RestartPolicy.OnFailure})
        self.routed_network = self.config.client.get_routed_network(self.routed_network.guid)
        self.assertEqual(self.routed_network.runtime, 'device')
        self.assertEqual(self.routed_network.guid, self.routed_network.guid)
        self.assertEqual(self.routed_network.parameters, {'device_id': self.docker_device.deviceId,
                                                          'NETWORK_INTERFACE': 'docker0',
                                                          'restart_policy': RestartPolicy.OnFailure})
        self.assert_deployment_status(self.routed_network)
        self.assert_routed_network_present_in_list(self.routed_network.guid)
        guid = self.routed_network.guid
        self.logger.info('Delete routed network with guid : %s' % guid)
        self.routed_network.delete()
        self.assert_routed_network_stopped(guid)
