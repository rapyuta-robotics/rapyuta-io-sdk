from __future__ import absolute_import

from rapyuta_io.clients.package import ROSDistro

from sdk_test.package.package_test import PackageTest
from sdk_test.config import Configuration
from sdk_test.util import get_logger, get_package, add_package, delete_package, \
    add_cloud_native_network, get_native_network, delete_native_network, delete_build


class NoeticTest(PackageTest):

    TALKER_MANIFEST = 'talker-noetic.json'
    TALKER_BUILD = 'test-noetic-talker-build'
    TALKER_PACKAGE = 'test-noetic-talker-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.TALKER_MANIFEST, cls.TALKER_PACKAGE, build_map={
            'talker': {'talkerExec': (cls.TALKER_BUILD, cls.TALKER_MANIFEST)},
        })
        add_cloud_native_network('noetic_cloud_network', ros_distro=ROSDistro.NOETIC)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.TALKER_PACKAGE)
        delete_native_network('noetic_cloud_network')

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.native_network = get_native_network('noetic_cloud_network')
        self.deployments = []

    def tearDown(self):
        self.deprovision_all_deployments(self.deployments)

    def test_scoped_targeted_package(self):
        package = get_package(self.TALKER_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_native_network(self.native_network)
        deployment = self.deploy_package(package, provision_config)
        deployment.poll_deployment_till_ready()
        self.assert_deployment_status(deployment)
        self.deployments.append(deployment)
