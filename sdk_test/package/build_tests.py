from __future__ import absolute_import
import unittest
from rapyuta_io import Build, BuildStatus, StrategyType, SimulationOptions, CatkinOption, BuildOptions, \
    BuildOperation, BuildOperationInfo, ROSDistro, DeviceArch, Secret, SecretConfigSourceBasicAuth
from rapyuta_io.clients.build import GithubWebhook
from sdk_test.config import Configuration
from sdk_test.util import get_logger
from rapyuta_io.utils.error import ForbiddenError, BuildOperationFailed


class BuildTest(unittest.TestCase):
    build_list = []

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.buildName = 'test-build'
        self.strategyType = StrategyType.SOURCE
        self.rosDistro = ROSDistro.MELODIC
        self.repository = 'https://github.com/rapyuta-robotics/io_tutorials.git'
        self.architecture = DeviceArch.AMD64
        simulation = SimulationOptions(False)
        buildOptions = BuildOptions(catkinOptions=[CatkinOption(rosPkgs='talker')])
        self.build_req = Build(self.buildName, self.strategyType, self.repository, self.architecture, self.rosDistro,
                               isRos=True,
                               contextDir='talk/talker', simulationOptions=simulation, buildOptions=buildOptions)
        self.build = None
        self.branch = 'master'
        self.triggerName = "trigger-name"
        self.tagName = "tag-name"

    def create_build(self, build, refresh=True):
        self.build = self.config.client.create_build(build, refresh)

    def test_01_create_build_success(self):
        self.logger.info('Started creating build')
        self.create_build(self.build_req)
        self.assertEqual(self.build_req.guid, self.build.guid)
        self.assertEqual(self.build.status, BuildStatus.BUILD_IN_PROGRESS)
        self.assertEqual(self.build.buildGeneration, 1)
        self.__class__.build_list.append(self.build)

    def test_02_trigger_and_rollback_and_delete_build_error(self):
        # build created in previous case is likely in progress
        build = self.__class__.build_list[0]
        expected_err_msg = 'build {} is in BuildInProgress state'.format(build.guid)

        req = BuildOperation([BuildOperationInfo(build.guid)])
        trigger_response = self.config.client.trigger_build(req)
        self.assertEqual(trigger_response['buildOperationResponse'][0]['buildGUID'], build.guid)
        self.assertEquals(trigger_response['buildOperationResponse'][0]['error'], expected_err_msg)
        self.assertFalse(trigger_response['buildOperationResponse'][0]['success'])

        rollback_req = BuildOperation([BuildOperationInfo(build.guid, 1)])
        rollback_response = self.config.client.rollback_build(rollback_req)
        self.assertEqual(rollback_response['buildOperationResponse'][0]['buildGUID'], build.guid)
        self.assertEquals(rollback_response['buildOperationResponse'][0]['error'], expected_err_msg)
        self.assertFalse(rollback_response['buildOperationResponse'][0]['success'])

        expected_err_msg = "can't delete build since its corresponding build request is still in progress"
        with self.assertRaises(ForbiddenError) as e:
            self.config.client.delete_build(build.guid)
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_03_poll_build_till_ready(self):
        self.build = self.__class__.build_list[0]
        self.build.poll_build_till_ready()
        self.assertEqual(self.build.status, BuildStatus.COMPLETE)

    def test_04_get_build_success(self):
        guid = self.__class__.build_list[0].guid
        get_build_response_with_query_param = self.config.client.get_build(guid, include_build_requests=True)
        get_build_response_without_query_param = self.config.client.get_build(guid)
        self.assertIn("buildRequests", get_build_response_with_query_param)
        self.assertNotIn("buildRequests", get_build_response_without_query_param)

    def test_05_list_build_success(self):
        guid = self.__class__.build_list[0].guid
        get_complete_builds = self.config.client.list_builds(statuses=[BuildStatus.COMPLETE])
        self.assertIn(guid, [build.guid for build in get_complete_builds])
        get_in_progress_builds = self.config.client.list_builds(statuses=[BuildStatus.BUILD_IN_PROGRESS])
        self.assertNotIn(guid, [build.guid for build in get_in_progress_builds])

    def test_06_delete_build_success(self):
        guid = self.__class__.build_list[0].guid
        self.assertIsNone(self.config.client.delete_build(guid))
        self.__class__.build_list.pop(0)

    def test_07_refresh_success(self):
        self.create_build(self.build_req, False)
        self.assertTrue('buildGeneration' not in self.build)
        self.build.refresh()
        self.assertTrue('buildGeneration' in self.build)
        self.__class__.build_list.append(self.build)

    def test_08_trigger_and_rollback_and_delete_error(self):
        # build created in previous case is likely in progress
        build = self.__class__.build_list[0]
        expected_err_msg = 'build {} is in BuildInProgress state'.format(build.guid)

        with self.assertRaises(BuildOperationFailed) as e:
            build.trigger()
        self.assertEqual(str(e.exception), expected_err_msg)

        with self.assertRaises(BuildOperationFailed) as e:
            build.rollback(1)
        self.assertEqual(str(e.exception), expected_err_msg)

        expected_err_msg = "can't delete build since its corresponding build request is still in progress"
        with self.assertRaises(ForbiddenError) as e:
            build.delete()
        self.assertEqual(str(e.exception), expected_err_msg)
        build.poll_build_till_ready()

    def test_09_trigger_success(self):
        build = self.__class__.build_list[0]
        prev_build_generation_number = build.buildGeneration
        build.trigger()
        build.poll_build_till_ready()
        self.assertEqual(prev_build_generation_number + 1, build.buildGeneration)

    def test_10_rollback_success(self):
        build = self.__class__.build_list[0]
        build_generation_number = 1
        build.rollback(build_generation_number)
        build.poll_build_till_ready()
        self.assertEqual(build_generation_number, build.buildGeneration)

    def test_11_delete_success(self):
        build = self.__class__.build_list[0]
        self.assertIsNone(build.delete())
        self.__class__.build_list.pop(0)

    def test_12_create_build_with_push_pull_secret(self):
        repository = 'ssh://git@bitbucket.org/rapyutians/io_test_scenarios#test/private-docker-pull'
        source_secret = self.config.get_secret('git')
        docker_secret = self.config.get_secret('docker')
        build = Build('test-docker-pull-push-secret', StrategyType.DOCKER, repository, DeviceArch.AMD64,
                      contextDir='flask_helloworld', secret=source_secret.guid, dockerPullSecret=docker_secret.guid,
                      dockerPushSecret=docker_secret.guid, dockerPushRepository='docker.io/rrdockerhub/rapyutapushsecret')
        self.build = self.config.client.create_build(build)
        self.build.poll_build_till_ready()
        self.build.delete()

    def test_13_trigger_build_using_rio_client(self):
        repository = 'ssh://git@bitbucket.org/rapyutians/io_test_scenarios#test/private-docker-pull'
        source_secret = self.config.get_secret('git')
        docker_secret = self.config.get_secret('docker')
        build = Build('test-build-using-rio-client', StrategyType.DOCKER, repository, DeviceArch.AMD64,
                      contextDir='flask_helloworld', secret=source_secret.guid, dockerPullSecret=docker_secret.guid,
                      dockerPushSecret=docker_secret.guid, dockerPushRepository='docker.io/rrdockerhub/rapyutapushsecret',
                      )
        self.build = self.config.client.create_build(build)
        self.build.poll_build_till_ready()
        build_operation_info = BuildOperationInfo(self.build.guid, triggerName="trigger-name", tagName="tag-name")
        build_operation = BuildOperation([build_operation_info])
        self.config.client.trigger_build(build_operation)
        self.build.poll_build_till_ready()
        get_build_response_with_build_requests = self.config.client.get_build(self.build.guid,
                                                                              include_build_requests=True)
        self.assertEqual(get_build_response_with_build_requests.buildRequests[1]['triggerName'], self.triggerName)
        self.assertEqual(get_build_response_with_build_requests.buildRequests[1]['tagName'], self.tagName)
        self.build.delete()

    def test_14_trigger_build_using_self_trigger(self):
        repository = 'ssh://git@bitbucket.org/rapyutians/io_test_scenarios#test/private-docker-pull'
        source_secret = self.config.get_secret('git')
        docker_secret = self.config.get_secret('docker')
        build = Build('test-build-using-self-trigger', StrategyType.DOCKER, repository, DeviceArch.AMD64,
                      contextDir='flask_helloworld', secret=source_secret.guid, dockerPullSecret=docker_secret.guid,
                      dockerPushSecret=docker_secret.guid, dockerPushRepository='docker.io/rrdockerhub/rapyutapushsecret',
                      )
        self.build = self.config.client.create_build(build)
        self.build.poll_build_till_ready()
        self.build.trigger(triggerName="trigger-name", tagName="tag-name")
        self.build.poll_build_till_ready()
        get_build_response_with_build_requests = self.config.client.get_build(self.build.guid,
                                                                              include_build_requests=True)
        self.assertEqual(get_build_response_with_build_requests.buildRequests[1]['triggerName'], self.triggerName)
        self.assertEqual(get_build_response_with_build_requests.buildRequests[1]['tagName'], self.tagName)
        self.build.delete()

    def test_15_update_build_with_success(self):
        self.logger.info('Started creating build')
        simulation = SimulationOptions(False)
        build_options = BuildOptions(catkinOptions=[CatkinOption(rosPkgs='talker')])
        build = Build(self.buildName, self.strategyType, self.repository, self.architecture, self.rosDistro,
                      isRos=True, contextDir='talk/talker', simulationOptions=simulation,
                      buildOptions=build_options)
        self.build = self.config.client.create_build(build)
        self.build.poll_build_till_ready()
        created_build = self.config.client.get_build(self.build.guid)
        self.logger.info('Updating the build')
        created_build.buildInfo.repository = 'https://github.com/rapyuta-robotics'
        created_build.buildInfo.branch = 'test-branch'
        created_build.buildInfo.contextDir = 'test-context-dir'
        created_build.buildInfo.buildOptions = BuildOptions(catkinOptions=[CatkinOption(rosPkgs='listener')])
        created_build.save()
        updated_build = self.config.client.get_build(self.build.guid)
        self.logger.info('asserting the build')
        self.assertEqual(updated_build.buildInfo.repository, 'https://github.com/rapyuta-robotics')
        self.assertEqual(updated_build.buildInfo.branch, 'test-branch')
        self.assertEqual(updated_build.buildInfo.contextDir, 'test-context-dir')
        self.assertEqual(updated_build.buildInfo.buildOptions,
                         {
                             "catkinOptions": [
                                 {
                                     "rosPkgs": "listener",
                                     "cmakeArgs": "",
                                     "makeArgs": "",
                                     "blacklist": "",
                                     "catkinMakeArgs": ""
                                 }
                             ]
                         }
                         )
        self.logger.info('deleting the build')
        self.build.delete()

    def test_16_create_build_with_trigger_name_tag_name(self):
        repository = 'ssh://git@bitbucket.org/rapyutians/io_test_scenarios#test/private-docker-pull'
        source_secret = self.config.get_secret('git')
        docker_secret = self.config.get_secret('docker')
        build = Build('test-docker-pull-push-secret', StrategyType.DOCKER, repository, DeviceArch.AMD64,
                      contextDir='flask_helloworld', secret=source_secret.guid, dockerPullSecret=docker_secret.guid,
                      dockerPushSecret=docker_secret.guid,
                      dockerPushRepository='docker.io/rrdockerhub/rapyutapushsecret', triggerName=self.triggerName,
                      tagName=self.tagName)
        self.build = self.config.client.create_build(build)
        self.build.poll_build_till_ready()
        created_build = self.config.client.get_build(self.build.guid, include_build_requests=True)
        self.logger.info('asserting the build')
        self.assertEqual(created_build.buildRequests[0]['triggerName'], self.triggerName)
        self.assertEqual(created_build.buildRequests[0]['tagName'], self.tagName)
        self.build.delete()

    def test_17_create_build_with_webhook(self):
        repository = 'https://github.com/adityeah8969/demo-flask-app#feature/adding_github_workflow'
        accessToken = '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'
        workflowName = 'dispatch.yaml'
        webhooks = [GithubWebhook(workflowName=workflowName, accessToken=accessToken)]
        build = Build(
                    buildName='test-sdk-build-webhook',
                    strategyType='Docker',
                    repository=repository,
                    architecture='amd64',
                    isRos = False,
                    buildWebhooks=webhooks
        )
        self.build = self.config.client.create_build(build)
        self.build.poll_build_till_ready()
        created_build = self.config.client.get_build(self.build.guid, include_build_requests=True)
        self.logger.info('asserting the build')
        self.assertEqual(created_build.buildRequests[0]['buildWebhooks'][0]['webhookType'] , 'githubWorkflow')
        self.assertEqual(created_build.buildRequests[0]['buildWebhooks'][0]['accessToken'] , accessToken)
        self.assertEqual(created_build.buildRequests[0]['buildWebhooks'][0]['workflowName'] , workflowName)
        self.assertEqual(created_build.buildRequests[0]['buildWebhooks'][0]['repositoryUrl'] , repository)
        self.build.delete()

    def test_17_update_build_with_webhook(self):
        repository = 'https://github.com/adityeah8969/demo-flask-app#feature/adding_github_workflow'
        accessToken = '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'
        workflowName = 'dispatch.yaml'
        webhooks = [GithubWebhook(workflowName=workflowName, accessToken=accessToken)]
        build = Build(
                    buildName='test-sdk-build-webhook',
                    strategyType='Docker',
                    repository=repository,
                    architecture='amd64',
                    isRos=False,
        )
        self.build = self.config.client.create_build(build)
        self.build.poll_build_till_ready()
        created_build = self.config.client.get_build(self.build.guid, include_build_requests=True)
        created_build.buildWebhooks = webhooks
        created_build.save()
        created_build.trigger()
        created_build.poll_build_till_ready()
        build_with_webhook = self.config.client.get_build(self.build.guid, include_build_requests=True)
        self.logger.info('asserting the newly triggered build')
        self.assertEqual(build_with_webhook.buildRequests[1]['buildWebhooks'][0]['webhookType'] , 'githubWorkflow')
        self.assertEqual(build_with_webhook.buildRequests[1]['buildWebhooks'][0]['accessToken'] , accessToken)
        self.assertEqual(build_with_webhook.buildRequests[1]['buildWebhooks'][0]['workflowName'] , workflowName)
        self.assertEqual(build_with_webhook.buildRequests[1]['buildWebhooks'][0]['repositoryUrl'] , repository)
        self.build.delete()
