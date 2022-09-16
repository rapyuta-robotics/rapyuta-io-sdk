from __future__ import absolute_import
from rapyuta_io import DeviceArch
from rapyuta_io.clients.device import SystemMetric, QoS
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.util import get_logger


class MetricsTest(DeviceTest):

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        # Assumption: We only have one amd64 device with Docker runtime.
        devices = self.config.get_devices(arch=DeviceArch.AMD64, runtime="Dockercompose")
        self.device = devices[0]
        self.logger = get_logger()

    def test_metrics(self):
        metrics = self.device.metrics()
        expected_metrics_list = ['cpu', 'disk', 'diskio', 'memory', 'network', 'wireless']
        metric_names = sorted([metric.name for metric in metrics])
        self.assertEqual(len(metrics), 6)
        self.assertEqual(metric_names, expected_metrics_list)

    def test_unsubscribe_metrics(self):
        """Only tests whether unsubscribe_metrics() returns True.
        All metric APIs have been deprecated and they return stubbed responses."""
        metrics_to_unsubscribe = [SystemMetric.CPU, SystemMetric.NETWORK, SystemMetric.MEMORY,
                                  SystemMetric.DISKIO, SystemMetric.DISK, SystemMetric.WIRELESS]
        for metric in metrics_to_unsubscribe:
            self.assertTrue(self.device.unsubscribe_metric(metric))

    def test_subscribe_metrics(self):
        metrics_to_unsubscribe = [SystemMetric.CPU, SystemMetric.NETWORK, SystemMetric.MEMORY,
                                  SystemMetric.DISKIO, SystemMetric.DISK, SystemMetric.WIRELESS]
        for metric in metrics_to_unsubscribe:
            self.assertTrue(self.device.subscribe_metric(metric, qos=QoS.LOW))
        metrics = self.device.metrics()
        self.assertEqual(6, len([metrc for metrc in metrics if metrc.status == 'subscribed']))

