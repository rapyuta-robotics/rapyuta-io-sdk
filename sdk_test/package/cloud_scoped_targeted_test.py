# encoding: utf-8

from __future__ import absolute_import

from rapyuta_io import DeviceArch
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, start_roscore, stop_roscore, add_package, delete_package, \
    get_package, add_cloud_native_network, add_cloud_routed_network, delete_native_network, delete_routed_network, \
    get_routed_network, get_native_network


class TestScopedTargeted(PackageTest):
    ST_DEV_COMP = "devicepong"

    SCOPED_TARGETED_PACKAGE = 'test-scoped-targeted'
    SCOPED_TARGETED_MANIFEST = 'scoped-targeted.json'

    SCOPED_CLOUD_PACKAGE = 'test-scoped-cloud'
    SCOPED_CLOUD_MANIFEST = 'scoped-cloud.json'

    NO_SCOPED_TARGETED_PACKAGE = 'test-no-scoped-targeted'
    NO_SCOPED_TARGETED_MANIFEST = 'no-scoped-targeted.json'

    @classmethod
    def setUpClass(cls):
        add_package(cls.SCOPED_TARGETED_MANIFEST, cls.SCOPED_TARGETED_PACKAGE
                    , build_map={
                        'cloudping': {'cloudy': ('pingpong-build', 'pingpong.json')}
        })
        add_package(cls.SCOPED_CLOUD_MANIFEST, cls.SCOPED_CLOUD_PACKAGE,
                    build_map={
                        'cloudping': {'cloudy': ('pingpong-build', 'pingpong.json')}
        })
        add_package(cls.NO_SCOPED_TARGETED_MANIFEST, cls.NO_SCOPED_TARGETED_PACKAGE)
        config = Configuration()
        devices = config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        start_roscore(devices[0])
        add_cloud_native_network('cloud_scoped_targeted_native_network')
        add_cloud_routed_network('cloud_scoped_targeted_routed_network')

    @classmethod
    def tearDownClass(cls):
        config = Configuration()
        devices = config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        stop_roscore(devices[0])
        delete_package(cls.SCOPED_TARGETED_PACKAGE, False)
        delete_package(cls.SCOPED_CLOUD_PACKAGE)
        delete_package(cls.NO_SCOPED_TARGETED_PACKAGE)
        delete_native_network('cloud_scoped_targeted_native_network')
        delete_routed_network('cloud_scoped_targeted_routed_network')

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        devices = self.config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        self.device = devices[0]
        self.deployments = []
        self.non_st_dep_deployment = None
        self.routed_network = get_routed_network('cloud_scoped_targeted_routed_network')
        self.native_network = get_native_network('cloud_scoped_targeted_native_network')

    def tearDown(self):
        self.deprovision_all_deployments(self.deployments)

    def test_scoped_targeted_package(self):
        package = get_package(self.SCOPED_TARGETED_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_device(self.ST_DEV_COMP, self.device, ignore_device_config=['network_interface'])
        provision_config.add_routed_networks([self.routed_network])
        deployment = self.deploy_package(package, provision_config)
        deployment.poll_deployment_till_ready()
        self.assert_deployment_status(deployment)
        self.deployments.append(deployment)

    def test_scoped_cloud_package_ros_namespace(self):
        package = get_package(self.SCOPED_CLOUD_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_native_network(self.native_network)
        provision_config.set_component_alias("cloudping", "cloudping", True)
        deployment = self.deploy_package(package, provision_config)
        deployment.poll_deployment_till_ready()
        comp_id = deployment.componentInfo[0].componentID
        self.assert_deployment_status_st_check(deployment, comp_id, "cloudping", True)
        self.assert_deployment_status(deployment)
        self.deployments.append(deployment)

    def test_scoped_targeted_package_non_alias_depends(self):
        package = get_package(self.SCOPED_TARGETED_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_device(self.ST_DEV_COMP, self.device, ignore_device_config=['network_interface'])
        provision_config.add_routed_networks([self.routed_network])
        comp_id = provision_config.plan.get_component_id(self.ST_DEV_COMP)
        st_deployment = self.deploy_package(package, provision_config)
        st_deployment.poll_deployment_till_ready()
        self.deployments.append(st_deployment)
        self.assert_deployment_status(st_deployment)
        self.assert_deployment_status_st_check(st_deployment, comp_id, self.device.name, False)
        package = get_package(self.NO_SCOPED_TARGETED_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_dependent_deployment(st_deployment)
        provision_config.add_routed_network(self.routed_network)
        non_st_dep_deployment = self.deploy_package(package, provision_config)
        self.assert_dependent_deployment(non_st_dep_deployment, [st_deployment])
        non_st_dep_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(non_st_dep_deployment)
        self.deployments.append(non_st_dep_deployment)

    def assert_deployment_status_st_check(self, deployment, component, alias, set_ros_namespace):
        componentobj = getattr(deployment.parameters, component)
        self.assertEqual(componentobj.bridge_params.alias, alias)
        self.assertEqual(componentobj.bridge_params.setROSNamespace, set_ros_namespace)
        self.logger.info('Deployment %s(%s) started successfully' % (deployment.name,
                                                                     deployment.packageId))
