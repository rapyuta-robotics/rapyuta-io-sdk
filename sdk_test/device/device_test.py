from __future__ import absolute_import
import unittest

from rapyuta_io import DeviceStatus


class DeviceTest(unittest.TestCase):

    def with_error(self, message, exception_class, fun, *args, **kwargs):
        try:
            fun(*args, **kwargs)
        except exception_class:
            self.logger.info('%s Exception raised while %s' % (exception_class.__name__, message))
            return
        raise AssertionError('Expected %s exception. But no exception were raised'
                             % exception_class.__name__)

    def assert_device_status(self, device, status):
        self.logger.info('Checking device status')
        self.assertIsNotNone(device)
        if isinstance(status, DeviceStatus):
            status = status.value
        self.assertEqual(device.status.lower(), status.lower(),
                         'Device is not online(%s)' % device.status)
        self.logger.info('Device(%s) is %s' % (device.name, device.status))

