from __future__ import absolute_import

import requests
import unittest

from mock import patch, Mock, call
from datetime import datetime, timedelta

from rapyuta_io.clients.metrics import QueryMetricsRequest, MetricFunction, MetricOperation, \
    StepInterval, SortOrder, ListMetricsRequest, Entity, ListTagKeysRequest, ListTagValuesRequest
from rapyuta_io.utils.error import InvalidParameterException
from tests.utils.client import get_client, headers
from tests.utils.query_metrics_responses import QUERY_METRICS_SUCCESS, QUERY_METRICS_SUCCESS_WITH_GROUPBY, \
    LIST_METRICS_SUCCESS, LIST_TAG_KEYS_SUCCESS, LIST_TAG_VALUES_SUCCESS
from tests.utils.user_response import GET_USER_RESPONSE


class QueryMetricsTests(unittest.TestCase):
    def setUp(self):
        self.project = 'test-project'
        self.organization = 'test-organization'
        self.from_datetime = datetime.now() - timedelta(days=1)
        self.to_datetime = datetime.now()
        self.metrics = [MetricOperation(MetricFunction.COUNT, 'cpu.usage_idle')]
        self.tags = {
            'tenant_id': {'operator': 'eq', 'value': 'test-project'},
            'organization_id': {'operator': 'eq', 'value': 'test-organization'}
        }
        super(QueryMetricsTests, self).setUp()

    def test_query_metrics_invalid_from_date(self):
        expected_err_msg = 'from_datetime should be a datetime object'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest('invalid_from_datetime', self.to_datetime,
                                                     StepInterval.ONE_MINUTE, self.metrics))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_to_date(self):
        expected_err_msg = 'to_datetime should be a datetime object'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, 'invalid_to_datetime',
                                                     StepInterval.ONE_MINUTE, self.metrics))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_step_interval(self):
        expected_err_msg = 'step_interval should be a member of StepInterval enum'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     'ONE_MINUTE', self.metrics))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_metric_function(self):
        expected_err_msg = 'function should be member of MetricFunction'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE, [MetricOperation('invalid-function',
                                                                                               'cpu.metrics')]))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_metric_name(self):
        expected_err_msg = 'metric name should be a string'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE,
                                                     [MetricOperation(MetricFunction.COUNT, None)]))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_empty_metric_operation(self):
        expected_err_msg = 'metrics should be non-empty list of MetricOperation objects'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE, []))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_metric_operation_element(self):
        expected_err_msg = 'metrics should be non-empty list of MetricOperation objects'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE, [None]))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_tags(self):
        expected_err_msg = 'tags should be key value of tags and values'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE, self.metrics,
                                                     tags='invalid_tags'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_sort(self):
        expected_err_msg = 'sort should be a member of SortOrder enum'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE, self.metrics, self.tags,
                                                     sort='ASC'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_groupby(self):
        expected_err_msg = 'grouby should be list of strings'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE, self.metrics,
                                                     groupby='invalid_groupby'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_groupby_element(self):
        expected_err_msg = 'grouby should be list of strings'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE, self.metrics,
                                                     groupby=[None]))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_clickhouse_step_interval(self):
        expected_err_msg = 'step_interval must be one of 1m, 5m, 15m for from_datetime before 7 days from today'
        client = get_client()
        self.from_datetime = datetime.now() - timedelta(days=8)
        self.to_datetime = self.from_datetime + timedelta(days=1)
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_SECOND, self.metrics))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_from_datetime_greater_than_to_datetime(self):
        expected_err_msg = 'from_datetime must be less than to_datetime'
        client = get_client()
        self.from_datetime = datetime.now() + timedelta(days=1)
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics(QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                                     StepInterval.ONE_MINUTE, self.metrics))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_query_metrics_invalid_metrics_query_object(self):
        expected_err_msg = 'metrics_query_request must be of type ' \
                           'rapyuta_io.clients.metrics.MetricsQueryRequest'
        client = get_client()
        with self.assertRaises(InvalidParameterException) as e:
            client.query_metrics('invalid_data')

        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_query_metrics_success(self, mock_request):
        expected_payload = {'from': self.from_datetime.isoformat(),
                            'tags': {
                                'organization_id': {'operator': 'eq', 'value': 'test-organization'},
                                'tenant_id': {'operator': 'eq', 'value': 'test-project'}
                            },
                            'metrics': [{'function': 'count', 'metric_name': 'cpu.usage_idle'}],
                            'to': self.to_datetime.isoformat(), 'step': '1m', 'sort': 'desc'}

        query_metrics = QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                            StepInterval.ONE_MINUTE, self.metrics, tags=self.tags, sort=SortOrder.DESC)
        mock_query_metrics_request = Mock()
        mock_query_metrics_request.text = QUERY_METRICS_SUCCESS
        mock_query_metrics_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_query_metrics_request]
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/metrics/v0/query/'

        client = get_client()
        response = client.query_metrics(query_metrics)

        mock_request.assert_called_once_with(headers=headers,
                                             json=expected_payload,
                                             url=expected_url,
                                             method='POST',
                                             params={},
                                             timeout=(30, 150))

        rows, cols = response.to_row_column_format()
        self.assertEqual(len(response.columns) == len(response.rows), True)
        self.assertEqual(list(cols), ['timestamp', 'count(cpu.usage_user)'])
        self.assertEqual(list(rows), [(1612814880000000000, 0.7716360673079268),
                                      (1612814890000000000, 0.7716360673079268)])

    @patch('requests.request')
    def test_query_metrics_success_with_groupby(self, mock_request):
        expected_payload = {'sort': 'asc', 'from': self.from_datetime.isoformat(),
                            'tags': {
                                'organization_id': {'operator': 'eq', 'value': 'test-organization'},
                                'tenant_id': {'operator': 'eq', 'value': 'test-project'}
                            },
                            'metrics': [{'function': 'count', 'metric_name': 'cpu.usage_idle'}],
                            'to': self.to_datetime.isoformat(), 'step': '1m',
                            'groupby': ['device_id', 'host']}
        expected_columns = ['timestamp',
                            'count(cpu.usage_idle){device_id=35b1a367-5c83-473e-9e44-1e57ac520c44,host=rapyuta}',
                            'count(cpu.usage_idle){device_id=7d4283a4-5912-4f85-83d3-f6e6584f36dc,host=rapyuta}']
        expected_rows = [(1612814880000000000, 0.5106911720333912, 0.9757220882033476),
                         (1612814890000000000, None, None), (1612814900000000000, None, None),
                         (1612814910000000000, 0.35028308953010395, None)]

        query_metrics = QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                            StepInterval.ONE_MINUTE, self.metrics,
                                            tags=self.tags, groupby=['device_id', 'host'])
        mock_query_metrics_request = Mock()
        mock_query_metrics_request.text = QUERY_METRICS_SUCCESS_WITH_GROUPBY
        mock_query_metrics_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_query_metrics_request]
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/metrics/v0/query/'

        client = get_client()
        response = client.query_metrics(query_metrics)

        mock_request.assert_called_once_with(headers=headers,
                                             json=expected_payload,
                                             url=expected_url,
                                             method='POST',
                                             params={},
                                             timeout=(30, 150))

        rows, cols = response.to_row_column_format()
        self.assertEqual(len(response.columns) == len(response.rows), True)
        self.assertEqual(list(cols), expected_columns)
        self.assertEqual(list(rows), expected_rows)

    @patch('requests.request')
    def test_query_metrics_success_without_project_in_tags(self, mock_request):
        expected_payload = {'from': self.from_datetime.isoformat(),
                            'tags': {
                                'organization_id': {'operator': 'eq', 'value': 'test-organization'},
                                'tenant_id': {'operator': 'eq', 'value': 'test_project'}
                            },
                            'metrics': [{'function': 'count', 'metric_name': 'cpu.usage_idle'}],
                            'to': self.to_datetime.isoformat(), 'step': '1m', 'sort': 'desc'}

        query_metrics = QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                            StepInterval.ONE_MINUTE, self.metrics,
                                            tags={'organization_id': {'operator': 'eq', 'value': self.organization}},
                                            sort=SortOrder.DESC)
        mock_query_metrics_request = Mock()
        mock_query_metrics_request.text = QUERY_METRICS_SUCCESS
        mock_query_metrics_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_query_metrics_request]
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/metrics/v0/query/'

        client = get_client()
        response = client.query_metrics(query_metrics)

        mock_request.assert_called_once_with(headers=headers,
                                             json=expected_payload,
                                             url=expected_url,
                                             method='POST',
                                             params={},
                                             timeout=(30, 150))

        rows, cols = response.to_row_column_format()
        self.assertEqual(len(response.columns) == len(response.rows), True)
        self.assertEqual(list(cols), ['timestamp', 'count(cpu.usage_user)'])
        self.assertEqual(list(rows), [(1612814880000000000, 0.7716360673079268),
                                      (1612814890000000000, 0.7716360673079268)])

    @patch('requests.request')
    def test_query_metrics_success_without_organization_in_tags(self, mock_request):
        expected_payload = {'from': self.from_datetime.isoformat(),
                            'tags': {
                                'organization_id': {'operator': 'eq', 'value': 'test-organization'},
                                'tenant_id': {'operator': 'eq', 'value': 'test-project'}
                            },
                            'metrics': [{'function': 'count', 'metric_name': 'cpu.usage_idle'}],
                            'to': self.to_datetime.isoformat(), 'step': '1m', 'sort': 'desc'}

        query_metrics = QueryMetricsRequest(self.from_datetime, self.to_datetime,
                                            StepInterval.ONE_MINUTE, self.metrics,
                                            tags={'tenant_id': {'operator': 'eq', 'value': self.project}},
                                            sort=SortOrder.DESC)
        mock_get_user_request = Mock()
        mock_get_user_request.text = GET_USER_RESPONSE
        mock_get_user_request.status_code = requests.codes.OK

        mock_query_metrics_request = Mock()
        mock_query_metrics_request.text = QUERY_METRICS_SUCCESS
        mock_query_metrics_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_get_user_request, mock_query_metrics_request]
        expected_get_user_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/user/me/get'
        expected_query_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/metrics/v0/query/'

        client = get_client()
        response = client.query_metrics(query_metrics)

        mock_request.assert_has_calls([
            call(headers=headers, json=None, method='GET', params={}, url=expected_get_user_url, timeout=(30, 150)),
            call(headers=headers, json=expected_payload, url=expected_query_url, method='POST', params={},
                 timeout=(30, 150))
        ])

        rows, cols = response.to_row_column_format()
        self.assertEqual(len(response.columns) == len(response.rows), True)
        self.assertEqual(len(response.columns) == len(response.rows), True)
        self.assertEqual(list(cols), ['timestamp', 'count(cpu.usage_user)'])
        self.assertEqual(list(rows), [(1612814880000000000, 0.7716360673079268),
                                      (1612814890000000000, 0.7716360673079268)])

    def test_list_metrics_invalid_entity(self):
        expected_err_msg = 'entity should be a member of Entity enum'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListMetricsRequest('invalid_entity', self.project,
                                                   self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_metrics_invalid_entity_id(self):
        expected_err_msg = 'entity_id non empty string'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListMetricsRequest(Entity.PROJECT, 123, self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_metrics_empty_entity_id(self):
        expected_err_msg = 'entity_id non empty string'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListMetricsRequest(Entity.PROJECT, '', self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_metrics_invalid_start_date(self):
        expected_err_msg = 'start_date should be a datetime object'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListMetricsRequest(Entity.PROJECT, self.project,
                                                   'invalid_from_datetime', self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_metrics_invalid_end_date(self):
        expected_err_msg = 'end_date should be a datetime object'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListMetricsRequest(Entity.PROJECT, self.project,
                                                   self.from_datetime, 'invalid_to_datetime'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_metrics_entity_org_for_influx(self):
        expected_err_msg = 'Entity.ORGANIZATION cannot be queried for start_date before 7 days from today'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListMetricsRequest(Entity.ORGANIZATION, self.organization,
                                                   self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_metrics_start_date_greater_than_end_date(self):
        expected_err_msg = 'start_date must be less than end_date'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListMetricsRequest(Entity.PROJECT, self.project, self.to_datetime, self.from_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_metrics_invalid_list_metrics_query_object(self):
        expected_err_msg = 'metrics_query_request must be of type rapyuta_io.clients.metrics.ListMetricsRequest'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics('invalid_query')

        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_list_metrics_success(self, mock_request):
        expected_params = {'start_date': self.from_datetime.isoformat(), 'end_date': self.to_datetime.isoformat()}
        mock_list_metrics_request = Mock()
        mock_list_metrics_request.text = LIST_METRICS_SUCCESS
        mock_list_metrics_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_metrics_request]
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/metrics/v0/metrics/{}/{}'.format(
            Entity.PROJECT,
            self.project)

        client = get_client()
        response = client.list_metrics(ListMetricsRequest(Entity.PROJECT, self.project,
                                                          self.from_datetime, self.to_datetime))

        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params=expected_params,
                                             timeout=(30, 150))

        self.assertEqual(response[0].metric_group, 'cpu')
        self.assertEqual(response[0].metric_names, ['usage_guest', 'usage_guest_nice', 'usage_idle',
                                                    'usage_iowait', 'usage_irq', 'usage_nice',
                                                    'usage_softirq', 'usage_steal', 'usage_system', 'usage_user'])

    def test_list_tag_keys_invalid_entity(self):
        expected_err_msg = 'entity should be a member of Entity enum'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListTagKeysRequest('invalid_entity', self.project,
                                                   self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_keys_invalid_entity_id(self):
        expected_err_msg = 'entity_id non empty string'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListTagKeysRequest(Entity.PROJECT, 123, self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_keys_empty_entity_id(self):
        expected_err_msg = 'entity_id non empty string'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListTagKeysRequest(Entity.PROJECT, '', self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_keys_invalid_start_date(self):
        expected_err_msg = 'start_date should be a datetime object'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListTagKeysRequest(Entity.PROJECT, self.project,
                                                   'invalid_date', self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_keys_invalid_end_date(self):
        expected_err_msg = 'end_date should be a datetime object'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListTagKeysRequest(Entity.PROJECT, self.project,
                                                   self.from_datetime, 'invalid_date'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_keys_entity_org_for_influx(self):
        expected_err_msg = 'Entity.ORGANIZATION cannot be queried for start_date before 7 days from today'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListTagKeysRequest(Entity.ORGANIZATION, self.organization,
                                                   self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_keys_start_date_greater_than_end_date(self):
        expected_err_msg = 'start_date must be less than end_date'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_metrics(ListTagKeysRequest(Entity.PROJECT, self.project,
                                                   self.to_datetime,
                                                   self.from_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_keys_invalid_query_object(self):
        expected_err_msg = 'metrics_query_request must be of type rapyuta_io.clients.metrics.ListTagKeysRequest'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_keys('invalid_query')

        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_list_tag_keys_success(self, mock_request):
        expected_params = {'start_date': self.from_datetime.isoformat(), 'end_date': self.to_datetime.isoformat()}
        mock_list_tag_keys_request = Mock()
        mock_list_tag_keys_request.text = LIST_TAG_KEYS_SUCCESS
        mock_list_tag_keys_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_tag_keys_request]
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/metrics/v0/tags/{}/{}'.format(
            Entity.PROJECT,
            self.project)

        client = get_client()
        response = client.list_tag_keys(ListTagKeysRequest(Entity.PROJECT, self.project,
                                                           self.from_datetime, self.to_datetime))

        mock_request.assert_called_once_with(headers=headers,
                                             json=None,
                                             url=expected_url,
                                             method='GET',
                                             params=expected_params,
                                             timeout=(30, 150))

        self.assertEqual(response[0].metric_group, 'cpu')
        self.assertEqual(response[0].tags, ['cpu', 'device_id', 'host', 'tenant_id'])

    def test_list_tag_values_invalid_entity(self):
        expected_err_msg = 'entity should be a member of Entity enum'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest('invalid_entity', self.project, 'tag',
                                                        self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_invalid_entity_id(self):
        expected_err_msg = 'entity_id non empty string'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest(Entity.PROJECT, 123, 'tag',
                                                        self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_empty_entity_id(self):
        expected_err_msg = 'entity_id non empty string'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest(Entity.PROJECT, '', 'tag',
                                                        self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_invalid_tag_key(self):
        expected_err_msg = 'tag non empty string'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest(Entity.PROJECT, self.project, 123,
                                                        self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_empty_tag_key(self):
        expected_err_msg = 'tag non empty string'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest(Entity.PROJECT, self.project, '',
                                                        self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_invalid_start_date(self):
        expected_err_msg = 'start_date should be a datetime object'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest(Entity.PROJECT, self.project, 'tag',
                                                        'invalid_data', self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_invalid_end_date(self):
        expected_err_msg = 'end_date should be a datetime object'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest(Entity.PROJECT, self.project, 'tag',
                                                        self.from_datetime, 'invalid_data'))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_entity_org_for_influx(self):
        expected_err_msg = 'Entity.ORGANIZATION cannot be queried for start_date before 7 days from today'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest(Entity.ORGANIZATION, self.organization, 'tag',
                                                        self.from_datetime, self.to_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_start_date_greater_than_end_date(self):
        expected_err_msg = 'start_date must be less than end_date'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values(ListTagValuesRequest(Entity.PROJECT, self.project, 'tag',
                                                        self.to_datetime, self.from_datetime))

        self.assertEqual(str(e.exception), expected_err_msg)

    def test_list_tag_values_invalid_query_object(self):
        expected_err_msg = 'metrics_query_request must be of type rapyuta_io.clients.metrics.ListTagValuesRequest'
        client = get_client()

        with self.assertRaises(InvalidParameterException) as e:
            client.list_tag_values('invalid_query')

        self.assertEqual(str(e.exception), expected_err_msg)

    @patch('requests.request')
    def test_list_tag_values_success(self, mock_request):
        tag = 'cpu'
        expected_params = {'start_date': self.from_datetime.isoformat(), 'end_date': self.to_datetime.isoformat()}
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/metrics/v0/tags/{}/{}/{}'.format(
            Entity.PROJECT,
            self.project, tag)
        mock_list_tag_values_request = Mock()
        mock_list_tag_values_request.text = LIST_TAG_VALUES_SUCCESS
        mock_list_tag_values_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_tag_values_request]

        client = get_client()
        response = client.list_tag_values(ListTagValuesRequest(Entity.PROJECT, self.project, tag,
                                                               self.from_datetime, self.to_datetime))

        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url,
                                             method='GET',
                                             params=expected_params,
                                             timeout=(30, 150))

        self.assertEqual(response, ['cpu-total', 'cpu0', 'cpu1', 'cpu2', 'cpu3'])

    @patch('requests.request')
    def test_list_tag_values_entity_org_success(self, mock_request):
        tag = 'cpu'
        from_datetime = datetime.now() - timedelta(days=7, minutes=1)
        expected_params = {'start_date': from_datetime.isoformat(), 'end_date': self.to_datetime.isoformat()}
        expected_url = 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io/api/metrics/v0/tags/{}/{}/{}'.format(
            Entity.ORGANIZATION,
            self.organization, tag)
        mock_list_tag_values_request = Mock()
        mock_list_tag_values_request.text = LIST_TAG_VALUES_SUCCESS
        mock_list_tag_values_request.status_code = requests.codes.OK
        mock_request.side_effect = [mock_list_tag_values_request]

        client = get_client()
        response = client.list_tag_values(ListTagValuesRequest(Entity.ORGANIZATION, self.organization, tag,
                                                               from_datetime, self.to_datetime))

        mock_request.assert_called_once_with(headers=headers, json=None,
                                             url=expected_url,
                                             method='GET',
                                             params=expected_params,
                                             timeout=(30, 150))

        self.assertEqual(response, ['cpu-total', 'cpu0', 'cpu1', 'cpu2', 'cpu3'])
