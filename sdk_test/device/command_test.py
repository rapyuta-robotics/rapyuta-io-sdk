from __future__ import absolute_import
from rapyuta_io import Command, DeviceArch
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.util import get_logger

COMMAND = 'script output.txt'
COMMAND_USING_CWD = 'pwd'


class TestDeviceCommand(DeviceTest):

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        # Assumption: We only have one Arm32 device with Preinstalled runtime.
        devices = self.config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        self.device = devices[0]

    def test_execute_command(self):
        command = Command(COMMAND)
        self.logger.info('Command %s is going to execute on device %s(%s)'
                         % (COMMAND, self.device.name, self.device.uuid))
        result = self.device.execute_command(command).replace('\n', '').replace('\r', '')
        expected = 'Script started, file is output.txt# Script done, file is output.txt'
        self.assertEquals(expected, result, 'Actual and expected should be same')
        self.logger.info('Command executed successfully. Result: %s' % result)

    def test_execute_command_using_cwd(self):
        home_dir = '/home'
        command = Command(cmd=COMMAND_USING_CWD, cwd=home_dir)
        self.logger.info('Command %s is going to execute on device %s(%s)'
                         % (COMMAND_USING_CWD, self.device.name, self.device.uuid))
        result = str(self.device.execute_command(command).replace('\n', '').replace('\r', ''))
        expected = home_dir
        self.assertEquals(expected, result, 'Actual and expected should be same')
        self.logger.info('Command executed successfully. Result: %s' % result)
