from __future__ import absolute_import
from rapyuta_io import Label, DeviceArch
from rapyuta_io.utils import ConflictError, LabelNotFoundException
from rapyuta_io.utils.utils import generate_random_value
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.util import get_logger


class TestDeviceLabel(DeviceTest):

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        # Assumption: We only have one Arm32 device with Docker runtime.
        devices = self.config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        self.device = devices[0]
        self.label = None

    def tearDown(self):
        self.delete_label(self.label)

    def test_get_labels(self):
        labels = self.device.get_labels()
        self.assert_device_labels(labels)

    def create_label(self, key=generate_random_value(5), value='value'):
        self.label = self.device.add_label(key, value)

    def assert_label(self, device, label, key, value):
        self.logger.info('Validating label key and value')
        self.assertIsNotNone(label)
        if not isinstance(label, Label):
            raise Exception('Not instance of %s' % Label.__class__)
        labels = device.get_labels()

        new_label = self.find_label(labels, label.id)
        self.assertIsNotNone(new_label, 'Label should not be empty')
        self.assertEqual(new_label.key, key)
        self.assertEqual(new_label.value, value)

    def assert_device_labels(self, labels):
        for label in labels:
            self.assertTrue(isinstance(label, Label), 'Should be instance of class Label')
            self.assertIsNotNone(label.id)
            self.assertIsNotNone(label.key)
            self.assertIsNotNone(label.value)

        self.logger.info('Total device labels: %d' % len(labels))
        self.logger.info(labels)

    def delete_label(self, label):
        if label:
            try:
                self.device.delete_label(label.id)
            except Exception as err:
                self.logger.error(err)
                self.logger.error('Deleting label failed (%s)' % label.key)

    @staticmethod
    def find_label(labels, label_id):
        for label in labels:
            if label.id == label_id:
                return label
        return None

    def test_add_label(self):
        self.logger.info('Adding new label')
        labels = self.device.get_labels()
        initial_label_count = len(labels)
        label_key = generate_random_value(5)
        label_value = 'value'
        self.create_label(label_key, label_value)
        self.assert_label(self.device, self.label, label_key, label_value)
        self.logger.info('Checking labels count after adding new label: %s' % label_key)
        labels = self.device.get_labels()
        self.assertEqual(len(labels), initial_label_count + 1)
        self.logger.info('Label added successfully')

        operation = 'Adding the same label'
        self.logger.info(operation)
        self.with_error(operation, ConflictError, self.device.add_label, label_key, label_value)

    def test_update_label(self):
        self.logger.info('Updating label')
        self.create_label()
        self.label.value = update_label_value = 'new_value'
        label_key = self.label.key
        label = self.device.update_label(self.label)
        self.logger.info('Checking updated label: %s' % label.key)
        self.assert_label(self.device, self.label, label_key, update_label_value)
        self.logger.info('Label updated successfully')

    def test_update_invalid_label(self):
        operation = 'Updating invalid device label'
        invalid_label = Label(id=0, key='key', value='value')
        self.logger.info(operation)
        self.with_error(operation, LabelNotFoundException, self.device.update_label, invalid_label)

    def test_delete_label(self):
        self.logger.info('Deleting label')
        self.create_label()
        initial_label_count = len(self.device.get_labels())
        delete_status = self.device.delete_label(self.label.id)
        self.assertTrue(delete_status)
        labels = self.device.get_labels()
        self.logger.info('Checking labels count %d == %d' % (len(labels), initial_label_count))
        self.assertEqual(len(labels), initial_label_count - 1)
        self.logger.info('Label deleted (key: %s)' % self.label.key)
        self.label = None
