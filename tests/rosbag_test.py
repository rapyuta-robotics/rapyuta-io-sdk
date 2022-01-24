from __future__ import absolute_import

import os

import requests
from mock import patch, Mock, call
from pyfakefs import fake_filesystem_unittest

from rapyuta_io.clients.rosbag import ROSBagJob, ROSBagOptions, ROSBagJobStatus, ROSBagBlobStatus, \
    ROSBagCompression, UploadOptions
from rapyuta_io.utils.error import InvalidParameterException, ROSBagBlobError
from tests.utils.client import get_client, headers
from tests.utils.rosbag_responses import ROSBAG_JOB_SUCCESS, ROSBAG_JOB_LIST_SUCCESS, \
    ROSBAG_BLOB_LIST_SUCCESS, ROSBAG_BLOB_LIST_WITH_ERROR_BLOB_SUCCESS, ROSBAG_BLOB_RETRY_SUCCESS, \
    ROSBAG_BLOB_GET_SUCCESS, ROSBAG_BLOB_LIST_WITH_UPLOADING_BLOB_SUCCESS, ROSBAG_BLOB_GET_WITH_UPLOADED_SUCCESS, \
    ROSBAG_BLOB_GET_WITH_ERROR, ROSBAG_BLOB_LIST_WITH_DEVICE_BLOB_SUCCESS


class ROSBagTests(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_create_rosbag_job_invalid_rosbag_job_type(self):
        expected_err_msg = 'rosbag job must be non-empty and of type rapyuta_io.clients.rosbag.ROSBagJob'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_rosbag_job('invalid-rosbag-job-type')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_rosbag_job_options_absent(self):
        expected_err_msg = 'rosbag_options must be a instance of ROSBagOptions'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.create_rosbag_job(ROSBagJob('job_name', None))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_rosbag_job_name_absent(self):
        expected_err_msg = 'name must be a non-empty string'
        client = get_client()
        rosbag_options = ROSBagOptions(all_topics=True)
        with self.assertRaises(InvalidParameterException) as e:
            client.create_rosbag_job(ROSBagJob(None, rosbag_options))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_rosbag_job_deployment_id_absent(self):
        expected_err_msg = 'deployment id must be non empty string'
        client = get_client()
        rosbag_options = ROSBagOptions(all_topics=True)
        with self.assertRaises(InvalidParameterException) as e:
            client.create_rosbag_job(ROSBagJob('name', rosbag_options))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_create_rosbag_job_component_instance_id_absent(self):
        expected_err_msg = 'component instance id must be non empty string'
        client = get_client()
        rosbag_options = ROSBagOptions(all_topics=True)
        with self.assertRaises(InvalidParameterException) as e:
            client.create_rosbag_job(ROSBagJob('name', rosbag_options, deployment_id='dep-id'))

        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_create_rosbag_job_success(self, mock_request):
        expected_payload = {
            'recordOptions': {
                'allTopics': True,
                'topics': ['/teleone', '/teletwo'],
                'compression': ROSBagCompression.BZ2
            },
            'name': 'job_name',
            'componentInstanceID': 'comp-inst-id',
            'deploymentID': 'dep-id'
        }
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs/dep-id'
        mock_create_rosbag_job = Mock()
        mock_create_rosbag_job.text = ROSBAG_JOB_SUCCESS
        mock_create_rosbag_job.status_code = requests.codes.OK
        mock_request.side_effect = [mock_create_rosbag_job]
        client = get_client()
        rosbag_options = ROSBagOptions(all_topics=True, topics=['/teleone', '/teletwo'],
                                       compression=ROSBagCompression.BZ2)
        rosbag_job = ROSBagJob('job_name', rosbag_options,
                               deployment_id='dep-id', component_instance_id='comp-inst-id')
        job = client.create_rosbag_job(rosbag_job)
        mock_request.assert_called_once_with(headers=headers,
                                             json=expected_payload,
                                             url=expected_url,
                                             method='POST',
                                             params=None)
        self.assertEqual(job.guid, 'job-guid')
        self.assertEqual(job.name, 'job_name')

    def test_rosbag_options_invalid_all_topics(self):
        expected_err_msg = 'all_topics must be a bool'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(all_topics='invalid')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_topics_not_list(self):
        expected_err_msg = 'topics must be a list of string'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(topics='invalid')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_topics(self):
        expected_err_msg = 'topics must be a list of string'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(topics=[1, 2])

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_include_regex_not_list(self):
        expected_err_msg = 'topic_include_regex must be a list of string'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(topic_include_regex='invalid')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_include_regex(self):
        expected_err_msg = 'topic_include_regex must be a list of string'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(topic_include_regex=[1, 2])

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_exclude_regex(self):
        expected_err_msg = 'topic_exclude_regex must be a non-empty string'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(topic_exclude_regex=1)

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_node_option(self):
        expected_err_msg = 'node must be a non-empty string'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(node=1)

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_compression_option(self):
        expected_err_msg = 'compression must be a LZ4 or BZ2'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(compression='invalid')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_max_splits_option(self):
        expected_err_msg = 'max_splits must be a int'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions(max_splits='invalid')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_rosbag_options_invalid_max_splits_option(self):
        expected_err_msg = 'One of all_topics, topics, topic_include_regex, and node must be provided'
        with self.assertRaises(InvalidParameterException) as e:
            ROSBagOptions()

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_upload_options_non_positive_max_upload_rate(self):
        expected_err_msg = 'max_upload_rate must be a positive int'
        with self.assertRaises(InvalidParameterException) as e:
            UploadOptions(max_upload_rate=0)

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_upload_options_invalid_max_upload_rate(self):
        expected_err_msg = 'max_upload_rate must be a positive int'
        with self.assertRaises(InvalidParameterException) as e:
            UploadOptions(max_upload_rate='invalid')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_upload_options_invalid_purge_after(self):
        expected_err_msg = 'purge_after must be a bool'
        with self.assertRaises(InvalidParameterException) as e:
            UploadOptions(purge_after='invalid')

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_rosbag_jobs_invalid_deployment_id(self):
        expected_err = 'deployment id be non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_jobs(1)
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_jobs_invalid_component_instance_id(self):
        expected_err = 'component_instance_ids needs to be a list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_jobs('dep-id', component_instance_ids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_jobs_invalid_job_ids(self):
        expected_err = 'guids needs to be a list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_jobs('dep-id', guids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_jobs_invalid_status(self):
        expected_err = 'status needs to be a list of ROSBagJobStatus'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_jobs('dep-id', statuses=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_jobs_both_query_params_present(self):
        expected_err = 'only guid or component_instance_id should be present'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_jobs('dep-id', guids=['job-id'],
                                    component_instance_ids=['comp-inst-id'])
        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_list_rosbag_jobs_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs/dep-id'
        mock_list_rosbag_request = Mock()
        mock_list_rosbag_request.text = ROSBAG_JOB_LIST_SUCCESS
        mock_list_rosbag_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_request]
        client = get_client()
        rosbag_jobs = client.list_rosbag_jobs('dep-id')
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params={})
        self.assertEqual(rosbag_jobs[0].guid, 'job-guid')

    @patch('requests.request')
    def test_list_rosbag_jobs_success_with_component_instance_id(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs/dep-id'
        mock_list_rosbag_request = Mock()
        mock_list_rosbag_request.text = ROSBAG_JOB_LIST_SUCCESS
        mock_list_rosbag_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_request]
        client = get_client()
        rosbag_jobs = client.list_rosbag_jobs('dep-id',
                                              component_instance_ids=['comp-inst-id'])
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params={'componentInstanceID': ['comp-inst-id']})
        self.assertEqual(rosbag_jobs[0].guid, 'job-guid')

    @patch('requests.request')
    def test_list_rosbag_jobs_success_with_job_id(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs/dep-id'
        mock_list_rosbag_request = Mock()
        mock_list_rosbag_request.text = ROSBAG_JOB_LIST_SUCCESS
        mock_list_rosbag_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_request]
        client = get_client()
        rosbag_jobs = client.list_rosbag_jobs('dep-id',
                                              guids=['job-id'])
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params={'guid': ['job-id']})
        self.assertEqual(rosbag_jobs[0].guid, 'job-guid')

    @patch('requests.request')
    def test_list_rosbag_jobs_success_with_status(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs/dep-id'
        mock_list_rosbag_request = Mock()
        mock_list_rosbag_request.text = ROSBAG_JOB_LIST_SUCCESS
        mock_list_rosbag_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_request]
        client = get_client()
        rosbag_jobs = client.list_rosbag_jobs('dep-id',
                                              statuses=[ROSBagJobStatus.RUNNING])
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params={'status': ['Running']})
        self.assertEqual(rosbag_jobs[0].guid, 'job-guid')

    def test_list_rosbag_jobs_in_project_invalid_device_ids(self):
        expected_err = 'device_ids need to be a non-empty list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_jobs_in_project(device_ids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_jobs_in_project_empty_device_ids_list(self):
        expected_err = 'device_ids need to be a non-empty list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_jobs_in_project(device_ids=[])
        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_list_rosbag_jobs_in_project_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs'
        mock_list_rosbag_request = Mock()
        mock_list_rosbag_request.text = ROSBAG_JOB_LIST_SUCCESS
        mock_list_rosbag_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_request]
        client = get_client()
        rosbag_jobs = client.list_rosbag_jobs_in_project(device_ids=['device-id'])
        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params={'deviceID': ['device-id']})
        self.assertEqual(rosbag_jobs[0].guid, 'job-guid')

    def test_stop_rosbag_jobs_invalid_component_instance_ids(self):
        expected_err = 'component_instance_ids needs to be a list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.stop_rosbag_jobs('dep-id', component_instance_ids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_stop_rosbag_jobs_invalid_guids(self):
        expected_err = 'guids needs to list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.stop_rosbag_jobs('dep-id', guids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_stop_rosbag_jobs_both_query_params_present(self):
        expected_err = 'only guid or component_instance_id should be present'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.stop_rosbag_jobs('dep-id', guids=['job-id'],
                                    component_instance_ids=['comp-inst-id'])
        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_stop_rosbag_jobs_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs/dep-id'
        mock_stop_rosbag_job_request = Mock()
        mock_stop_rosbag_job_request.text = 'null'
        mock_stop_rosbag_job_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_stop_rosbag_job_request]
        client = get_client()
        client.stop_rosbag_jobs('dep-id')
        mock_request.assert_called_once_with(headers=headers,
                                             method='PATCH',
                                             url=expected_url,
                                             json=None,
                                             params={})

    @patch('requests.request')
    def test_stop_rosbag_jobs_success_with_component_instance_ids(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs/dep-id'
        mock_stop_rosbag_job_request = Mock()
        mock_stop_rosbag_job_request.text = 'null'
        mock_stop_rosbag_job_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_stop_rosbag_job_request]
        client = get_client()
        client.stop_rosbag_jobs('dep-id', component_instance_ids=['comp-inst-id'])
        mock_request.assert_called_once_with(headers=headers,
                                             method='PATCH',
                                             url=expected_url,
                                             json=None,
                                             params={'componentInstanceID': ['comp-inst-id']})

    @patch('requests.request')
    def test_stop_rosbag_jobs_success_with_guids(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-jobs/dep-id'
        mock_stop_rosbag_job_request = Mock()
        mock_stop_rosbag_job_request.text = 'null'
        mock_stop_rosbag_job_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_stop_rosbag_job_request]
        client = get_client()
        client.stop_rosbag_jobs('dep-id', guids=['job-id'])
        mock_request.assert_called_once_with(headers=headers,
                                             method='PATCH',
                                             url=expected_url,
                                             json=None,
                                             params={'guid': ['job-id']})

    def test_list_rosbag_blobs_invalid_deployment_ids(self):
        expected_err = 'deployment_ids needs to be a list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_blobs(deployment_ids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_blobs_invalid_component_instance_ids(self):
        expected_err = 'component_instance_ids needs to be a list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_blobs(component_instance_ids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_blobs_invalid_guids(self):
        expected_err = 'guids needs to be a list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_blobs(guids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_blobs_invalid_status(self):
        expected_err = 'status needs to be a list of ROSBagBlobStatus'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_blobs(statuses=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_blobs_invalid_job_ids(self):
        expected_err = 'job_ids needs to be a list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_blobs(job_ids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_blobs_invalid_device_ids(self):
        expected_err = 'device_ids need to be a list of string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_blobs(device_ids=[1])
        self.assertEqual(str(e.exception), expected_err)

    def test_list_rosbag_blobs_multiple_query_param(self):
        expected_err = 'only one of deployment_ids, component_instance_ids, guids or job_ids should be present'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.list_rosbag_blobs(job_ids=['job-id'], guids=['blob-id'])
        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_list_rosbag_blobs_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs'
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request]
        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs(guids=['blob-id'])
        mock_request.assert_called_once_with(headers=headers, method='GET',
                                             url=expected_url,
                                             json=None,
                                             params={'guid': ['blob-id']})
        self.assertEqual(rosbag_blobs[0].guid, 'blob-id')
        self.assertEqual(rosbag_blobs[0].job.guid, 'job-id')

    @patch('requests.request')
    def test_list_rosbag_blobs_success_with_deployment_ids(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs'
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request]
        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs(deployment_ids=['dep-id'])
        mock_request.assert_called_once_with(headers=headers, method='GET',
                                             url=expected_url,
                                             json=None,
                                             params={'deploymentID': ['dep-id']})
        self.assertEqual(rosbag_blobs[0].guid, 'blob-id')
        self.assertEqual(rosbag_blobs[0].job.guid, 'job-id')

    @patch('requests.request')
    def test_list_rosbag_blobs_success_with_job_ids(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs'
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request]
        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs(job_ids=['job-id'])
        mock_request.assert_called_once_with(headers=headers, method='GET',
                                             url=expected_url,
                                             json=None,
                                             params={'jobID': ['job-id']})
        self.assertEqual(rosbag_blobs[0].guid, 'blob-id')
        self.assertEqual(rosbag_blobs[0].job.guid, 'job-id')

    @patch('requests.request')
    def test_list_rosbag_blobs_success_with_status(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs'
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request]
        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs(statuses=[ROSBagBlobStatus.UPLOADED])
        mock_request.assert_called_once_with(headers=headers, method='GET',
                                             url=expected_url,
                                             json=None,
                                             params={'status': ['Uploaded']})
        self.assertEqual(rosbag_blobs[0].guid, 'blob-id')
        self.assertEqual(rosbag_blobs[0].job.guid, 'job-id')

    @patch('requests.request')
    def test_list_rosbag_blobs_success_with_component_instance_ids(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs'
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request]
        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs(component_instance_ids=['comp-inst-id'])
        mock_request.assert_called_once_with(headers=headers, method='GET',
                                             url=expected_url,
                                             json=None,
                                             params={'componentInstanceID': ['comp-inst-id']})
        self.assertEqual(rosbag_blobs[0].guid, 'blob-id')
        self.assertEqual(rosbag_blobs[0].job.guid, 'job-id')

    @patch('requests.request')
    def test_list_rosbag_blobs_success_with_device_ids(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs'
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request]
        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs(device_ids=['device-id'])
        mock_request.assert_called_once_with(headers=headers, method='GET',
                                             url=expected_url,
                                             json=None,
                                             params={'deviceID': ['device-id']})
        self.assertEqual(rosbag_blobs[0].guid, 'blob-id')
        self.assertEqual(rosbag_blobs[0].job.guid, 'job-id')

    def test_delete_rosbag_jobs_empty_blob_id(self):
        expected_err = 'guid needs to non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.delete_rosbag_blob('')
        self.assertEqual(str(e.exception), expected_err)

    def test_delete_rosbag_jobs_invalid_blob_id(self):
        expected_err = 'guid needs to non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.delete_rosbag_blob(1)
        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_delete_rosbag_jobs_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id'
        mock_delete_rosbag_blob_request = Mock()
        mock_delete_rosbag_blob_request.text = 'null'
        mock_delete_rosbag_blob_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_delete_rosbag_blob_request]
        client = get_client()
        client.delete_rosbag_blob('blob-id')
        mock_request.assert_called_once_with(headers=headers,
                                             url=expected_url,
                                             json=None, params=None,
                                             method='DELETE')

    @patch('requests.request')
    def test_delete_rosbag_blob_with_object_success(self, mock_request):
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_delete_rosbag_blob_request = Mock()
        mock_delete_rosbag_blob_request.text = 'null'
        mock_delete_rosbag_blob_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request, mock_delete_rosbag_blob_request]
        client = get_client()
        rosbag_blob = client.list_rosbag_blobs(guids=['blob-id'])[0]
        blob_id = rosbag_blob.guid
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/{}'.format(blob_id)
        rosbag_blob.delete()
        mock_request.assert_called_with(headers=headers,
                                        url=expected_url,
                                        json=None, params={},
                                        method='DELETE')

    def test_download_rosbag_jobs_empty_blob_id(self):
        expected_err = 'guid needs to non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.download_rosbag_blob('')
        self.assertEqual(str(e.exception), expected_err)

    def test_download_rosbag_jobs_invalid_blob_id(self):
        expected_err = 'guid needs to non empty string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.download_rosbag_blob(1)
        self.assertEqual(str(e.exception), expected_err)

    @patch('requests.request')
    def test_download_rosbag_blobs_success(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id/file'
        signed_url = "http://signed-url"
        blob_filename = "blob_filename.bag"
        mock_download_rosbag_blob_request = Mock()
        mock_download_rosbag_blob_request.text = '{"url":"%s"}' % signed_url
        mock_download_rosbag_blob_request.status_code = requests.codes.OK
        mock_download_file_request = Mock()
        mock_download_file_request.headers = {'Content-Disposition': 'attachment;filename=%s' % blob_filename}
        mock_download_file_request.iter_content.side_effect = lambda x: [b'd', b'a', b't', b'a']
        mock_download_file_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_download_rosbag_blob_request, mock_download_file_request]
        client = get_client()
        client.download_rosbag_blob('blob-id')
        mock_request.assert_has_calls([
            call(headers=headers, json=None, params=None, method='GET', url=expected_url),
            call(headers={}, json=None, params={}, method='GET', url=signed_url)
        ])
        self.assertTrue(os.path.exists(blob_filename))

    @patch('requests.request')
    def test_download_rosbag_blobs_success_with_dir(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id/file'
        signed_url = "http://signed-url"
        blob_filename = "blob_filename.bag"
        download_dir = "/some/random/path/"
        os.makedirs(download_dir)
        mock_download_rosbag_blob_request = Mock()
        mock_download_rosbag_blob_request.text = '{"url":"%s"}' % signed_url
        mock_download_rosbag_blob_request.status_code = requests.codes.OK
        mock_download_file_request = Mock()
        mock_download_file_request.headers = {'Content-Disposition': 'attachment;filename=%s' % blob_filename}
        mock_download_file_request.iter_content.side_effect = lambda x: [b'd', b'a', b't', b'a']
        mock_download_file_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_download_rosbag_blob_request, mock_download_file_request]
        client = get_client()
        client.download_rosbag_blob('blob-id', download_dir='/some/random/path/')
        mock_request.assert_has_calls([
            call(headers=headers, json=None, params=None, method='GET', url=expected_url),
            call(headers={}, json=None, params={}, method='GET', url=signed_url)
        ])
        self.assertTrue(os.path.exists(os.path.join(download_dir, blob_filename)))

    @patch('requests.request')
    def test_download_rosbag_blobs_success_with_filename(self, mock_request):
        expected_url = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id/file'
        signed_url = "http://signed-url"
        blob_filename = "filename.bag"
        mock_download_rosbag_blob_request = Mock()
        mock_download_rosbag_blob_request.text = '{"url":"%s"}' % signed_url
        mock_download_rosbag_blob_request.status_code = requests.codes.OK
        mock_download_file_request = Mock()
        mock_download_file_request.headers = {'Content-Disposition': 'attachment;filename=random_name.bag'}
        mock_download_file_request.iter_content.side_effect = lambda x: [b'd', b'a', b't', b'a']
        mock_download_file_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_download_rosbag_blob_request, mock_download_file_request]
        client = get_client()
        client.download_rosbag_blob('blob-id', filename=blob_filename)
        mock_request.assert_has_calls([
            call(headers=headers, json=None, params=None, method='GET', url=expected_url),
            call(headers={}, json=None, params={}, method='GET', url=signed_url)
        ])
        self.assertTrue(os.path.exists(blob_filename))

    @patch('requests.request')
    def test_rosbag_blob_retry_upload_cloud_error(self, mock_request):
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request]

        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs()
        with self.assertRaisesRegex(InvalidParameterException, 'retry_upload not supported for Cloud ROSBagBlobs'):
            rosbag_blobs[0].retry_upload()

        mock_request.assert_has_calls([
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs', json=None,
                 params={}),
        ])
        self.assertEqual(1, mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_rosbag_blob_retry_upload_non_error_status_error(self, mock_request):
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_WITH_DEVICE_BLOB_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request]

        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs()
        with self.assertRaisesRegex(InvalidParameterException, 'ROSBagBlob does not have Error status'):
            rosbag_blobs[0].retry_upload()

        mock_request.assert_has_calls([
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs', json=None,
                 params={}),
        ])
        self.assertEqual(1, mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_rosbag_blob_retry_upload_success(self, mock_request):
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_WITH_ERROR_BLOB_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_retry_call = Mock()
        mock_retry_call.text = ROSBAG_BLOB_RETRY_SUCCESS
        mock_retry_call.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request, mock_retry_call]

        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs()
        rosbag_blobs[0].retry_upload()

        mock_request.assert_has_calls([
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs', json=None,
                 params={}),
            call(headers=headers, method='POST', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id/retry',
                 json=None, params={}),
        ])
        self.assertEqual(2, mock_request.call_count, 'extra request calls were made')
        self.assertEqual(rosbag_blobs[0].status, ROSBagBlobStatus.STARTING)

    @patch('requests.request')
    def test_rosbag_blob_refresh_success(self, mock_request):
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_WITH_ERROR_BLOB_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_refresh_call = Mock()
        mock_refresh_call.text = ROSBAG_BLOB_GET_SUCCESS
        mock_refresh_call.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request, mock_refresh_call]

        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs()
        rosbag_blobs[0].refresh()

        mock_request.assert_has_calls([
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs', json=None,
                 params={}),
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id',
                 json=None, params={}),
        ])
        self.assertEqual(2, mock_request.call_count, 'extra request calls were made')
        self.assertEqual(rosbag_blobs[0].status, ROSBagBlobStatus.UPLOADING)

    @patch('time.sleep')
    @patch('requests.request')
    def test_rosbag_blob_poll_blob_till_ready_success(self, mock_request, mock_sleep):
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_WITH_UPLOADING_BLOB_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_refresh_call = Mock()
        mock_refresh_call.text = ROSBAG_BLOB_GET_SUCCESS
        mock_refresh_call.status_code = requests.codes.OK
        mock_refresh_call2 = Mock()
        mock_refresh_call2.text = ROSBAG_BLOB_GET_WITH_UPLOADED_SUCCESS
        mock_refresh_call2.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request, mock_refresh_call, mock_refresh_call2]

        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs()
        rosbag_blobs[0].poll_till_ready()

        mock_request.assert_has_calls([
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs', json=None,
                 params={}),
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id',
                 json=None, params={}),
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id',
                 json=None, params={}),
        ])
        self.assertEqual(3, mock_request.call_count, 'extra request calls were made')
        mock_sleep.assert_called_once_with(5)
        self.assertEqual(rosbag_blobs[0].status, ROSBagBlobStatus.UPLOADED)

    @patch('time.sleep')
    @patch('requests.request')
    def test_rosbag_blob_poll_blob_till_ready_error(self, mock_request, mock_sleep):
        mock_list_rosbag_blobs_request = Mock()
        mock_list_rosbag_blobs_request.text = ROSBAG_BLOB_LIST_WITH_UPLOADING_BLOB_SUCCESS
        mock_list_rosbag_blobs_request.status_code = requests.codes.OK
        mock_refresh_call = Mock()
        mock_refresh_call.text = ROSBAG_BLOB_GET_SUCCESS
        mock_refresh_call.status_code = requests.codes.OK
        mock_refresh_call2 = Mock()
        mock_refresh_call2.text = ROSBAG_BLOB_GET_WITH_ERROR
        mock_refresh_call2.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_rosbag_blobs_request, mock_refresh_call, mock_refresh_call2]

        client = get_client()
        rosbag_blobs = client.list_rosbag_blobs()
        with self.assertRaisesRegex(ROSBagBlobError, 'device offline'):
            rosbag_blobs[0].poll_till_ready()

        mock_request.assert_has_calls([
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs', json=None,
                 params={}),
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id',
                 json=None, params={}),
            call(headers=headers, method='GET', url='https://gacatalog.apps.okd4v2.prod.rapyuta.io/rosbag-blobs/blob-id',
                 json=None, params={}),
        ])
        self.assertEqual(3, mock_request.call_count, 'extra request calls were made')
        mock_sleep.assert_called_once_with(5)
        self.assertEqual(rosbag_blobs[0].status, ROSBagBlobStatus.ERROR)
