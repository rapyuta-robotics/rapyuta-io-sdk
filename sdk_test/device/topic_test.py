from __future__ import absolute_import

from rapyuta_io import TopicKind, DeviceArch
from rapyuta_io.clients.device import QoS
from rapyuta_io.utils import BadRequestError
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.util import get_logger, start_roscore, stop_roscore
import six


class TestTopic(DeviceTest):

    @classmethod
    def setUpClass(cls):
        config = Configuration()
        devices = config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        start_roscore(devices[0])

    @classmethod
    def tearDownClass(cls):
        config = Configuration()
        devices = config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        stop_roscore(devices[0])

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        # Assumption: We only have one Arm32 device with Docker runtime.
        self.device = self.config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")[0]

    def assert_topic_subscription_status(self, topic, subscription_status):
        if subscription_status.get('subscribed_success', None):
            self.assertIn(topic, subscription_status.get('subscribed_success'),
                          'Topic %s not found on the subscribed list' % topic)
            self.logger.info('Topic %s subscribed successfully' % topic)
            return
        elif subscription_status.get('subscribed_error', None):
            error = subscription_status.get('subscribed_error')[0][topic]
            self.logger.info('Topic subscription failed due to %s' % error)

        raise AssertionError('Topic subscription failed for the topic: %s' % topic)

    def assert_topic_unsubscription_status(self, topic, unsubscription_status):
        if unsubscription_status.get('unsubscribed_success', None):
            self.assertIn(topic, unsubscription_status.get('unsubscribed_success'),
                          'Topic %s not found on the unsubscribed list' % topic)
            self.logger.info('Topic %s unsubscribed successfully' % topic)
            return
        elif unsubscription_status.get('unsubscribed_error', None):
            error = unsubscription_status.get('unsubscribed_error')[0]
            self.logger.error('Topic unsubscription failed due to %s' % error)

        raise AssertionError('Topic unsubscription failed for the topic: %s' % topic)

    def assert_topic_status(self, topic_status, topic, kind):
        self.logger.info('Asserting subscribed topic is present on the subscription status')
        if isinstance(kind, TopicKind):
            kind = kind.value
        for topic_dict in topic_status.Subscribed[kind.lower()]:
            if topic == topic_dict['name']:
                self.logger.info('Topic %s is in the subscribed list' % topic)
                return
        self.logger.error('Topic %s is not found in the subscribed list' % topic)
        raise AssertionError('%s topic is not in subscribed list' % topic)

    def subscribe_any_topic(self):
        topics = self.device.topics()
        self.assertNotEqual(0, len(topics), 'Topics should not be empty')
        topic = topics[0]
        subscription_status = self.device.subscribe_topic(topic, QoS.MEDIUM.value, TopicKind.LOG)
        topic_status = self.device.topic_status()
        self.assert_topic_subscription_status(topic, subscription_status)
        self.assert_topic_status(topic_status, topic, TopicKind.LOG)
        return topic

    def test_topics(self):
        self.logger.info('Started device topics test')
        self.logger.info('Getting topic lists')
        topics = self.device.topics()
        self.assertTrue(isinstance(topics, list))
        for topic in topics:
            self.assertTrue(isinstance(topic, six.string_types))
        self.logger.info(topics)

    def test_topic_status(self):
        self.logger.info('Getting topic status')
        topic_status = self.device.topic_status()
        self.assertTrue(isinstance(topic_status.Subscribed.metric, list))
        self.assertTrue(isinstance(topic_status.Subscribed.log, list))
        self.assertTrue(isinstance(topic_status.Unsubscribed, list))
        self.logger.info(topic_status)

    def test_subscribe_topic(self):
        self.logger.info('Subscribing for a valid topic')
        self.subscribe_any_topic()

    def test_subscribe_unknown_topic(self):
        self.logger.info('Subscribing for unknown topic')
        unknown_topic = '/unknow_topic'
        with self.assertRaises(AssertionError):
            subscription_status = self.device.subscribe_topic(unknown_topic, QoS.HIGH.value, TopicKind.METRIC)
            self.assert_topic_subscription_status(unknown_topic, subscription_status)

    def test_unsubscribe_topic(self):
        self.logger.info('Unsubscribing valid topic')
        topic_status = self.device.topic_status()
        topic = None
        if len(topic_status.Subscribed.metric) > 0:
            topic = topic_status.Subscribed.metric[0].get('name')
            kind = TopicKind.METRIC
        elif len(topic_status.Subscribed.log) > 0:
            topic = topic_status.Subscribed.log[0]['name']
            kind = TopicKind.LOG

        if not topic:
            topic = self.subscribe_any_topic()
            kind = TopicKind.LOG

        unsubscription_status = self.device.unsubscribe_topic(topic, kind)
        self.assert_topic_unsubscription_status(topic, unsubscription_status)

    def test_unsubscribe_unknown_topic(self):
        self.logger.info('Unsubscribing invalid topic')
        unknown_topic = '/unknow_topic'
        with self.assertRaises(AssertionError):
            unsubscription_status = self.device.unsubscribe_topic(unknown_topic, TopicKind.METRIC)
            self.assert_topic_unsubscription_status(unknown_topic, unsubscription_status)

    def test_subscribe_topic_with_fields_override(self):
        self.logger.info('Subscribing for unknown topic')
        unknown_topic = '/unknow_topic'
        subscription_status = self.device.subscribe_topic(unknown_topic, QoS.HIGH.value, TopicKind.METRIC,
                                                          whitelist_field=['randomfieldoverride'],
                                                          fail_on_topic_inexistence=False)
        self.assert_topic_subscription_status(unknown_topic, subscription_status)

    def test_subscribe_topic_with_tags_fields_override(self):
        self.logger.info('Subscribing for unknown topic')
        unknown_topic = '/unknow_topic'
        subscription_status = self.device.subscribe_topic(unknown_topic, QoS.HIGH.value, TopicKind.METRIC,
                                                          whitelist_field=['randomfieldoverride'],
                                                          whitelist_tag=['randomtags'],
                                                          fail_on_topic_inexistence=False)
        self.assert_topic_subscription_status(unknown_topic, subscription_status)

    def test_subscribe_topic_with_tags_override_error(self):
        self.logger.info('Subscribing for unknown topic')
        unknown_topic = '/unknow_topic'
        self.with_error('', BadRequestError, self.device.subscribe_topic, unknown_topic, QoS.HIGH.value,
                        TopicKind.METRIC,
                        whitelist_tag=['randomtags', 1, 2],
                        whitelist_field=['randomfieldoverride'],
                        fail_on_topic_inexistence=False)

    def test_subscribe_topic_with_fields_override_error(self):
        self.logger.info('Subscribing for unknown topic')
        unknown_topic = '/unknow_topic'
        self.with_error('', BadRequestError, self.device.subscribe_topic, unknown_topic, QoS.HIGH.value,
                        TopicKind.METRIC,
                        whitelist_field=['randomfieldoverride', 1, 2],
                        whitelist_tag=['randomtags'],
                        fail_on_topic_inexistence=False)
