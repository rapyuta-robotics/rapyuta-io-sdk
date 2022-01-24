from __future__ import absolute_import
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, add_package, delete_package, get_package


class InboundIncomingScopedTargetedTestCase(PackageTest):

    INBOUND_INCOMING_SCOPED_TARGETED_MANIFEST = 'inbound-incoming-scoped-targeted.json'
    TALKER_CLOUD_MANIFEST = 'talker-cloud.json'

    INBOUND_INCOMING_SCOPED_TARGETED_PACKAGE = 'test-inbound-incoming-scoped-targeted-pkg'
    TALKER_CLOUD_PACKAGE = 'test-inbound-incoming-scoped-targeted-talker-cloud-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.INBOUND_INCOMING_SCOPED_TARGETED_MANIFEST,
                    cls.INBOUND_INCOMING_SCOPED_TARGETED_PACKAGE)
        add_package(cls.TALKER_CLOUD_MANIFEST,
                    cls.TALKER_CLOUD_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.INBOUND_INCOMING_SCOPED_TARGETED_PACKAGE)
        delete_package(cls.TALKER_CLOUD_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.talker_deployment = None
        self.listener_deployment = None
        self.routed_network = self.create_cloud_routed_network('cloud_routed_network')

    def tearDown(self):
        self.deprovision_all_deployments([self.talker_deployment, self.listener_deployment])
        self.routed_network.delete()

    def deploy_inbound_incoming_scoped_targeted_listener_package(self):
        package = get_package(self.INBOUND_INCOMING_SCOPED_TARGETED_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_routed_network(self.routed_network)
        self.logger.info('Deploying listener package')
        self.listener_deployment = self.deploy_package(package, provision_config)
        self.listener_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.listener_deployment)

    def test_inbound_incoming_scoped_targeted(self):
        self.deploy_inbound_incoming_scoped_targeted_listener_package()
        package = get_package(self.TALKER_CLOUD_PACKAGE)
        provision_config = package.get_provision_configuration()
        provision_config.add_routed_network(self.routed_network)
        self.logger.info('Deploying talker package')
        self.talker_deployment = self.deploy_package(package, provision_config)
        self.talker_deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.talker_deployment)
