from __future__ import absolute_import
from collections import OrderedDict

from mock import call, ANY

from tests.utils.client import headers
import six

_URL_PREFIX = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/paramserver/'


def _get_mock_calls(tree_paths, ignore_tree_paths=None, delete_existing_trees=False):
    """
    Creates request mock calls from tree paths.

    ignore_tree_paths is a list of tree paths to not create mock call for.
    """
    mock_calls = []
    for tree_path, value in six.iteritems(tree_paths):
        if ignore_tree_paths and tree_path in ignore_tree_paths:
            continue
        api_prefix = 'tree'
        content_type = 'text/yaml'
        if value and '.yaml' not in tree_path:
            _add_mock_binary_file_mock_call(mock_calls, tree_path)
            continue
        url = _URL_PREFIX + api_prefix + '/' + tree_path
        slash_count = tree_path.count('/')
        if delete_existing_trees and slash_count == 0:
            mock_calls.append(call(url=url, method='DELETE', headers=headers, params={}, json=None))

        if value is None:
            if slash_count % 2 == 0:
                json = {'type': 'ValueNode'}
            else:
                json = {'type': 'AttributeNode'}
        else:
            json = {'type': 'FileNode', 'data': value, 'contentType': content_type}
        mock_calls.append(call(url=url, method='PUT', headers=headers, params={}, json=json))
    return mock_calls

def _get_folder_mock_calls(tree_paths, ignore_tree_paths=None, delete_existing_trees=False):
    """
    Creates request mock calls from tree paths.

    ignore_tree_paths is a list of tree paths to not create mock call for.
    """
    mock_calls = []
    for tree_path, value in six.iteritems(tree_paths):
        if ignore_tree_paths and tree_path in ignore_tree_paths:
            continue
        api_prefix = 'tree'
        content_type = 'text/yaml'
        if value and '.yaml' not in tree_path:
            _add_mock_binary_file_mock_call(mock_calls, tree_path)
            continue
        url = _URL_PREFIX + api_prefix + '/' + tree_path
        slash_count = tree_path.count('/')
        if delete_existing_trees and slash_count == 0:
            mock_calls.append(call(url=url, method='DELETE', headers=headers, params={}, json=None))

        if value is None:
            if slash_count == 0:
                json = {'type': 'ValueNode'}
            else:
                json = {'type': 'FolderNode'}
        else:
            json = {'type': 'FileNode', 'data': value, 'contentType': content_type}
        mock_calls.append(call(url=url, method='PUT', headers=headers, params={}, json=json))
    return mock_calls


def _add_mock_binary_file_mock_call(mock_calls, tree_path):
    headers_copy = headers.copy()
    content_type = 'image/png'
    api_prefix = 'filenode'
    url = _URL_PREFIX + api_prefix + '/' + tree_path
    headers_copy.update({'X-Rapyuta-Params-Version': "0",
                         'Content-Type': content_type,
                         'Checksum': '5e14cebcc5c5f444e0da2151a49999c0'})

    mock_calls.append(call(url=url, method='PUT', headers=headers_copy, params={}, data=ANY))


BINARY_DATA = 'binary-data'
BYTE_ARRAY_DATA = [b'b', b'i', b'n', b'a', b'r', b'y', b'-', b'd', b'a', b't', b'a']

UPLOAD_SUCCESS_TREE_PATHS = OrderedDict([
    ('tree1', None),
    ('tree1/config.yaml', 'a: b'),
    ('tree1/attr', None),
    ('tree2', None),
    ('tree2/device.yaml', 'a: b'),
    ('tree2/motors.yaml', 'a: b'),
    ('tree2/device.png', BINARY_DATA),
    ('tree2/robot_type', None),
    ('tree2/robot_type/AGV', None),
    ('tree2/robot_type/AGV/motors.yaml', 'a: b'),
    ('tree2/robot_type/AGV/robot_name', None),
    ('tree2/robot_type/AGV/robot_name/robot1', None),
    ('tree2/robot_type/AGV/robot_name/robot1/device.yaml', 'a: b'),
    ('tree2/robot_type/AGV/robot_name/robot2', None),
    ('tree2/robot_type/AMR', None),
])

UPLOAD_SUCCESS_MOCK_CALLS = _get_mock_calls(UPLOAD_SUCCESS_TREE_PATHS)
UPLOAD_SUCCESS_FOLDER_MOCK_CALLS = _get_folder_mock_calls(UPLOAD_SUCCESS_TREE_PATHS)

UPLOAD_SUCCESS_WITH_TREE_NAMES_MOCK_CALLS = _get_mock_calls(UPLOAD_SUCCESS_TREE_PATHS,
                                                            ignore_tree_paths=['tree1', 'tree1/config.yaml',
                                                                               'tree1/attr'])

UPLOAD_SUCCESS_WITH_TREE_NAMES_AS_FOLDER_MOCK_CALLS = _get_folder_mock_calls(UPLOAD_SUCCESS_TREE_PATHS,
                                                            ignore_tree_paths=['tree1', 'tree1/config.yaml',
                                                                               'tree1/attr'])

UPLOAD_SUCCESS_DELETE_EXISTING_MOCK_CALLS = _get_mock_calls(UPLOAD_SUCCESS_TREE_PATHS, delete_existing_trees=True)

UPLOAD_FAILURE_400CASE_TREE_PATHS = OrderedDict([
    ('tree1', None),
    ('tree1/config.yaml', 'a: b'),
    ('tree1/attr', None),
    ('tree2', None),
    ('tree2/robot_type', None),
    ('tree2/robot_type/AGV', None),
    ('tree2/robot_type/AGV/motors.yaml', 'a: b'),
    ('tree2/robot_type/AGV/robot_name', None),
    ('tree2/robot_type/AGV/robot_name/robot1', None),
    ('tree2/robot_type/AMR', None),
    ('tree2/robot_type/AMR/motors.yaml', 'invalid data'),
])

UPLOAD_FAILURE_400CASE_MOCK_CALLS = _get_mock_calls(UPLOAD_FAILURE_400CASE_TREE_PATHS)

UPLOAD_FAILURE_500CASE_TREE_PATHS = OrderedDict([
    ('tree1', None),
    ('tree1/config.yaml', 'a: b'),
    ('tree1/attr', None),
    ('tree2', None),
    ('tree2/robot_type', None),
    ('tree2/robot_type/AGV', None),
    ('tree2/robot_type/AGV/motors.yaml', 'a: b'),
    ('tree2/robot_type/AGV/robot_name', None),
    ('tree2/robot_type/AGV/robot_name/robot1', None),
    ('tree2/robot_type/AGV/robot_name/robot2', None),
    ('tree2/robot_type/AMR', None),
])

UPLOAD_FAILURE_500CASE_MOCK_CALLS = _get_mock_calls(UPLOAD_FAILURE_500CASE_TREE_PATHS,
                                                    ignore_tree_paths=['tree2/robot_type/AGV/robot_name/robot1',
                                                                       'tree2/robot_type/AGV/robot_name/robot2'])

DOWNLOAD_TREES_RESPONSE = {
    'data': ['tree1', 'tree2']
}

DOWNLOAD_TREE1_RESPONSE = {
  'data': {
    'version': 1,
    'type': 'ValueNode',
    'name': 'tree1',
    'path': '/',
    'children': [{
        'version': 1,
        'type': 'AttributeNode',
        'name': 'attr',
        'path': '/attr/',
        'updatedAt': '2019-12-10T04:27:14Z',
        'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
      },
      {
        'version': 1,
        'type': 'FileNode',
        'data': 'a: b',
        'name': 'config.yaml',
        'path': '/config.yaml',
        'updatedAt': '2019-12-10T04:27:11Z',
        'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
      }
    ],
    'updatedAt': '2019-12-10T04:27:01Z',
    'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
  }
}

DOWNLOAD_TREE2_RESPONSE = {
  'data': {
    'version': 1,
    'type': 'ValueNode',
    'name': 'tree2',
    'path': '/',
    'children': [{
        'version': 2,
        'type': 'FileNode',
        'data': 'a: b',
        'name': 'device.yaml',
        'path': '/device.yaml',
        'updatedAt': '2019-12-10T04:35:08Z',
        'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
      },
      {
        'version': 2,
        'type': 'FileNode',
        'data': 'a: b',
        'name': 'motors.yaml',
        'path': '/motors.yaml',
        'updatedAt': '2019-12-10T04:35:20Z',
        'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
      },
      {
        'version': 1,
        'type': 'AttributeNode',
        'name': 'robot_type',
        'path': '/robot_type/',
        'children': [{
            'version': 1,
            'type': 'ValueNode',
            'name': 'AGV',
            'path': '/robot_type/AGV/',
            'children': [{
                'version': 2,
                'type': 'FileNode',
                'data': 'a: b',
                'name': 'motors.yaml',
                'path': '/robot_type/AGV/motors.yaml',
                'updatedAt': '2019-12-10T04:36:01Z',
                'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
              },
              {
                'version': 1,
                'type': 'AttributeNode',
                'name': 'robot_name',
                'path': '/robot_type/AGV/robot_name/',
                'children': [{
                    'version': 1,
                    'type': 'ValueNode',
                    'name': 'robot1',
                    'path': '/robot_type/AGV/robot_name/robot1/',
                    'children': [{
                      'version': 2,
                      'type': 'FileNode',
                      'data': 'a: b',
                      'name': 'device.yaml',
                      'path': '/robot_type/AGV/robot_name/robot1/device.yaml',
                      'updatedAt': '2019-12-10T04:36:38Z',
                      'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
                    }],
                    'updatedAt': '2019-12-10T04:36:17Z',
                    'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
                  },
                  {
                    'version': 1,
                    'type': 'ValueNode',
                    'name': 'robot2',
                    'path': '/robot_type/AGV/robot_name/robot2/',
                    'updatedAt': '2019-12-10T04:36:49Z',
                    'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
                  }
                ],
                'updatedAt': '2019-12-10T04:36:13Z',
                'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
              }
            ],
            'updatedAt': '2019-12-10T04:35:33Z',
            'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
          },
          {
            'version': 1,
            'type': 'ValueNode',
            'name': 'AMR',
            'path': '/robot_type/AMR/',
            'updatedAt': '2019-12-10T04:35:36Z',
            'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
          }
        ],
        'updatedAt': '2019-12-10T04:35:27Z',
        'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
      }
    ],
    'updatedAt': '2019-12-10T04:34:22Z',
    'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
  }
}

GET_BLOB_TREE = {
    'data': {
        'isComplete': True,
        'blobRefs': [
            {
                'ID': 1,
                'CreatedAt': '2020-07-09T09:15:36.688756+05:30',
                'UpdatedAt': '2020-07-09T12:47:04.423233755+05:30',
                'DeletedAt': None,
                'checksum': '5e14cebcc5c5f444e0da2151a49999c0',
                'ownerProject': 'project-pyylndadsnxjdativxazxjgy',
                'signedUrl': 'http://test-signedurl',
                'status': 'Uploaded'
            }
        ]
    }
}

BINARY_FILE_NODE = {
    'version': 1,
    'type': 'FileNode',
    'data': '',
    'blobRefId': '1',
    'name': 'config.png',
    'path': '/config.png',
    'checksum': '5e14cebcc5c5f444e0da2151a49999c0',
    'updatedAt': '2019-12-10T04:27:11Z',
    'userGUID': 'c0b76341-a20c-4e3b-b11b-8a25dc973448'
}
