# encoding: utf-8
from __future__ import absolute_import
import requests
import json
import os
import shutil
import sys
from concurrent import futures

from mock import call, patch, MagicMock
from pyfakefs import fake_filesystem_unittest
from requests import Response

import rapyuta_io.utils.error
from rapyuta_io.utils.error import BadRequestError, InternalServerError
from tests.utils.client import get_client, headers
from tests.utils.paramserver import UPLOAD_SUCCESS_TREE_PATHS, UPLOAD_SUCCESS_MOCK_CALLS, UPLOAD_FAILURE_400CASE_TREE_PATHS, \
    UPLOAD_FAILURE_400CASE_MOCK_CALLS, DOWNLOAD_TREES_RESPONSE, DOWNLOAD_TREE1_RESPONSE, DOWNLOAD_TREE2_RESPONSE, \
    UPLOAD_FAILURE_500CASE_TREE_PATHS, UPLOAD_FAILURE_500CASE_MOCK_CALLS, UPLOAD_SUCCESS_WITH_TREE_NAMES_MOCK_CALLS, \
    UPLOAD_SUCCESS_DELETE_EXISTING_MOCK_CALLS, GET_BLOB_TREE, BINARY_DATA, BINARY_FILE_NODE, BYTE_ARRAY_DATA,\
    UPLOAD_SUCCESS_FOLDER_MOCK_CALLS, UPLOAD_SUCCESS_WITH_TREE_NAMES_AS_FOLDER_MOCK_CALLS
import six


def _fake_rmtree(path):
    """pyfakefs-compatible rmtree for Python 3.12+.

    Python 3.12 changed shutil.rmtree to use _rmtree_safe_fd which relies
    on os.open(O_PATH) and os.fstat on directory fds — operations that
    pyfakefs does not fully support.  This simple recursive implementation
    uses only the os calls that pyfakefs handles correctly.
    """
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            _fake_rmtree(entry_path)
        else:
            os.remove(entry_path)
    os.rmdir(path)


class _SynchronousExecutor:
    """Drop-in replacement for ThreadPoolExecutor that runs tasks
    synchronously in the calling thread.

    Workaround for a pyfakefs race condition on Python 3.13+:
    ``FakeOsModule.use_original`` is a class-level (non-thread-local) flag.
    The ``use_original_os()`` context-manager used by pyfakefs's linecache
    patcher can temporarily set it to ``True`` in one thread while a
    ThreadPoolExecutor worker is checking the same flag, causing the worker
    to fall through to the real OS and fail.  Running synchronously avoids
    the race entirely while still exercising all paramserver logic.
    """

    def __init__(self, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def submit(self, fn, *args, **kwargs):
        future = futures.Future()
        try:
            result = fn(*args, **kwargs)
            future.set_result(result)
        except BaseException as exc:
            future.set_exception(exc)
        return future


class ParamserverClientTests(fake_filesystem_unittest.TestCase):
    FILE_NODE = 'FileNode'
    VALUE_NODE = 'ValueNode'
    ATTRIBUTE_NODE = 'AttributeNode'
    FOLDER_NODE = 'FolderNode'

    URL_PREFIX = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/paramserver/tree'

    def setUp(self):
        self.setUpPyfakefs()
        # Python 3.13+ exposes a pyfakefs threading race condition
        # (FakeOsModule.use_original is not thread-local). Patch the
        # executor to run synchronously so the fake filesystem is used
        # consistently. See _SynchronousExecutor docstring for details.
        if sys.version_info >= (3, 13):
            patcher = patch(
                'rapyuta_io.clients.paramserver.futures.ThreadPoolExecutor',
                _SynchronousExecutor,
            )
            patcher.start()
            self.addCleanup(patcher.stop)

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
            if 'binaryfilenode' in kwargs.get('url', ''):
                mock_response.text = json.dumps({'data': {}})
            else:
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_upload_configurations_as_folder_success(self, mock_request):
        rootdir = '/upload/success'
        self._create_fake_filesystem(rootdir, UPLOAD_SUCCESS_TREE_PATHS)
        expected_mock_calls = UPLOAD_SUCCESS_FOLDER_MOCK_CALLS

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = requests.codes.OK
            if 'binaryfilenode' in kwargs.get('url', ''):
                mock_response.text = json.dumps({'data': {}})
            else:
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir, as_folder=True)
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
            if 'binaryfilenode' in kwargs.get('url', ''):
                mock_response.text = json.dumps({'data': {}})
            else:
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir, tree_names=['tree2'])
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('requests.request')
    def test_upload_configurations_success_as_folder_with_tree_names(self, mock_request):
        rootdir = '/upload/success/with_tree_names'
        self._create_fake_filesystem(rootdir, UPLOAD_SUCCESS_TREE_PATHS)
        expected_mock_calls = UPLOAD_SUCCESS_WITH_TREE_NAMES_AS_FOLDER_MOCK_CALLS

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = requests.codes.OK
            if 'binaryfilenode' in kwargs.get('url', ''):
                mock_response.text = json.dumps({'data': {}})
            else:
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir, tree_names=['tree2'], as_folder=True)
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
            if 'binaryfilenode' in kwargs.get('url', ''):
                mock_response.text = json.dumps({'data': {}})
            else:
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir, delete_existing_trees=True)
        mock_request.assert_has_calls(expected_mock_calls, any_order=True)
        self.assertEqual(len(expected_mock_calls), mock_request.call_count, 'extra request calls were made')

    @patch('rapyuta_io.clients.paramserver.new_anonymous_azure')
    @patch('requests.request')
    def test_upload_configurations_azure_upload_and_commit(self, mock_request, mock_new_azure):
        """When the binaryfilenode PUT returns blobRefId/uploadUrl the client
        must upload the blob via the Azure SDK and then issue a commit PATCH."""
        rootdir = '/upload/azure_commit'
        self._create_fake_filesystem(rootdir, UPLOAD_SUCCESS_TREE_PATHS)

        blob_ref_id = 'test-blob-123'
        azure_signed_url = 'https://test-azure.blob.core.windows.net/container/blob?sig=test'

        # Mock Azure client
        mock_azure_client = MagicMock()
        mock_new_azure.return_value = mock_azure_client

        # Expected headers for the binary file PUT and commit PATCH
        binary_headers = headers.copy()
        binary_headers.update({
            'X-Rapyuta-Params-Version': "0",
            'Content-Type': 'image/png',
            'Checksum': '5e14cebcc5c5f444e0da2151a49999c0'
        })

        binaryfilenode_base = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/paramserver/binaryfilenode/'

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = requests.codes.OK
            url = kwargs.get('url', '')
            method = kwargs.get('method', '')
            if 'binaryfilenode' in url and method == 'PATCH':
                # commit call
                mock_response.text = json.dumps({'data': {}})
            elif 'binaryfilenode' in url and method == 'PUT':
                # blob reference creation – return blobRefId + uploadUrl
                mock_response.text = json.dumps({
                    'data': {
                        'blobRefId': blob_ref_id,
                        'uploadUrl': azure_signed_url
                    }
                })
            else:
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        get_client().upload_configurations(rootdir)

        # --- Assert the binaryfilenode PUT was issued ---
        mock_request.assert_any_call(
            url=binaryfilenode_base + 'tree2/device.png',
            method='PUT', headers=binary_headers, params={}, data=None,
            timeout=(30, 150)
        )

        # --- Assert the commit PATCH was issued ---
        expected_commit_url = binaryfilenode_base + 'tree2/blobref/' + blob_ref_id
        mock_request.assert_any_call(
            url=expected_commit_url,
            method='PATCH', headers=binary_headers, params={}, json=None,
            timeout=(30, 150)
        )

        # --- Assert Azure SDK was used correctly ---
        mock_new_azure.assert_called_once()
        mock_azure_client.upload.assert_called_once()

        # Verify UploadOptions passed to Azure.upload()
        upload_call_args = mock_azure_client.upload.call_args
        _file_obj = upload_call_args[0][0]  # first positional arg: opened file
        upload_options = upload_call_args[0][1]  # second positional arg: UploadOptions
        self.assertEqual(upload_options.signed_url, azure_signed_url)
        self.assertEqual(upload_options.max_concurrency, 4)
        self.assertIn('x-ms-blob-content-type', upload_options.headers)
        self.assertEqual(upload_options.headers['x-ms-blob-content-type'], 'image/png')
        self.assertIn('x-ms-blob-content-md5', upload_options.headers)

        # Total HTTP calls = non-binary tree calls + binary PUT + commit PATCH
        expected_total = len(UPLOAD_SUCCESS_MOCK_CALLS) + 1  # +1 for the PATCH commit
        self.assertEqual(expected_total, mock_request.call_count,
                         'expected exactly one extra PATCH commit call')

    @patch('rapyuta_io.clients.paramserver.new_anonymous_azure')
    @patch('requests.request')
    def test_upload_binary_azure_upload_failure_raises_upload_error(self, mock_request, mock_new_azure):
        """When the Azure SDK upload raises an exception the client must
        propagate it as an UploadError."""
        rootdir = '/upload/azure_failure'
        self._create_fake_filesystem(rootdir, UPLOAD_SUCCESS_TREE_PATHS)

        blob_ref_id = 'fail-blob-456'
        azure_signed_url = 'https://test-azure.blob.core.windows.net/container/blob?sig=fail'

        mock_azure_client = MagicMock()
        mock_azure_client.upload.side_effect = Exception('connection timed out')
        mock_new_azure.return_value = mock_azure_client

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = requests.codes.OK
            url = kwargs.get('url', '')
            if 'binaryfilenode' in url and kwargs.get('method') == 'PUT':
                mock_response.text = json.dumps({
                    'data': {
                        'blobRefId': blob_ref_id,
                        'uploadUrl': azure_signed_url,
                    }
                })
            else:
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        with self.assertRaises(rapyuta_io.utils.error.UploadError) as ctx:
            get_client().upload_configurations(rootdir)
        self.assertIn('Failed to upload to Azure blob storage', str(ctx.exception))
        mock_azure_client.upload.assert_called_once()

    @patch('rapyuta_io.clients.paramserver.new_anonymous_azure')
    @patch('requests.request')
    def test_upload_binary_commit_blobref_already_uploaded_tolerated(self, mock_request, mock_new_azure):
        """When two concurrent uploads share the same blobRef the second
        commit receives 'blobRef already uploaded'. The client must treat
        this as a successful upload rather than raising."""
        rootdir = '/upload/azure_dup'
        self._create_fake_filesystem(rootdir, UPLOAD_SUCCESS_TREE_PATHS)

        blob_ref_id = 'dup-blob-789'
        azure_signed_url = 'https://test-azure.blob.core.windows.net/container/blob?sig=dup'

        mock_azure_client = MagicMock()
        mock_new_azure.return_value = mock_azure_client

        def side_effect(*args, **kwargs):
            mock_response = MagicMock(spec=Response)
            url = kwargs.get('url', '')
            method = kwargs.get('method', '')
            if 'binaryfilenode' in url and method == 'PATCH':
                # Simulate "blobRef already uploaded" error from commit
                mock_response.status_code = requests.codes.BAD_REQUEST
                mock_response.text = json.dumps({
                    'error': 'blobRef already uploaded'
                })
            elif 'binaryfilenode' in url and method == 'PUT':
                mock_response.status_code = requests.codes.OK
                mock_response.text = json.dumps({
                    'data': {
                        'blobRefId': blob_ref_id,
                        'uploadUrl': azure_signed_url,
                    }
                })
            else:
                mock_response.status_code = requests.codes.OK
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        # Should NOT raise — the "already uploaded" error is tolerated
        get_client().upload_configurations(rootdir)

        mock_azure_client.upload.assert_called_once()
        # Verify the commit PATCH was attempted
        binaryfilenode_base = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/paramserver/binaryfilenode/'
        expected_commit_url = binaryfilenode_base + 'tree2/blobref/' + blob_ref_id
        binary_headers = headers.copy()
        binary_headers.update({
            'X-Rapyuta-Params-Version': "0",
            'Content-Type': 'image/png',
            'Checksum': '5e14cebcc5c5f444e0da2151a49999c0',
        })
        mock_request.assert_any_call(
            url=expected_commit_url,
            method='PATCH', headers=binary_headers, params={}, json=None,
            timeout=(30, 150),
        )

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
            if url_suffix != '/tree2/robot_type/AMR/motors.yaml':
                mock_response.status_code = requests.codes.OK
                mock_response.text = 'null'
            return mock_response
        mock_request.side_effect = side_effect

        with self.assertRaisesRegex(rapyuta_io.utils.error.InvalidYAMLError, 'Invalid YAML') as exc:
            get_client().upload_configurations(rootdir)
        self.assertRegex(str(exc.exception), 'tree2/robot_type/AMR/motors.yaml')
        self.assertNotEqual(len(expected_mock_calls), mock_request.call_count,
                            'expected fewer calls due to client side exception')

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

    @patch('rapyuta_io.clients.paramserver.rmtree', side_effect=_fake_rmtree)
    @patch('tempfile.mkdtemp')
    @patch('requests.request')
    def test_download_configurations_success(self, mock_request, mock_temp_dir, _mock_rmtree):
        rootdir = '/download/success'
        os.makedirs('/tmp/test_blob_dir_success')
        mock_temp_dir.return_value = '/tmp/test_blob_dir_success'
        test_signed_url = 'http://test-signedurl'
        expected_mock_calls = [
            call(url=test_signed_url, method='GET', headers={}, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + 'blobs', method='GET', headers=headers, params={'treeNames': ['tree1', 'tree2']},
                 json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
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

    @patch('rapyuta_io.clients.paramserver.rmtree', side_effect=_fake_rmtree)
    @patch('tempfile.mkdtemp')
    @patch('requests.request')
    def test_download_configurations_success_with_tree_names(self, mock_request, mock_temp_dir, _mock_rmtree):
        rootdir = '/download/success/with_tree_names'
        os.makedirs('/tmp/test_blob_dir_tree_names')
        mock_temp_dir.return_value = '/tmp/test_blob_dir_tree_names'
        test_signed_url = 'http://test-signedurl'
        expected_mock_calls = [
            call(url=test_signed_url, method='GET', headers={}, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + 'blobs', method='GET', headers=headers, params={'treeNames': ['tree2']},
                 json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
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

    @patch('rapyuta_io.clients.paramserver.rmtree', side_effect=_fake_rmtree)
    @patch('tempfile.mkdtemp')
    @patch('requests.request')
    def test_download_configurations_success_delete_existing(self, mock_request, mock_temp_dir, _mock_rmtree):
        rootdir = '/download/success/delete_existing'
        # create empty dirs under trees to later validate they were deleted
        os.makedirs(os.path.join(rootdir, 'tree1/empty_dir'))
        os.makedirs(os.path.join(rootdir, 'tree2/empty_dir'))
        os.makedirs('/tmp/test_blob_dir')
        test_signed_url = 'http://test-signedurl'
        expected_mock_calls = [
            call(url=test_signed_url, method='GET', headers={}, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + 'blobs', method='GET', headers=headers, params={'treeNames': ['tree1', 'tree2']},
                 json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
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
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
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
                 json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
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
                 json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX, method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree1', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
            call(url=self.URL_PREFIX + '/tree2', method='GET', headers=headers, params={}, json=None, timeout=(30, 150)),
        ]
        # simulate failure by creating a directory in place of a file
        os.makedirs(rootdir+'/tree2/motors.yaml')
        expected_exc_regex = r"Is a directory.*{}/tree2/motors\.yaml".format(rootdir)

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


