from __future__ import absolute_import
import time
from datetime import timedelta, datetime

from rapyuta_io import DeviceArch
from rapyuta_io.clients import LogsUploadRequest, SharedURL
from rapyuta_io.utils import LogsUUIDNotFoundException
from rapyuta_io.utils.utils import generate_random_value
from sdk_test.config import Configuration
from sdk_test.device.device_test import DeviceTest
from sdk_test.util import get_logger
import six

LOG_SALT_MINION = '/var/log/salt/minion'

MINION = 'minion'


class LogsTest(DeviceTest):

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        # Assumption: We only have one Arm32 device with Docker runtime.
        devices = self.config.get_devices(arch=DeviceArch.ARM32V7, runtime="Preinstalled")
        self.device = devices[0]
        self.logs_uuid = None
        self.file_name = '{}-{}'.format(MINION, generate_random_value(5))

    def tearDown(self):
        self._delete_logs_upload()

    def _delete_logs_upload(self):
        self.logger.info('deleting uploaded logs')
        retry_count = 0
        retry_limit = 20
        try:
            while self.device.get_log_upload_status(self.logs_uuid).status == 'IN PROGRESS':
                if retry_count > retry_limit:
                    raise Exception('exceeded retry limit')
                time.sleep(5)
                retry_count += 1
            self.device.delete_uploaded_log_file(self.logs_uuid, retry_limit=0)
        except LogsUUIDNotFoundException as ex:
            self.logger.error('uuid not found or log is already deleted : {}'.format(ex))

    def test_logs_upload(self):
        logs_upload_request = LogsUploadRequest(LOG_SALT_MINION, self.file_name, override=True)
        self.logs_uuid = self.device.upload_log_file(logs_upload_request, retry_limit=0)
        self.assertTrue(self.logs_uuid)
        self.assertTrue(isinstance(self.logs_uuid, six.text_type))

    def test_logs_list_status_correct_optional_parameters(self):
        logs_upload_request = LogsUploadRequest(LOG_SALT_MINION, self.file_name, override=True)
        self.logs_uuid = self.device.upload_log_file(logs_upload_request, retry_limit=0)
        self.assertTrue(self.logs_uuid)
        status_list = self.device.list_uploaded_files_for_device(sort='filename',
                                                                 paginate=True, page_size=10, page_number=1,
                                                                 filter_by_filename='minion',
                                                                 filter_by_status=['COMPLETED', 'IN PROGRESS'])
        self.assertTrue(len(status_list) > 0)
        itr = [status for status in status_list if status.request_uuid == self.logs_uuid]
        self.assertTrue(len(itr) == 1)

    def test_logs_list_status_no_output_incorrect_optional_parameters(self):
        logs_upload_request = LogsUploadRequest(LOG_SALT_MINION, self.file_name, override=True)
        self.logs_uuid = self.device.upload_log_file(logs_upload_request, retry_limit=0)
        self.assertTrue(self.logs_uuid)
        status_list = self.device.list_uploaded_files_for_device(paginate=True, page_size=10, page_number=2,
                                                                 filter_by_filename='wrong_filename',
                                                                 filter_by_status=['FAILED'])
        self.assertTrue(len(status_list) == 0)

    def test_logs_status(self):
        logs_upload_request = LogsUploadRequest(LOG_SALT_MINION, self.file_name, override=True)
        self.logs_uuid = self.device.upload_log_file(logs_upload_request, retry_limit=0)
        self.assertTrue(self.logs_uuid)
        logs_upload_status = self.device.get_log_upload_status(self.logs_uuid, retry_limit=0)
        self.assertTrue(logs_upload_status.status in ['IN PROGRESS', 'FAILED', 'COMPLETED', 'CANCELLED'])
        self.assertTrue(len(logs_upload_status.error_message) == 0)
        self.assertTrue(logs_upload_status.filename == self.file_name)
        self.assertEqual(self.logs_uuid, logs_upload_status.request_uuid)

    def test_logs_file_download(self):
        logs_upload_request = LogsUploadRequest(LOG_SALT_MINION, self.file_name, override=True)
        self.logs_uuid = self.device.upload_log_file(logs_upload_request, retry_limit=0)
        self.assertTrue(self.logs_uuid)
        self._poll_for_status_complete(self.logs_uuid)
        download_url = self.device.download_log_file(self.logs_uuid, retry_limit=0)
        self.assertTrue(download_url)

    def _poll_for_status_complete(self, logs_uuid):
        while True:
            current_status = self.device.get_log_upload_status(logs_uuid).status
            if current_status == 'COMPLETED' or current_status == 'FAILED':
                break
            time.sleep(5)

    def test_logs_file_delete(self):
        logs_upload_request = LogsUploadRequest(LOG_SALT_MINION, self.file_name, override=True)
        self.logs_uuid = self.device.upload_log_file(logs_upload_request, retry_limit=0)
        self.assertTrue(self.logs_uuid)
        self._poll_for_status_complete(self.logs_uuid)
        delete_status = self.device.delete_uploaded_log_file(self.logs_uuid, retry_limit=0)
        self.assertTrue(delete_status)

    def test_logs_upload_cancel(self):
        logs_upload_request = LogsUploadRequest(LOG_SALT_MINION, self.file_name, override=True)
        self.logs_uuid = self.device.upload_log_file(logs_upload_request)
        self.assertTrue(self.logs_uuid)
        status = self.device.cancel_log_file_upload(self.logs_uuid)
        self.assertTrue(status)

    def test_shared_url(self):
        logs_upload_request = LogsUploadRequest(LOG_SALT_MINION, self.file_name, override=True)
        self.logs_uuid = self.device.upload_log_file(logs_upload_request, retry_limit=0)
        self.assertTrue(self.logs_uuid)
        self._poll_for_status_complete(self.logs_uuid)
        expiry_time = datetime.now() + timedelta(days=7)
        shared_url = self.device.create_shared_url(SharedURL(self.logs_uuid, expiry_time=expiry_time))
        self.assertTrue(shared_url)
        self.assertIsInstance(shared_url, SharedURL)
        self.assertIsNotNone(shared_url.url)
