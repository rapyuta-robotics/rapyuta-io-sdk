from __future__ import absolute_import
import requests
import unittest
import json
from mock import patch, Mock, MagicMock, call
from rapyuta_io.clients.build import Build, BuildStatus, SimulationOptions, BuildOptions, CatkinOption, GithubWebhook
from rapyuta_io.clients.buildoperation import BuildOperation, BuildOperationInfo
from tests.utils.client import get_client, remove_auth_token, headers
from rapyuta_io.utils.error import InvalidParameterException, ResourceNotFoundError
from tests.utils.build_responses import BUILD_CREATE_SUCCESS, BUILD_GET_SUCCESS, BUILD_GET_SUCCESS_WITH_BUILD_REQUESTS,\
    BUILD_LIST_SUCCESS, BUILD_NOT_FOUND, TRIGGER_BUILD_RESPONSE, \
    ROLLBACK_BUILD_RESPONSE, BUILD_GUID_NOT_FOUND, BUILD_IN_PROGRESS_ERROR
from requests import Response
from six.moves import map
from rapyuta_io.utils.partials import PartialMixin


class BuildTest(unittest.TestCase):

    def test_create_build_invalid_build_type(self):
        expected_err_msg = 'build must be non-empty and of type rapyuta_io.clients.build.Build'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build('invalid-build-type')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_invalid_strategy_type(self):
        expected_err_msg = 'StrategyType must be one of rapyuta_io.clients.package.StrategyType'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'invalid', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                                      'amd64', 'melodic'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_invalid_ros_distro(self):
        expected_err_msg = 'rosDistro must be one of rapyuta_io.clients.package.ROSDistro'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                                      'amd64', 'invalid', True))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_invalid_architecture(self):
        expected_err_msg = 'Architecture must be one of rapyuta_io.clients.device_manager.DeviceArch'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                                      'invalid', 'melodic'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_build_name_absent(self):
        expected_err_msg = 'buildName must be a non-empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                                      'amd64', 'melodic'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_repository_absent(self):
        expected_err_msg = 'repository must be a valid non-empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', None, 'amd64', 'melodic'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_invalid_simulation_option(self):
        expected_err_msg = 'simulation must be a boolean'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', None, 'amd64', 'melodic', simulationOptions=SimulationOptions(1)))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_invalid_catkin_options(self):
        expected_err_msg = 'catkinOptions must be an instance of list'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', None, 'amd64', rosDistro='melodic', buildOptions=BuildOptions(catkinOptions={})))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_invalid_only_docker_push_secret(self):
        expected_err_msg = 'both dockerPushRepository and dockerPushSecret must be present'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', 'https://github.com/example', 'amd64',
                                      isRos=False, dockerPushSecret='secret-guid'))
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_create_build_invalid_only_docker_push_repository(self):
        expected_err_msg = 'both dockerPushRepository and dockerPushSecret must be present'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', 'https://github.com/example', 'amd64',
                                      isRos=False, dockerPushRepository='docker.io/example/example'))
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_create_build_invalid_trigger_name(self):
        expected_err_msg = 'triggerName must be a non-empty string'
        client = get_client()
        invalid_trigger_name = 1
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', 'https://github.com/example', 'amd64',
                                      isRos=False, dockerPushSecret='secret-guid', triggerName=invalid_trigger_name,
                                      dockerPushRepository='docker.io/example/example'))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_invalid_tag_name(self):
        expected_err_msg = 'tagName must be a non-empty string'
        client = get_client()
        invalid_tag_name = 1
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', 'https://github.com/example', 'amd64',
                                      isRos=False, dockerPushSecret='secret-guid', tagName=invalid_tag_name,
                                      dockerPushRepository='docker.io/example/example'))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_invalid_only_tag_name_with_no_docker_push_secret(self):
        expected_err_msg = 'cannot use tagName without dockerPushSecret'
        client = get_client()
        test_tag_name = 'test_tag_name'
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', 'https://github.com/example', 'amd64',
                                      isRos=False, tagName=test_tag_name))
        self.assertEqual(expected_err_msg, str(e.exception))

    def test_create_build_operation_info_with_invalid_trigger_name(self):
        expected_err_msg = 'triggerName must be a non-empty string'
        inavlid_trigger_name = 1
        with self.assertRaises(InvalidParameterException) as e:
            BuildOperationInfo('build-guid', triggerName=inavlid_trigger_name, tagName='tag-name')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_operation_info_with_invalid_tag_name(self):
        expected_err_msg = 'tagName must be a non-empty string'
        inavlid_tag_name = 1
        with self.assertRaises(InvalidParameterException) as e:
            BuildOperationInfo('build-guid', triggerName='trigger_name', tagName=inavlid_tag_name)

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_build_operation_info_with_invalid_webhook(self):
        expected_err_msg = 'buildWebhooks must be a list of rapyuta_io.clients.build.GithubWebhook'
        inavlid_webhook = 1
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_build(Build('test_build', 'Source', 'https://github.com/example', 'amd64',
                                      isRos=False, dockerPushSecret='secret-guid',
                                      dockerPushRepository='docker.io/example/example',
                                      buildWebhooks = inavlid_webhook))
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_create_build_noetic_success(self, mock_request):
        expected_payload = {
            "buildName": "test_build",
            "strategyType": "Source",
            "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
            "architecture": "amd64",
            "rosDistro": "noetic",
            "isRos": True
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build'
        mock_create_build = Mock()
        mock_create_build.text = BUILD_CREATE_SUCCESS
        mock_create_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_build]
        client = get_client()
        build = client.create_build(
            Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                  'amd64', 'noetic', True), False)
        mock_request.assert_called_once_with(headers=headers,
                                             json=expected_payload,
                                             method='POST',
                                             url=expected_url,
                                             params=None)
        self.assertEqual(build.get('guid'), 'build-guid')
        self.assertEqual(build.get('buildName'), 'test_build')
        self.assertTrue(build.is_partial)

    @patch('requests.request')
    def test_create_build_success(self, mock_request):
        expected_payload = {
            "buildName": "test_build",
            "strategyType": "Source",
            "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
            "architecture": "amd64",
            "rosDistro": "melodic",
            "isRos": True
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build'
        mock_create_build = Mock()
        mock_create_build.text = BUILD_CREATE_SUCCESS
        mock_create_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_build]
        client = get_client()
        build = client.create_build(
            Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                  'amd64', 'melodic', True), False)
        mock_request.assert_called_once_with(headers=headers,
                                             json=expected_payload,
                                             method='POST',
                                             url=expected_url,
                                             params=None)
        self.assertEqual(build.get('guid'), 'build-guid')
        self.assertEqual(build.get('buildName'), 'test_build')
        self.assertTrue(build.is_partial)

    @patch('requests.request')
    def test_create_build_with_push_pull_secrets_success(self, mock_request):
        expected_payload = {
            "buildName": "test_build",
            "strategyType": "Docker",
            "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
            "architecture": "amd64",
            "isRos": False,
            "dockerPullSecrets": ["secret-guid"],
            "dockerPushSecret": "secret-guid",
            "dockerPushRepository": "docker.io/example/example"
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build'
        mock_create_build = Mock()
        mock_create_build.text = BUILD_CREATE_SUCCESS
        mock_create_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_build]
        client = get_client()
        build = client.create_build(
            Build('test_build', 'Docker', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                  'amd64', isRos=False, dockerPushSecret='secret-guid',
                  dockerPushRepository='docker.io/example/example', dockerPullSecret='secret-guid'), False)
        mock_request.assert_called_once_with(headers=headers,
                                             json=expected_payload,
                                             method='POST',
                                             url=expected_url,
                                             params=None)
        self.assertEqual(build.get('guid'), 'build-guid')
        self.assertEqual(build.get('buildName'), 'test_build')

    @patch('requests.request')
    def test_create_build_with_trigger_name_tag_name_success(self, mock_request):
        expected_payload = {
            "buildName": "test_build",
            "strategyType": "Docker",
            "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
            "architecture": "amd64",
            "isRos": False,
            "dockerPullSecrets": ["secret-guid"],
            "dockerPushSecret": "secret-guid",
            "dockerPushRepository": "docker.io/example/example",
            "triggerName": "test-trigger-name",
            "tagName": "test-tag-name"
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build'
        mock_create_build = Mock()
        mock_create_build.text = BUILD_CREATE_SUCCESS
        mock_create_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_build]
        client = get_client()
        build = client.create_build(
            Build('test_build', 'Docker', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                  'amd64', isRos=False, dockerPushSecret='secret-guid',
                  dockerPushRepository='docker.io/example/example', dockerPullSecret='secret-guid',
                  triggerName='test-trigger-name', tagName='test-tag-name'), False)
        mock_request.assert_called_once_with(headers=headers,
                                             json=expected_payload,
                                             method='POST',
                                             url=expected_url,
                                             params=None)
        self.assertEqual(build.get('guid'), 'build-guid')
        self.assertEqual(build.get('buildName'), 'test_build')

    @patch('requests.request')
    def test_create_build_with_refresh_success(self, mock_request):
        expected_payload = {
            "buildName": "test_build",
            "strategyType": "Source",
            "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
            "architecture": "amd64",
            "rosDistro": "melodic",
            "isRos": True
        }
        get_build_response = MagicMock(spec=Response)
        get_build_response.text = BUILD_GET_SUCCESS
        get_build_response.status_code = requests.codes.OK
        mock_create_build = Mock()
        mock_create_build.text = BUILD_CREATE_SUCCESS
        mock_create_build.status_code = requests.codes.OK
        mock_request.side_effect = [get_build_response, mock_create_build]
        client = get_client()
        build = client.create_build(
            Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                  'amd64', 'melodic', True))
        self.assertEqual(mock_request.call_count, 2)
        self.assertEqual(build.get('guid'), 'build-guid')
        self.assertEqual(build.get('buildName'), 'test_build')
        self.assertFalse(build.is_partial)

    @patch('requests.request')
    def test_create_build_with_webhook_success(self, mock_request):
        expected_payload = {
            "buildName": "test_build",
            "strategyType": "Source",
            "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
            "architecture": "amd64",
            "rosDistro": "melodic",
            "isRos": True,
            "buildWebhooks": [
                {
                    "webhookType": "githubWorkflow",
                    "accessToken": "fake_access_token",
                    "workflowName": "fake.yaml"
                }
            ]
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build'
        expected_get_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/build-guid'
        mock_create_build = Mock()
        mock_create_build.text = BUILD_CREATE_SUCCESS
        mock_create_build.status_code = requests.codes.OK
        mock_get_build = Mock()
        mock_get_build.text = BUILD_GET_SUCCESS_WITH_BUILD_REQUESTS
        mock_get_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_build, mock_get_build]
        webhooks = [GithubWebhook(workflowName='fake.yaml', accessToken='fake_access_token')]
        client = get_client()
        created_build = client.create_build(
            Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git',
                  'amd64', 'melodic', True, buildWebhooks=webhooks), False)
        build = client.get_build('build-guid', include_build_requests=True)
        mock_request.assert_has_calls([
            call(headers=headers, json=expected_payload, url=expected_url, method='POST', params=None),
            call(headers=headers, json=None, url=expected_get_url, method='GET', params={'include_build_requests': True}),
        ])
        self.assertEqual(created_build.get('guid'), 'build-guid')
        self.assertEqual(created_build.get('buildName'), 'test_build')
        self.assertEqual(build.buildRequests[0]['buildWebhooks'][0]['webhookType'], 'githubWorkflow')
        self.assertEqual(build.buildRequests[0]['buildWebhooks'][0]['accessToken'], 'fake_access_token')
        self.assertEqual(build.buildRequests[0]['buildWebhooks'][0]['workflowName'], 'fake.yaml')
        self.assertEqual(build.buildRequests[0]['buildWebhooks'][0]['repositoryUrl'], 'https://github.com/rapyuta-robotics/io_tutorials.git')


    @patch('requests.request')
    def test_get_build_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/{}'.format('build-guid')
        mock_get_build = Mock()
        mock_get_build.text = BUILD_GET_SUCCESS
        mock_get_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_build]
        client = get_client()
        build = client.get_build('build-guid')
        remove_auth_token(build)
        delattr(build, 'dockerPullSecret')
        expected_response = json.loads(BUILD_GET_SUCCESS)
        expected_response[PartialMixin.PARTIAL_ATTR] = False
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params=None)
        self.assertEqual(build.get('guid'), 'build-guid')
        self.assertEqual(build.get('buildName'), 'test_build')
        self.assertEqual(build.to_dict(), expected_response)
        self.assertFalse(build.is_partial)

    @patch('requests.request')
    def test_get_build_with_guid_not_found(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/{}'.format('build-guid')
        expected_err_msg = "build guid not found"
        mock_get_build = Mock()
        mock_get_build.text = BUILD_NOT_FOUND
        mock_get_build.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [mock_get_build]
        client = get_client()
        with self.assertRaises(ResourceNotFoundError) as e:
            client.get_build('build-guid')
        self.assertEqual(str(e.exception), expected_err_msg)
        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='GET', params=None)

    @patch('requests.request')
    def test_get_build_with_query_params(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/{}'.format('build-guid')
        expected_query_params = {'include_build_requests': True}
        mock_get_build = Mock()
        mock_get_build.text = BUILD_GET_SUCCESS_WITH_BUILD_REQUESTS
        mock_get_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_build]
        client = get_client()
        build = client.get_build('build-guid', include_build_requests=True)
        remove_auth_token(build)
        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='GET', params=expected_query_params)
        self.assertFalse(build.is_partial)

    @patch('requests.request')
    def test_list_build_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build'

        mock_list_build = Mock()
        mock_list_build.text = BUILD_LIST_SUCCESS
        mock_list_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_build]
        client = get_client()
        builds = client.list_builds()
        list(map(remove_auth_token, builds))
        list(map(lambda build: delattr(build, 'dockerPullSecret'), builds))
        expected_response = json.loads(BUILD_LIST_SUCCESS)
        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='GET', params=None)
        self.assertListEqual(builds, expected_response)
        for build in builds:
            self.assertTrue(build.is_partial)

    @patch('requests.request')
    def test_build_refresh_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build'

        mock_list_build = Mock()
        mock_list_build.text = BUILD_LIST_SUCCESS
        mock_list_build.status_code = requests.codes.OK
        mock_get_build = Mock()
        mock_get_build.text = BUILD_GET_SUCCESS
        mock_get_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_build, mock_get_build]

        client = get_client()
        builds = client.list_builds()
        build = builds[0]
        self.assertTrue(build.is_partial)
        builds[0].refresh()

        self.assertFalse(build.is_partial)
        remove_auth_token(build)
        expected_response = json.loads(BUILD_GET_SUCCESS)
        expected_response[PartialMixin.PARTIAL_ATTR] = False
        expected_response['dockerPullSecret'] = ''
        mock_request.assert_has_calls([
            call(headers=headers, json=None, url=expected_url, method='GET', params=None),
            call(headers=headers, json=None, url=expected_url+'/build-guid', method='GET', params={}),
        ])
        self.assertEqual(build, expected_response)

    @patch('requests.request')
    def test_list_builds_with_query_params_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build'
        expected_query_params = {'status': ['Complete', 'BuildInProgress']}
        mock_list_build = Mock()
        mock_list_build.text = BUILD_LIST_SUCCESS
        mock_list_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_build]
        statuses = [BuildStatus.COMPLETE, BuildStatus.BUILD_IN_PROGRESS]
        client = get_client()
        builds = client.list_builds(statuses=statuses)
        list(map(remove_auth_token, builds))
        list(map(lambda build: delattr(build, 'dockerPullSecret'), builds))
        expected_response = json.loads(BUILD_LIST_SUCCESS)
        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='GET', params=expected_query_params)
        self.assertListEqual(builds, expected_response)
        for build in builds:
            self.assertTrue(build.is_partial)

    def test_list_builds_with_invalid_statuses_type(self):
        expected_err_msg = 'statuses must be an instance of list'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_builds(statuses={})
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_builds_with_invalid_status_value(self):
        expected_err_msg = 'status must be of rapyuta_io.clients.build.BuildStatus'
        client = get_client()
        statuses = ['invalid-status']
        with self.assertRaises(InvalidParameterException) as e:
            client.list_builds(statuses=statuses)
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_update_build_success(self, mock_request):
        expected_payload = {
            "buildName": "test_build",
            "strategyType": "Source",
            "architecture": "amd64",
            "isRos": True,
            "rosDistro": "melodic",
            "repository": "https://github.com/rapyuta-robotics",
            "contextDir": "contextDir",
            "branch": "master",
            "buildOptions": {
                "catkinOptions": [
                    {
                        "rosPkgs": "listener",
                        "cmakeArgs": None,
                        "makeArgs": None,
                        "blacklist": None,
                        "catkinMakeArgs": None
                    }
                ]
            },
            "secret": "test-secret"
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/{}'.format('build-guid')
        build = Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git', 'amd64',
                      'melodic', True)
        setattr(build, '_host', 'https://gacatalog.apps.okd4v2.prod.rapyuta.io')
        setattr(build, 'guid', 'build-guid')
        setattr(build, '_auth_token', 'Bearer test_auth_token')
        setattr(build, '_project', 'test_project')
        mock_update_build = Mock()
        mock_update_build.text = 'null'
        mock_update_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_update_build]
        build.buildInfo.repository = 'https://github.com/rapyuta-robotics'
        build.buildInfo.branch = 'master'
        build.buildInfo.contextDir = 'contextDir'
        build.buildInfo.buildOptions = BuildOptions(catkinOptions=[CatkinOption(rosPkgs='listener')])
        build.secret = 'test-secret'
        build.save()
        mock_request.assert_called_with(headers=headers, json=expected_payload,
                                        url=expected_url, method='PUT', params={})


    @patch('requests.request')
    def test_update_build_invalid_secret(self, mock_request):
        expected_err_msg = 'secret must be a string'
        build = Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git', 'amd64',
                      'melodic', True)
        with self.assertRaises(InvalidParameterException) as e:
            build.secret = 1
            build.save()
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_update_build_invalid_docker_pull_secret(self, mock_request):
        expected_err_msg = 'dockerPullSecret must be a string'
        build = Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git', 'amd64',
                      'melodic', True)
        with self.assertRaises(InvalidParameterException) as e:
            build.dockerPullSecret = 1
            build.save()
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_update_build_invalid_docker_push_repository(self, mock_request):
        expected_err_msg = 'dockerPushRepository must be a string'
        build = Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git', 'amd64',
                      'melodic', True)
        with self.assertRaises(InvalidParameterException) as e:
            build.dockerPushRepository = 1
            build.save()
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_update_build_invalid_repository(self, mock_request):
        expected_err_msg = 'repository must be a valid non-empty string'
        build = Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git', 'amd64',
                      'melodic', True)
        with self.assertRaises(InvalidParameterException) as e:
            build.buildInfo.repository = 1
            build.save()
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_update_build_invalid_branch(self, mock_request):
        expected_err_msg = 'branch must be a valid non-empty string'
        build = Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git', 'amd64',
                      'melodic', True)
        with self.assertRaises(InvalidParameterException) as e:
            build.buildInfo.branch = 1
            build.save()
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_update_build_invalid_docker_file_path_usage_for_source_strategyType(self, mock_request):
        expected_err_msg = 'cannot use dockerFilePath for source strategyType'
        build = Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git', 'amd64',
                      'melodic', True)
        with self.assertRaises(InvalidParameterException) as e:
            build.buildInfo.dockerFilePath = 1
            build.save()
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_update_build_invalid_context_directory(self, mock_request):
        expected_err_msg = 'contextDir must be a string'
        build = Build('test_build', 'Source', 'https://github.com/rapyuta-robotics/io_tutorials.git', 'amd64',
                      'melodic', True)
        with self.assertRaises(InvalidParameterException) as e:
            build.buildInfo.contextDir = 1
            build.save()
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_delete_build_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/{}'.format('build-guid')
        get_build_response = MagicMock(spec=Response)
        get_build_response.text = BUILD_GET_SUCCESS
        get_build_response.status_code = requests.codes.OK
        mock_delete_build = Mock()
        mock_delete_build.text = None
        mock_delete_build.status_code = requests.codes.OK
        mock_request.side_effect = [get_build_response, mock_delete_build]
        client = get_client()
        client.delete_build('build-guid')
        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url, method='DELETE', params=None)

    @patch('requests.request')
    def test_delete_build_build_not_found(self, mock_request):
        expected_err_msg = 'build guid not found'
        get_build_response = MagicMock(spec=Response)
        get_build_response.text = BUILD_GET_SUCCESS
        get_build_response.status_code = requests.codes.OK
        mock_delete_build = Mock()
        mock_delete_build.text = BUILD_NOT_FOUND
        mock_delete_build.status_code = requests.codes.NOT_FOUND
        mock_request.side_effect = [get_build_response, mock_delete_build]
        client = get_client()
        build = client.get_build('build-guid')
        with self.assertRaises(ResourceNotFoundError) as e:
            build.delete()
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_trigger_build_invalid_build_operation_info_type(self):
        expected_err_msg = 'buildOperationInfo must be an instance of list'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.trigger_build(BuildOperation(buildOperationInfo={}))
        self.assertEqual(str(e.exception), expected_err_msg)

    def test_trigger_build_invalid_build_guid(self):
        expected_err_msg = 'buildGuid must be a non-empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            build_op_info = [BuildOperationInfo("")]
            req = BuildOperation(build_op_info)
            client.trigger_build(BuildOperation(req))
        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_trigger_build_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/operation/trigger'
        get_build_response = json.loads(BUILD_GET_SUCCESS)
        mock_trigger_build = Mock()
        mock_trigger_build.text = TRIGGER_BUILD_RESPONSE
        mock_trigger_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_trigger_build]
        trigger_request = BuildOperation([BuildOperationInfo('build-guid')])
        client = get_client()
        trigger_response = client.trigger_build(trigger_request)
        mock_request.assert_called_once_with(headers=headers, json=trigger_request,
                                             url=expected_url, method='PUT', params=None)
        self.assertEqual(get_build_response['buildGeneration'] + 1,
                         trigger_response['buildOperationResponse'][0]['buildGenerationNumber'])

    @patch('requests.request')
    def test_trigger_build_success_with_trigger_name(self, mock_request):
        expected_payload = {
                                "buildOperationInfo": [
                                    {
                                        "buildGUID": "build-guid",
                                        "triggerName": "trigger-name"
                                    }
                                ]
                            }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/operation/trigger'
        get_build_response = json.loads(BUILD_GET_SUCCESS)
        mock_trigger_build = Mock()
        mock_trigger_build.text = TRIGGER_BUILD_RESPONSE
        mock_trigger_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_trigger_build]
        trigger_request = BuildOperation([BuildOperationInfo('build-guid', triggerName='trigger-name')])
        client = get_client()
        trigger_response = client.trigger_build(trigger_request)
        mock_request.assert_called_once_with(headers=headers, json=expected_payload,
                                             url=expected_url, method='PUT', params=None)
        self.assertEqual(get_build_response['buildGeneration'] + 1,
                         trigger_response['buildOperationResponse'][0]['buildGenerationNumber'])

    @patch('requests.request')
    def test_trigger_build_success_with_tag_name(self, mock_request):
        expected_payload = {
            "buildOperationInfo": [
                {
                    "buildGUID": "build-guid",
                    "tagName": "tag-name"
                }
            ]
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/operation/trigger'
        get_build_response = json.loads(BUILD_GET_SUCCESS)
        mock_trigger_build = Mock()
        mock_trigger_build.text = TRIGGER_BUILD_RESPONSE
        mock_trigger_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_trigger_build]
        trigger_request = BuildOperation([BuildOperationInfo('build-guid', tagName='tag-name')])
        client = get_client()
        trigger_response = client.trigger_build(trigger_request)
        mock_request.assert_called_once_with(headers=headers, json=expected_payload,
                                             url=expected_url, method='PUT', params=None)
        self.assertEqual(get_build_response['buildGeneration'] + 1,
                         trigger_response['buildOperationResponse'][0]['buildGenerationNumber'])

    @patch('requests.request')
    def test_trigger_build_build_in_progress_error(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/operation/trigger'
        expected_err_msg = "build is in BuildInProgress state"
        mock_trigger_build = Mock()
        mock_trigger_build.text = BUILD_IN_PROGRESS_ERROR
        mock_trigger_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_trigger_build]
        trigger_request = BuildOperation([BuildOperationInfo('build-guid')])
        client = get_client()
        trigger_response = client.trigger_build(trigger_request)
        mock_request.assert_called_once_with(headers=headers, json=trigger_request,
                                             url=expected_url, method='PUT', params=None)
        self.assertEqual(trigger_response['buildOperationResponse'][0]['error'], expected_err_msg)

    @patch('requests.request')
    def test_trigger_build_guid_not_found(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/operation/trigger'
        expected_err_msg = "build guid not found"
        mock_trigger_build = Mock()
        mock_trigger_build.text = BUILD_GUID_NOT_FOUND
        mock_trigger_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_trigger_build]
        trigger_request = BuildOperation([BuildOperationInfo('build-guid-1')])
        client = get_client()
        trigger_response = client.trigger_build(trigger_request)
        mock_request.assert_called_once_with(headers=headers, json=trigger_request,
                                             url=expected_url, method='PUT', params=None)
        self.assertEqual(trigger_response['buildOperationResponse'][0]['error'], expected_err_msg)

    @patch('requests.request')
    def test_rollback_build_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/operation/rollback'
        get_build_response = json.loads(BUILD_GET_SUCCESS)
        mock_rollback_build = Mock()
        mock_rollback_build.text = ROLLBACK_BUILD_RESPONSE
        mock_rollback_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_rollback_build]
        rollback_request = BuildOperation([BuildOperationInfo('build-guid', 1)])
        client = get_client()
        rollback_response = client.rollback_build(rollback_request)
        mock_request.assert_called_once_with(headers=headers, json=rollback_request,
                                             url=expected_url, method='PUT', params=None)
        self.assertEqual(get_build_response['buildGeneration'],
                         rollback_response['buildOperationResponse'][0]['buildGenerationNumber'])

    @patch('requests.request')
    def test_rollback_build_build_in_progress_error(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/operation/rollback'
        expected_err_msg = "build is in BuildInProgress state"
        mock_rollback_build = Mock()
        mock_rollback_build.text = BUILD_IN_PROGRESS_ERROR
        mock_rollback_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_rollback_build]
        rollback_request = BuildOperation([BuildOperationInfo('build-guid', 1)])
        client = get_client()
        rollback_response = client.rollback_build(rollback_request)
        mock_request.assert_called_once_with(headers=headers, json=rollback_request,
                                             url=expected_url, method='PUT', params=None)
        self.assertEqual(rollback_response['buildOperationResponse'][0]['error'], expected_err_msg)

    @patch('requests.request')
    def test_rollback_build_guid_not_found(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/build/operation/rollback'
        expected_err_msg = "build guid not found"
        mock_rollback_build = Mock()
        mock_rollback_build.text = BUILD_GUID_NOT_FOUND
        mock_rollback_build.status_code = requests.codes.OK
        mock_request.side_effect = [mock_rollback_build]
        rollback_request = BuildOperation([BuildOperationInfo('build-guid-1', 1)])
        client = get_client()
        rollback_response = client.rollback_build(rollback_request)
        mock_request.assert_called_once_with(headers=headers, json=rollback_request,
                                             url=expected_url, method='PUT', params=None)
        self.assertEqual(rollback_response['buildOperationResponse'][0]['error'], expected_err_msg)

    @patch('requests.request')
    def test_rollback_build_invalid_build_gen_number(self, mock_request):
        expected_err_msg = 'build generation number must be an integer and greater than 0'
        get_build_response = MagicMock(spec=Response)
        get_build_response.text = BUILD_GET_SUCCESS
        get_build_response.status_code = requests.codes.OK
        mock_request.side_effect = [get_build_response]
        build = get_client().get_build('build-guid')
        with self.assertRaises(InvalidParameterException) as e:
            build.rollback(-1)
        self.assertEqual(str(e.exception), expected_err_msg)
