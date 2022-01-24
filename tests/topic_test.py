# encoding: utf-8
from __future__ import absolute_import
import requests
import unittest

from mock import patch, Mock
from requests import Response

from rapyuta_io.clients.device import TopicKind, Device, QoS
from tests.utils.client import get_client
from tests.utils.device_respones import TOPIC_LIST, TOPIC_LIST_EMPTY, TOPIC_LIST_EMPTY_DATA, \
    TOPICS_STATUS, DEVICE_INFO, SUBSCRIBE_TOPIC_OK, SUBSCRIBE_TOPIC_ERROR, UNSUBSCRIBE_TOPIC_OK, \
    UNSUBSCRIBE_TOPIC_ERROR, SUBSCRIBE_TOPIC_ERROR_INVALID_WHITELIST_TAG, \
    SUBSCRIBE_TOPIC_ERROR_INVALID_WHITELIST_FIELD


class DeviceTopicTests(unittest.TestCase):

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_topic_list_ok(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        topic_list_response = get_device_response()
        topic_list_response.text = TOPIC_LIST
        topic_list_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, topic_list_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        topics = device.topics()
        self.assertEqual(mock_execute.call_count, 2)
        self.assertIsNotNone(topics, 'Actual should not be empty')
        self.assertEqual(len(topics), 6)
        self.assertEqual(topics[1], '/telemetry')
        self.assertEqual(topics[2], '/rosout')
        self.assertEqual(topics[4], '/rosout_agg')

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_topic_list_no_topics(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        topic_list_response = get_device_response()
        topic_list_response.text = TOPIC_LIST_EMPTY
        topic_list_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, topic_list_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        topics = device.topics()
        self.assertEqual(mock_execute.call_count, 2)
        self.assertIsNotNone(topics, 'Actual should not be empty')
        self.assertEqual(len(topics), 0)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_topic_list_empty_data(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        topic_list_response = get_device_response()
        topic_list_response.text = TOPIC_LIST_EMPTY_DATA
        topic_list_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, topic_list_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        topics = device.topics()
        self.assertEqual(mock_execute.call_count, 2)
        self.assertIsNotNone(topics, 'Actual should not be empty')
        self.assertEqual(len(topics), 0)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_get_topic_status_ok(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        topic_status_response = get_device_response()
        topic_status_response.text = TOPICS_STATUS
        topic_status_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, topic_status_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        topics_status = device.topic_status()
        self.assertEqual(mock_execute.call_count, 2)
        self.assertTrue(topics_status.master_up, 'value should be true')
        self.assertEqual(len(topics_status.Unsubscribed), 3)
        self.assertEqual(len(topics_status.Subscribed.metric), 0)
        self.assertEqual(len(topics_status.Subscribed.log), 1)

    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_subscribe_topic_ok(self, mock_execute):
        device_response = Mock()
        device_response.text = DEVICE_INFO
        device_response.status_code = requests.codes.OK
        subscribe_topic_response = Mock()
        subscribe_topic_response.text = SUBSCRIBE_TOPIC_OK
        subscribe_topic_response.status_code = requests.codes.OK
        topic_list_response = Mock()
        topic_list_response.text = TOPIC_LIST
        topic_list_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_response, topic_list_response, subscribe_topic_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        subscription_status = device.subscribe_topic('/rosout', QoS.HIGH.value, TopicKind.METRIC)
        self.assertEqual(mock_execute.call_count, 3)
        self.assertTrue(subscription_status, 'status should be true')

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_subscribe_topic_failure_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        subscribe_topic_response = get_device_response()
        subscribe_topic_response.text = SUBSCRIBE_TOPIC_ERROR
        subscribe_topic_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, subscribe_topic_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        subscription_status = device.subscribe_topic('/testTopic', QoS.HIGH.value, TopicKind.METRIC)
        subscription_error = subscription_status['subscribed_error']
        self.assertEqual(len(subscription_error), 1)
        self.assertEqual(subscription_error[0]['/testTopic'], 'Unknown topic type: /testTopic')
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_un_subscribe_topic_ok(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        unsubscribe_topic_response = get_device_response()
        unsubscribe_topic_response.text = UNSUBSCRIBE_TOPIC_OK
        unsubscribe_topic_response.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, unsubscribe_topic_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        un_subscription_status = device.unsubscribe_topic('/testTopic', TopicKind.METRIC)
        self.assertTrue(un_subscription_status, 'status should be true')
        self.assertEqual(mock_execute.call_count, 2)

    @patch('requests.Response', spec=Response)
    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_un_subscribe_topic_unknown_topic_failure_case(self, mock_execute, get_device_response):
        get_device_response.text = DEVICE_INFO
        get_device_response.status_code = requests.codes.OK
        response2 = get_device_response()
        response2.text = UNSUBSCRIBE_TOPIC_ERROR
        response2.status_code = requests.codes.OK
        mock_execute.side_effect = [get_device_response, response2]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        un_subscription_status = device.unsubscribe_topic('/testTopic', TopicKind.METRIC)
        error = un_subscription_status['unsubscribed_error']
        self.assertIsNotNone(error)
        self.assertEqual(len(error), 1)
        self.assertEqual(error[0], '/testTopic')
        self.assertEqual(mock_execute.call_count, 2)

    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_subscribe_topic_invalid_whitelist_tag(self, mock_execute):
        device_response = Mock()
        device_response.text = DEVICE_INFO
        device_response.status_code = requests.codes.OK
        subscribe_topic_response = Mock()
        subscribe_topic_response.text = SUBSCRIBE_TOPIC_ERROR_INVALID_WHITELIST_TAG
        subscribe_topic_response.status_code = requests.codes.OK
        topic_list_response = Mock()
        topic_list_response.text = TOPIC_LIST
        topic_list_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_response, topic_list_response, subscribe_topic_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        subscription_status = device.subscribe_topic('/rosout', QoS.HIGH.value, TopicKind.METRIC, whitelist_tag=[1,2])
        subscription_error = subscription_status['subscribed_error']
        self.assertEqual(len(subscription_error), 1)
        self.assertEqual(subscription_error[0]['/testTopic'], 'invalid whitelist tag spec topic type: /testTopic')
        self.assertEqual(mock_execute.call_count, 3)

    @patch('rapyuta_io.utils.rest_client.RestClient.execute')
    def test_subscribe_topic_invalid_whitelist_field(self, mock_execute):
        device_response = Mock()
        device_response.text = DEVICE_INFO
        device_response.status_code = requests.codes.OK
        subscribe_topic_response = Mock()
        subscribe_topic_response.text = SUBSCRIBE_TOPIC_ERROR_INVALID_WHITELIST_FIELD
        subscribe_topic_response.status_code = requests.codes.OK
        topic_list_response = Mock()
        topic_list_response.text = TOPIC_LIST
        topic_list_response.status_code = requests.codes.OK
        mock_execute.side_effect = [device_response, topic_list_response, subscribe_topic_response]
        client = get_client()
        device = client.get_device('test_device_id')
        self.assertIsInstance(device, Device, 'Object should be an instance of class Device')
        subscription_status = device.subscribe_topic('/rosout', QoS.HIGH.value, TopicKind.METRIC, whitelist_tag=[1,2])
        subscription_error = subscription_status['subscribed_error']
        self.assertEqual(len(subscription_error), 1)
        self.assertEqual(subscription_error[0]['/testTopic'], 'invalid whitelist field spec topic type: /testTopic')
        self.assertEqual(mock_execute.call_count, 3)
