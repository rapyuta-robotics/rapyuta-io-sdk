from __future__ import absolute_import
from rapyuta_io import DeviceConfig, DeviceArch
from rapyuta_io.utils import OperationNotAllowedError, ConflictError, ResourceNotFoundError
from rapyuta_io.utils.utils import generate_random_value
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.util import get_logger


class TestDeviceConfigVariable(DeviceTest):

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        # Assumption: We only have one Arm32 device with Preinstalled runtime.
        devices = self.config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        self.device = devices[0]
        self.config_variable = None

    def tearDown(self):
        if self.config_variable is not None:
            self.delete_config_variable(self.config_variable)
        self.config_variable = None

    @staticmethod
    def find_config_variable(config_variables, config_id):
        for config in config_variables:
            if config.id == config_id:
                return config
        return None

    def create_config_variable(self, key=generate_random_value(5), value='value'):
        self.config_variable = self.device.add_config_variable(key, value)

    def delete_config_variable(self, config_variable):
        if config_variable:
            try:
                self.device.delete_config_variable(config_variable.id)
            except Exception as err:
                self.logger.error(err)
                self.logger.error('Deleting configuration variable failed (%s)' %
                                  config_variable.key)

    def assert_config_variable(self, device, config_variable, key, value):
        self.logger.info('Validating newly created configuration key and value')
        self.assertIsNotNone(config_variable)
        if not isinstance(config_variable, DeviceConfig):
            raise Exception('Not instance of %s' % DeviceConfig.__class__)
        config_variables = device.get_config_variables()
        new_config_var = self.find_config_variable(config_variables, config_variable.id)
        self.assertIsNotNone(new_config_var, 'Config variable should not be empty')
        self.assertEqual(new_config_var.key, key)
        self.assertEqual(new_config_var.value, value)

    def assert_device_config_variables(self, config_variables):
        self.assertIsNotNone(config_variables)
        runtime_config_var = None
        for config_variable in config_variables:
            self.assertTrue(isinstance(config_variable, DeviceConfig),
                            'Config variable object should be instance of class DeviceConfig')
            self.assertIsNotNone(config_variable.id)
            self.assertIsNotNone(config_variable.key)
            self.assertIsNotNone(config_variable.value)

            if config_variable.key == 'runtime':
                runtime_config_var = config_variable

        if not runtime_config_var:
            raise AssertionError('runtime config variable not found')

        self.logger.info('Total device configuration variables: %d' % len(config_variables))
        self.logger.info(config_variables)

    def test_get_device_config_variables(self):
        self.logger.info('Checking device configuration variables')
        config_variables = self.device.get_config_variables()
        self.assert_device_config_variables(config_variables)

    def test_add_device_config_variable(self):
        self.logger.info('Started add device configuration variables test case')
        config_variables = self.device.get_config_variables()
        self.assert_device_config_variables(config_variables)
        initial_variable_count = len(config_variables)
        self.logger.info('Adding new device configuration variable')
        key = generate_random_value(5)
        value = 'value'
        self.create_config_variable(key, value)
        self.assertEqual(len(self.device.get_config_variables()), initial_variable_count + 1)
        self.assert_config_variable(self.device, self.config_variable, key, value)
        self.logger.info('Configuration variable added successfully')

    def test_add_existing_device_config_variable(self):
        operation = 'Adding the same config variable'
        self.logger.info(operation)
        self.create_config_variable()
        self.with_error(operation, ConflictError, self.device.add_config_variable,
                        self.config_variable.key, self.config_variable.value)

    def test_update_device_config_variable(self):
        self.logger.info('Updating configuration variable')
        self.create_config_variable()
        self.config_variable.value = value = 'new_value'
        self.config_variable = self.device.update_config_variable(self.config_variable)
        self.assert_config_variable(self.device, self.config_variable, self.config_variable.key,
                                    value)

    def test_update_invalid_device_config_variable(self):
        operation = 'Updating invalid device configuration variable'
        self.logger.info(operation)
        invalid_config_var = DeviceConfig(id=-1, key='key', value='value')
        self.with_error(operation, ResourceNotFoundError, self.device.update_config_variable,
                        invalid_config_var)

    def test_update_default_config_variable(self):
        operation = 'Updating default configuration variable: runtime '
        self.logger.info(operation)
        for config in self.device.get_config_variables():
            if config.key == "runtime":
                self.with_error(operation, OperationNotAllowedError,
                                self.device.update_config_variable, config)
                return
        raise AssertionError('runtime config variable is not present')

    def test_delete_device_config_variable(self):
        self.logger.info('Deleting configuration variable')
        self.create_config_variable()
        config_variables = self.device.get_config_variables()
        initial_variable_count = len(config_variables)
        delete_status = self.device.delete_config_variable(self.config_variable.id)
        self.assertTrue(delete_status)
        config_variables = self.device.get_config_variables()
        self.assertEqual(len(config_variables), initial_variable_count - 1)
        self.logger.info('Configuration variable deleted (key: %s)' % self.config_variable.key)
        self.config_variable = None

    def test_delete_default_config_variable(self):
        operation = 'Deleting default configuration variable'
        self.logger.info(operation)
        for config in self.device.get_config_variables():
            if config.key in DeviceConfig.DEFAULT_DEVICE_CONFIG_VARIABLES:
                self.with_error(operation + ' %s' % config.key, OperationNotAllowedError,
                                self.device.delete_config_variable, config.id)
                return
