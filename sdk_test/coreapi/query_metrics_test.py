import pytz
from datetime import datetime, timedelta
from unittest import TestCase


from rapyuta_io import DeviceArch
from rapyuta_io.clients.device import SystemMetric, QoS
from rapyuta_io.clients.metrics import QueryMetricsRequest, MetricFunction, MetricOperation, \
    StepInterval, SortOrder, ListMetricsRequest, Entity, ListTagKeysRequest, ListTagValuesRequest
from rapyuta_io.utils.error import ConflictError
from sdk_test.config import Configuration
from sdk_test.util import get_logger
from time import sleep


class MetricsTests(TestCase):
    DEVICE = None
    WAIT_TIME = 120

    @classmethod
    def setUpClass(cls):
        config = Configuration()
        logger = get_logger()
        device = config.get_devices(arch=DeviceArch.AMD64, runtime='Dockercompose')[0]
        try:
            logger.info('subscribing to metrics')
            device.subscribe_metric(SystemMetric.CPU, QoS.LOW)
            logger.info('waiting for {} seconds '.format(cls.WAIT_TIME))
            sleep(cls.WAIT_TIME)
        except ConflictError:
            get_logger().info('metrics is info already subscribed')
        cls.DEVICE = device

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.to_datetime = datetime.now(pytz.UTC)
        self.from_datetime = self.to_datetime - timedelta(days=1)

    @classmethod
    def tearDownClass(cls):
        cls.DEVICE.unsubscribe_metric(SystemMetric.CPU)

    def assert_column_object_fields(self, columns):
        self.assertTrue(self.has_value_for_attribute(columns, 'name'))
        self.assertTrue(all(map(lambda x: getattr(x, 'function') if x.name != 'timestamp' else True,
                                columns)))
        self.assertTrue(all(map(lambda x: getattr(x, 'metric_group') if x.name != 'timestamp' else True,
                                columns)))
        for col in columns:
            if getattr(col, 'tag_names'):
                self.assertTrue(len(col.tag_names) == len(col.tag_values))

    @staticmethod
    def has_value_for_attribute(response, field):
        return all(map(lambda x: getattr(x, field), response))

    def test_query_metrics(self):
        metrics = [MetricOperation(MetricFunction.COUNT, 'cpu.usage_system'),
                   MetricOperation(MetricFunction.PERCENTILE_95, 'cpu.usage_idle')]
        query_metrics_request = QueryMetricsRequest(self.from_datetime, self.to_datetime, StepInterval.ONE_MINUTE,
                                                    metrics, groupby=['device_id'], sort=SortOrder.DESC)
        metrics_response = self.config.client.query_metrics(query_metrics_request)

        self.assert_column_object_fields(metrics_response.columns)
        self.assertTrue(len(metrics_response.columns))
        self.assertTrue(len(metrics_response.rows) == len(metrics_response.columns))

    def test_list_metrics(self):
        list_metrics_query = ListMetricsRequest(Entity.PROJECT, self.config._project.guid,
                                                self.from_datetime, self.to_datetime)
        metrics = self.config.client.list_metrics(list_metrics_query)

        self.assertTrue(len(metrics))
        self.assertTrue(self.has_value_for_attribute(metrics, 'metric_group'))
        self.assertTrue(self.has_value_for_attribute(metrics, 'metric_names'))

    def test_list_tag_keys(self):
        list_tag_keys_query = ListTagKeysRequest(Entity.PROJECT, self.config._project.guid,
                                                 self.from_datetime, self.to_datetime)
        tag_keys = self.config.client.list_tag_keys(list_tag_keys_query)

        self.assertTrue(len(tag_keys))
        self.assertTrue(self.has_value_for_attribute(tag_keys, 'tags'))
        self.assertTrue(self.has_value_for_attribute(tag_keys, 'metric_group'))

    def test_list_tag_values(self):
        tag = 'cpu'
        list_tag_values_query = ListTagValuesRequest(Entity.PROJECT, self.config._project.guid, tag,
                                                     self.from_datetime, self.to_datetime)
        tag_values = self.config.client.list_tag_values(list_tag_values_query)

        self.assertTrue(len(tag_values))
        self.assertTrue(isinstance(tag_values, list))
