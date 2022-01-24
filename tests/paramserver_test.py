# encoding: utf-8
from __future__ import absolute_import
import requests
import json
import os

from mock import call, patch, MagicMock
from pyfakefs import fake_filesystem_unittest
from requests import Response

from rapyuta_io.utils.error import BadRequestError, InternalServerError
from tests.utils.client import get_client, headers
from tests.utils.paramserver import UPLOAD_SUCCESS_TREE_PATHS, UPLOAD_SUCCESS_MOCK_CALLS, UPLOAD_FAILURE_400CASE_TREE_PATHS, \
    UPLOAD_FAILURE_400CASE_MOCK_CALLS, DOWNLOAD_TREES_RESPONSE, DOWNLOAD_TREE1_RESPONSE, DOWNLOAD_TREE2_RESPONSE, \
    UPLOAD_FAILURE_500CASE_TREE_PATHS, UPLOAD_FAILURE_500CASE_MOCK_CALLS, UPLOAD_SUCCESS_WITH_TREE_NAMES_MOCK_CALLS, \
    UPLOAD_SUCCESS_DELETE_EXISTING_MOCK_CALLS, GET_BLOB_TREE, BINARY_DATA, BINARY_FILE_NODE, BYTE_ARRAY_DATA
import six


class ParamserverClientTests(fake_filesystem_unittest.TestCase):
    FILE_NODE = 'FileNode'
    VALUE_NODE = 'ValueNode'
    ATTRIBUTE_NODE = 'AttributeNode'

    URL_PREFIX = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/paramserver/tree'

    def setUp(self):
        self.setUpPyfakefs()

    @staticmethod
    def _create_fake_filesystem(rootdir, tree_paths):
        for tree_path, value in six.iteritems(tree_paths):
            path = os.path.join(rootdir, tree_path)
            if value is None:
                os.makedirs(path)
            else:
                with open(path, 'w') as f:
                    f.write(value)

    def _validate_tree_node_on_filesystem(self, node, dir_prefix):
        path = os.path.join(dir_prefix, node['name'])
        self.assertTrue(os.path.exists(path), path + ': does not exist')
        if node['type'] == 'FileNode':
            with open(path, 'r') as f:
                data = node['data']
                if not data:
                    data = BINARY_DATA
                self.assertEqual(data, f.read(), path + ': data mismatch')
        else:
            self.assertTrue(os.path.isdir(path), path + ': not a directory')
            for child in node.get('children', []):
                self._validate_tree_node_on_filesystem(child, path)

    @patch('requests.request')
    def test_upload_configurations_success(self, mock_request):
        rootdir = '/upload/success'
        self._create_fake_filesystem(rootdir, UPLOAD_SUCCESS_TREE_PATHS)
        expected_mock_calls = UPLOAD_SUCCESS_MOCK_CALLS

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = requests.codes.OK
            mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_upload_configurations_success_with_tree_names(self, mock_request):
        rootdir = '/upload/success/with_tree_names'
        self._create_fake_filesystem(rootdir, UPLOAD_SUCCESS_TREE_PATHS)
        expected_mock_calls = UPLOAD_SUCCESS_WITH_TREE_NAMES_MOCK_CALLS

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = requests.codes.OK
            mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir, tree_names=['tree2'])
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_upload_configurations_success_delete_existing(self, mock_request):
        rootdir = '/upload/success/delete_existing'
        self._create_fake_filesystem(rootdir, UPLOAD_SUCCESS_TREE_PATHS)
        expected_mock_calls = UPLOAD_SUCCESS_DELETE_EXISTING_MOCK_CALLS

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = requests.codes.OK
            mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir, delete_existing_trees=True)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_upload_configurations_failure_400case(self, mock_request):
        rootdir = '/upload/failure/400case'
        tree_paths = UPLOAD_FAILURE_400CASE_TREE_PATHS
        self._create_fake_filesystem(rootdir, tree_paths)
        expected_mock_calls = UPLOAD_FAILURE_400CASE_MOCK_CALLS

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            url = kwargs['url']
            url_suffix = url[len(self.URL_PREFIX):]
            if url_suffix == '/tree2/robot_type/AMR/motors.yaml':
                mock_response.status_code = requests.codes.BAD_REQUEST
                mock_response.text = '{"error": "invalid data"}'
            else:
                mock_response.status_code = requests.codes.OK
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        with self.assertRaisesRegex(BadRequestError, 'invalid data') as exc:
            get_client().upload_configurations(rootdir)
        self.assertEqual('tree2/robot_type/AMR/motors.yaml', exc.exception.tree_path)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_upload_configurations_failure_500case(self, mock_request):
        rootdir = '/upload/failure/500case'
        tree_paths = UPLOAD_FAILURE_500CASE_TREE_PATHS
        self._create_fake_filesystem(rootdir, tree_paths)
        expected_mock_calls = UPLOAD_FAILURE_500CASE_MOCK_CALLS

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            url = kwargs['url']
            url_suffix = url[len(self.URL_PREFIX):]
            if url_suffix == '/tree2/robot_type/AGV/robot_name':
                mock_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
                mock_response.text = '{"error": "something went wrong"}'
            else:
                mock_response.status_code = requests.codes.OK
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        with self.assertRaisesRegex(InternalServerError, 'something went wrong') as exc:
            get_client().upload_configurations(rootdir)
        self.assertEqual('tree2/robot_type/AGV/robot_name', exc.exception.tree_path)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_download_configurations_success(self, mock_request):
        rootdir = '/download/success'
        test_signed_url = 'http://test-signedurl'
        expected_mock_calls = [
            call(url=test_signed_url, method='GET', headers={}, params={}, json=None),
            call(url=self.URL_PREFIX + 'blobs', method='GET', headers=headers, params={'treeNames': ['tree1', 'tree2']},
                 json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None),
        ]

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            url = kwargs['url']
            url_suffix = url[len(self.URL_PREFIX):]
            if url == test_signed_url:
                mock_response.status_code = requests.codes.OK
                mock_response.iter_content.side_effect = lambda x: BYTE_ARRAY_DATA
            elif url_suffix == 'blobs':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(GET_BLOB_TREE)
            elif url_suffix == '':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREES_RESPONSE)
            elif url_suffix == '/tree1':
                tree_response = DOWNLOAD_TREE1_RESPONSE.copy()
                mock_response.status_code = requests.codes.OK
                tree_response['data']['children'].append(BINARY_FILE_NODE)
                mock_response.text = json.dumps(tree_response)
            elif url_suffix == '/tree2':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREE2_RESPONSE)
            return mock_response
        mock_request.side_effect = side_effect

        get_client().download_configurations(rootdir)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')
        self._validate_tree_node_on_filesystem(DOWNLOAD_TREE1_RESPONSE['data'], rootdir)
        self._validate_tree_node_on_filesystem(DOWNLOAD_TREE2_RESPONSE['data'], rootdir)

    @patch('requests.request')
    def test_download_configurations_success_with_tree_names(self, mock_request):
        rootdir = '/download/success/with_tree_names'
        test_signed_url = 'http://test-signedurl'
        expected_mock_calls = [
            call(url=test_signed_url, method='GET', headers={}, params={}, json=None),
            call(url=self.URL_PREFIX + 'blobs', method='GET', headers=headers, params={'treeNames': ['tree2']},
                 json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None),
        ]

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            url = kwargs['url']
            url_suffix = url[len(self.URL_PREFIX):]
            if url == test_signed_url:
                mock_response.status_code = requests.codes.OK
                mock_response.iter_content.side_effect = lambda x: BYTE_ARRAY_DATA
            elif url_suffix == 'blobs':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(GET_BLOB_TREE)
            elif url_suffix == '':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREES_RESPONSE)
            elif url_suffix == '/tree2':
                tree_response = DOWNLOAD_TREE2_RESPONSE.copy()
                tree_response['data']['children'].append(BINARY_FILE_NODE)
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(tree_response)
            return mock_response
        mock_request.side_effect = side_effect

        get_client().download_configurations(rootdir, tree_names=['tree2'])
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')
        self.assertFalse(os.path.exists(os.path.join(rootdir, 'tree1')), 'tree1 should not be created')
        self._validate_tree_node_on_filesystem(DOWNLOAD_TREE2_RESPONSE['data'], rootdir)

    @patch('tempfile.mkdtemp')
    @patch('requests.request')
    def test_download_configurations_success_delete_existing(self, mock_request, mock_temp_dir):
        rootdir = '/download/success/delete_existing'
        # create empty dirs under trees to later validate they were deleted
        os.makedirs(os.path.join(rootdir, 'tree1/empty_dir'))
        os.makedirs(os.path.join(rootdir, 'tree2/empty_dir'))
        os.makedirs('/tmp/test_blob_dir')
        test_signed_url = 'http://test-signedurl'
        expected_mock_calls = [
            call(url=test_signed_url, method='GET', headers={}, params={}, json=None),
            call(url=self.URL_PREFIX + 'blobs', method='GET', headers=headers, params={'treeNames': ['tree1', 'tree2']},
                 json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None),
        ]

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            url = kwargs['url']
            url_suffix = url[len(self.URL_PREFIX):]
            if url == test_signed_url:
                mock_response.status_code = requests.codes.OK
                mock_response.iter_content.side_effect = lambda x: BYTE_ARRAY_DATA
            elif url_suffix == '':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREES_RESPONSE)
            elif url_suffix == '/tree1':
                tree_response = DOWNLOAD_TREE1_RESPONSE.copy()
                mock_response.status_code = requests.codes.OK
                tree_response['data']['children'].append(BINARY_FILE_NODE)
                mock_response.text = json.dumps(tree_response)
            elif url_suffix == '/tree2':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREE2_RESPONSE)
            elif url_suffix == 'blobs':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(GET_BLOB_TREE)
            return mock_response
        mock_request.side_effect = side_effect
        mock_temp_dir.return_value = '/tmp/test_blob_dir'

        get_client().download_configurations(rootdir, delete_existing_trees=True)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')
        self._validate_tree_node_on_filesystem(DOWNLOAD_TREE1_RESPONSE['data'], rootdir)
        self._validate_tree_node_on_filesystem(DOWNLOAD_TREE2_RESPONSE['data'], rootdir)
        self.assertFalse(os.path.exists(os.path.join(rootdir, 'tree1/empty_dir')), 'tree1/empty_dir should be deleted')
        self.assertFalse(os.path.exists(os.path.join(rootdir, 'tree2/empty_dir')), 'tree2/empty_dir should be deleted')

    @patch('requests.request')
    def test_download_configurations_failure_tree_list(self, mock_request):
        rootdir = '/download/failure/tree_list'
        expected_mock_calls = [
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
        ]

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
            mock_response.text = '{"error": "something went wrong"}'
            return mock_response
        mock_request.side_effect = side_effect

        with self.assertRaisesRegex(InternalServerError, 'something went wrong') as exc:
            get_client().download_configurations(rootdir)
        self.assertEqual('', exc.exception.tree_path)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('tempfile.mkdtemp')
    @patch('requests.request')
    def test_download_configurations_failure_500case(self, mock_request, mock_temp_dir):
        rootdir = '/download/failure/500case'
        expected_mock_calls = [
            call(url=self.URL_PREFIX + 'blobs', method='GET', headers=headers, params={'treeNames': ['tree1', 'tree2']},
                 json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None),
        ]

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            url = kwargs['url']
            url_suffix = url[len(self.URL_PREFIX):]
            if url_suffix == '':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREES_RESPONSE)
            elif url_suffix == '/tree1':
                mock_response.status_code = requests.codes.INTERNAL_SERVER_ERROR
                mock_response.text = '{"error": "something went wrong"}'
            elif url_suffix == '/tree2':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREE2_RESPONSE)
            elif url_suffix == 'blobs':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps({'data': {'blobRefs': []}})
            return mock_response
        mock_request.side_effect = side_effect
        mock_temp_dir.return_value = '/tmp/test_blob_dir'

        with self.assertRaisesRegex(InternalServerError, 'something went wrong') as exc:
            get_client().download_configurations(rootdir)
        self.assertEqual('tree1', exc.exception.tree_path)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_download_configurations_failure_fileopen(self, mock_request):
        rootdir = '/download/failure/fileopen'
        expected_mock_calls = [
            call(url=self.URL_PREFIX + 'blobs', method='GET', headers=headers, params={'treeNames': ['tree1', 'tree2']},
                 json=None),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None),
        ]
        # simulate failure by creating a directory in place of a file
        os.makedirs(rootdir+'/tree2/motors.yaml')
        expected_exc_regex = "Is a directory in the fake filesystem: '{}/tree2/motors.yaml'".format(rootdir)

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            url = kwargs['url']
            url_suffix = url[len(self.URL_PREFIX):]
            if url_suffix == '':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREES_RESPONSE)
            elif url_suffix == '/tree1':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREE1_RESPONSE)
            elif url_suffix == '/tree2':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps(DOWNLOAD_TREE2_RESPONSE)
            elif url_suffix == 'blobs':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps({'data': {'blobRefs': []}})
            return mock_response
        mock_request.side_effect = side_effect

        with self.assertRaisesRegex(IOError, expected_exc_regex) as exc:
            get_client().download_configurations(rootdir)
        self.assertEqual('tree2', exc.exception.tree_path)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')


