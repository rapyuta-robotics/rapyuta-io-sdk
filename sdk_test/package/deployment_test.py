from __future__ import absolute_import

from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, add_package, delete_package, get_package
from rapyuta_io.clients.deployment import DeploymentPhaseConstants
from rapyuta_io.utils.error import BadRequestError

class UpdateDeployment(PackageTest):

    CLOUD_NON_ROS_MANIFEST = 'cloud-non-ros.json'
    CLOUD_NON_ROS_PACKAGE = 'test-cloud-non-ros-package'
    CLOUD_NON_ROS_DEPLOYMENT = 'test-cloud-non-ros-deployment'

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        add_package(self.CLOUD_NON_ROS_MANIFEST,self.CLOUD_NON_ROS_PACKAGE)
        self.cloud_non_ros_pkg = get_package(self.CLOUD_NON_ROS_PACKAGE)
        provision_configuration = self.cloud_non_ros_pkg.get_provision_configuration()
        self.deployment = self.deploy_package(self.cloud_non_ros_pkg, provision_configuration)
        self.deployment.poll_deployment_till_ready()

    def tearDown(self):
        self.deprovision_all_deployments([self.deployment])
        delete_package(self.CLOUD_NON_ROS_PACKAGE)

    def test_update_deployment_provisioning_deployment(self):
        component_context = get_component_context(self.deployment.get("componentInfo", {}))
        payload = {
            "service_id": self.deployment["packageId"],
            "plan_id": self.deployment["planId"],
            "deployment_id": self.deployment["deploymentId"],
            "context": {
                "component_context": component_context
            }
        }
        self.config.client.update_deployment(payload)
        deployment = self.config.client.get_deployment(self.deployment["deploymentId"])
        self.assertEqual(deployment["phase"], DeploymentPhaseConstants.PROVISIONING)

        # tries to update deployment which is in provisioning state
        with self.assertRaises(BadRequestError):
            self.config.client.update_deployment(payload)

    def test_update_deployment_success(self):
        self.logger.info("Started update deployment")
        component_context = get_component_context(self.deployment.get("componentInfo", {}))
        payload = {
            "service_id": self.deployment["packageId"],
            "plan_id": self.deployment["planId"],
            "deployment_id": self.deployment["deploymentId"],
            "context": {
                "component_context": component_context
            }
        }
        self.config.client.update_deployment(payload)
        deployment = self.config.client.get_deployment(self.deployment["deploymentId"])
        self.assertEqual(deployment["phase"], DeploymentPhaseConstants.PROVISIONING)

        deployment.poll_deployment_till_ready()
        deployment = self.config.client.get_deployment(self.deployment["deploymentId"])
        self.assertEqual(deployment["phase"], DeploymentPhaseConstants.SUCCEEDED)

def get_component_context(component_info):
    result = {}
    for component in component_info:
        comp = {}
        executables = []
        executableMetaData = component.get("executableMetaData", []) or []
        for exec in executableMetaData:
            # Component will be considered only if any of its executables is docker or build
            if not (exec.get("docker") or exec.get("buildGUID")):
                continue
            executable = {}
            if exec.get("buildGUID"):
                executable["buildGUID"] = exec["buildGUID"]
            if exec.get("docker"):
                executable["docker"] = exec["docker"]

            executable["id"] = exec.get("id", "")
            executable["name"] = exec.get("name", "")
            executables.append(executable)

        if len(executables) > 0:
            result[component["componentID"]] = comp
            comp["executables"] = executables
            comp["update_deployment"] = True

    return result