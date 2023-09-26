from __future__ import absolute_import
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, add_package, delete_package, get_package


class StaticRouteTest(PackageTest):
    STATIC_ROUTE_1 = 'nginx'
    STATIC_ROUTE_2 = 'nginx2'
    ENDPOINT_1 = 'test'
    ENDPOINT_2 = 'test2'

    NGINX_MULTI_COMPONENT_MANIFEST = 'nginx-multi-component.json'
    NGINX_MULTI_COMPONENT_PACKAGE = 'test-static-route-nginx-multi-component-pkg'

    NGINX_SINGLE_COMPONENT_MANIFEST = 'nginx-single-component.json'
    NGINX_SINGLE_COMPONENT_PACKAGE = 'test-static-route-nginx-single-component-pkg'

    @classmethod
    def setUpClass(cls):
        add_package(cls.NGINX_MULTI_COMPONENT_MANIFEST,
                    cls.NGINX_MULTI_COMPONENT_PACKAGE)
        add_package(cls.NGINX_SINGLE_COMPONENT_MANIFEST,
                    cls.NGINX_SINGLE_COMPONENT_PACKAGE)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.NGINX_MULTI_COMPONENT_PACKAGE)
        delete_package(cls.NGINX_SINGLE_COMPONENT_PACKAGE)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.volume_instance = None
        self.deployment = None
        self.static_routes = []
        self.nginx_multi_pkg = get_package(self.NGINX_MULTI_COMPONENT_PACKAGE)
        self.nginx_single_pkg = get_package(self.NGINX_SINGLE_COMPONENT_PACKAGE)

    def tearDown(self):
        self.deprovision_all_deployments([self.deployment])
        self._remove_static_routes()

    def _create_static_routes(self):
        sr1 = self.config.client.create_static_route(self.STATIC_ROUTE_1)
        sr2 = self.config.client.create_static_route(self.STATIC_ROUTE_2)
        # Doing a get again to get the urlString field
        self.static_routes.append(self.config.client.get_static_route(sr1.guid))
        self.static_routes.append(self.config.client.get_static_route(sr2.guid))

    def _remove_static_routes(self):
        self.logger.info("Removing all static routes")
        for route in self.static_routes:
            result = route.delete()
            if not result:
                self.logger.warn("Error while cleaning up static routes {}".format(route))

    def test_deployment_with_multiple_static_routes(self):
        self.logger.info("Started multi component static route deployment")
        provision_configuration = self.nginx_multi_pkg.get_provision_configuration()
        self._create_static_routes()
        provision_configuration.add_static_route(self.STATIC_ROUTE_1, self.ENDPOINT_1, self.static_routes[0])
        provision_configuration.add_static_route(self.STATIC_ROUTE_2, self.ENDPOINT_2, self.static_routes[1])
        self.deployment = self.deploy_package(self.nginx_multi_pkg, provision_configuration)
        self.deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.deployment)
        self.assert_static_route('https://' + str(self.static_routes[0].urlString))
        self.assert_static_route('https://' + str(self.static_routes[1].urlString))

    def test_deployment_with_single_static_routes(self):
        self.logger.info("Started single component static route deployment")
        provision_configuration = self.nginx_single_pkg.get_provision_configuration()
        self._create_static_routes()
        provision_configuration.add_static_route(self.STATIC_ROUTE_1, self.ENDPOINT_1, self.static_routes[0])
        self.deployment = self.deploy_package(self.nginx_single_pkg, provision_configuration)
        self.deployment.poll_deployment_till_ready()
        self.assert_deployment_status(self.deployment)
        self.assert_static_route('https://' + str(self.static_routes[0].urlString))

    def test_get_static_route_by_name_404_case(self):
        self._create_static_routes()
        route = self.config.client.get_static_route_by_name('temp')
        self.assertIsNone(route)

    # TODO(senapati): This test is commented because filter static route
    # API is deprecated in v1 api server.
    # def test_get_static_route_by_name_success(self):
    #     self._create_static_routes()
    #     route = self.config.client.get_static_route_by_name(self.STATIC_ROUTE_1)
    #     route_name = route['urlPrefix'].split('-')[0]
    #     self.assertEqual(route_name, self.STATIC_ROUTE_1)

    def test_delete_static_route_success(self):
        route1 = self.config.client.create_static_route(self.STATIC_ROUTE_1)
        route_guid = route1.guid
        self.config.client.delete_static_route(route_guid)
        route = self.config.client.get_static_route_by_name(self.STATIC_ROUTE_1)
        self.assertIsNone(route)


