from __future__ import absolute_import

import os
from time import sleep

from rapyuta_io import ROSDistro, DeviceArch
from rapyuta_io.clients.rosbag import ROSBagJob, ROSBagOptions, ROSBagJobStatus, ROSBagBlobStatus, \
    UploadOptions
from rapyuta_io.utils.utils import generate_random_value
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, get_package, add_package, delete_package, \
    add_cloud_routed_network, delete_routed_network, get_routed_network, add_build


class ROSBagJobTest(PackageTest):
    deployment = None
    device_rosbag_job = None
    cloud_rosbag_job = None

    TALKER_MANIFEST = 'talker.json'
    TALKER_BUILD = 'test-rosbag-job-talker-pkg'

    TALKER_CLOUD_DEVICE_MANIFEST = 'talker-cloud-device.json'
    TALKER_CLOUD_DEVICE_PACKAGE = 'test-rosbag-job-talker-cloud-device-pkg'

    ROSBAG_TALKER_MANIFEST = 'rosbag-talker-cloud.json'
    ROSBAG_TALKER_PACKAGE = 'test-rosbag-talker-cloud-pkg'

    @classmethod
    def setUpClass(cls):
        add_build(cls.TALKER_MANIFEST, cls.TALKER_BUILD)
        add_package(cls.TALKER_CLOUD_DEVICE_MANIFEST, cls.TALKER_CLOUD_DEVICE_PACKAGE,
        build_map={
            'talker-device': {'talker': ('talker-build', 'talker.json')},
            'talker-cloud': {'talker': ('talker-build', 'talker.json')},
        })
        add_package(cls.ROSBAG_TALKER_MANIFEST, cls.ROSBAG_TALKER_PACKAGE, build_map={
            'talker-cloud': {'talker': ('talker-build', 'talker.json')},
        })
        add_cloud_routed_network('rosbag_cloud_network', ros_distro=ROSDistro.MELODIC)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.TALKER_CLOUD_DEVICE_PACKAGE, delete_builds=False)
        delete_package(cls.ROSBAG_TALKER_PACKAGE)
        delete_routed_network('rosbag_cloud_network')

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.package = [get_package(self.TALKER_CLOUD_DEVICE_PACKAGE), get_package(self.ROSBAG_TALKER_PACKAGE)]
        self.routed_network = get_routed_network('rosbag_cloud_network')
        self.device = self.config.get_devices(arch=DeviceArch.AMD64, runtime='Dockercompose')[0]
        self.bag_filename = 'test.bag'
        self.rosbag_job_name = 'test-rosbag-defs'

    def tearDown(self):
        if os.path.exists(self.bag_filename):
            os.remove(self.bag_filename)

    def test_01_create_deployment_with_rosbag_jobs(self):
        self.logger.info('creating deployment with rosbag jobs')
        device_rosbag_job = ROSBagJob('device-init-job', ROSBagOptions(all_topics=True),
                                      upload_options=UploadOptions())
        cloud_rosbag_job = ROSBagJob('cloud-init-job', ROSBagOptions(all_topics=True))
        provision_config = self.package[0].get_provision_configuration()
        provision_config.add_routed_network(self.routed_network)
        ignored_device_configs = ['network_interface']
        provision_config.add_device('talker-device', self.device, ignore_device_config=ignored_device_configs)
        provision_config.add_rosbag_job('talker-device', device_rosbag_job)
        provision_config.add_rosbag_job('talker-cloud', cloud_rosbag_job)
        deployment = self.deploy_package(self.package[0], provision_config, ignored_device_configs=ignored_device_configs)
        deployment.poll_deployment_till_ready(retry_count=100, sleep_interval=5)
        self.__class__.deployment = self.config.client.get_deployment(deployment.deploymentId)
        self.assert_rosbag_jobs_present(self.deployment.deploymentId, [device_rosbag_job.name, cloud_rosbag_job.name],
                                        [ROSBagJobStatus.STARTING, ROSBagJobStatus.RUNNING])
        self.assert_rosbag_jobs_in_project(device_rosbag_job.name)

    def test_02_create_rosbag_jobs(self):
        self.logger.info('creating rosbag jobs on cloud and device')
        self.__class__.device_rosbag_job = self.create_rosbag_job('talker-device', is_device=True)
        self.__class__.cloud_rosbag_job = self.create_rosbag_job('talker-cloud')
        self.assert_rosbag_jobs_present(self.deployment.deploymentId, [self.device_rosbag_job.name, self.cloud_rosbag_job.name],
                                        [ROSBagJobStatus.RUNNING, ROSBagJobStatus.STARTING])

    def test_03_stop_rosbag_jobs(self):
        self.wait_till_jobs_are_running(self.deployment.deploymentId, [self.cloud_rosbag_job.guid,
                                                              self.device_rosbag_job.guid], sleep_interval_in_sec=5)
        self.logger.info('stopping the running rosbag jobs on cloud and device')
        self.config.client.stop_rosbag_jobs(self.deployment.deploymentId, guids=[
            self.device_rosbag_job.guid, self.cloud_rosbag_job.guid])
        self.assert_rosbag_jobs_present(self.deployment.deploymentId, [self.device_rosbag_job.name, self.cloud_rosbag_job.name],
                                        [ROSBagJobStatus.STOPPING, ROSBagJobStatus.STOPPED])

    def test_04_rosbag_blobs(self):
        blobs = self.wait_till_blobs_are_uploaded(sleep_interval_in_sec=5)
        self.logger.info('validating the uploaded rosbag blobs for the stopped jobs')
        self.assert_rosbag_blobs_of_device(blobs)
        self.assert_rosbag_blobs(blobs)

    def test_05_auto_stop_rosbag_jobs_on_deprovision(self):
        jobs = self.config.client.list_rosbag_jobs(deployment_id=self.deployment.deploymentId,
                                                   statuses=[ROSBagJobStatus.RUNNING])
        job_ids = list(map(lambda job: job.guid, jobs))
        self.assertEqual(2, len(jobs))
        init_job_names = list(map(lambda job: job.name, jobs))
        self.logger.info('deprovisioning deployment with running rosbag jobs')
        self.deployment.deprovision()
        self.assert_rosbag_jobs_present(self.deployment.deploymentId, init_job_names,
                                        [ROSBagJobStatus.STOPPING, ROSBagJobStatus.STOPPED])
        self.wait_till_blobs_are_uploaded(jobs=job_ids, sleep_interval_in_sec=5)

    def test_06_create_deployment_with_rosbag_jos_in_package_config(self):
        provision_config = self.package[1].get_provision_configuration()
        provision_config.add_routed_network(self.routed_network)
        deployment = self.deploy_package(self.package[1], provision_config,
                                         ignored_device_configs=['network_interface'])
        deployment.poll_deployment_till_ready(retry_count=100, sleep_interval=5)
        self.assert_rosbag_jobs_present(deployment.deploymentId, [self.rosbag_job_name],
                                        [ROSBagJobStatus.STARTING, ROSBagJobStatus.RUNNING])
        jobs = self.config.client.list_rosbag_jobs(deployment.deploymentId)
        job_ids = [job.guid for job in jobs]
        self.wait_till_jobs_are_running(deployment.deploymentId)
        self.config.client.stop_rosbag_jobs(deployment.deploymentId)
        self.wait_till_blobs_are_uploaded(jobs=job_ids)
        deployment.deprovision()

    def assert_rosbag_jobs_present(self, deployment_id, job_names, statuses=None):
        self.logger.info('checking jobs ')
        jobs_list = self.config.client.list_rosbag_jobs(deployment_id)
        jobs = [x for x in jobs_list if x.name in job_names]
        self.assertNotEqual(len(jobs), 0, 'no jobs were started')
        if statuses:
            for job in jobs:
                self.assertTrue(job.status in statuses)

    def assert_rosbag_jobs_in_project(self, job_name):
        self.logger.info('checking jobs in project ')
        jobs_list = self.config.client.list_rosbag_jobs_in_project([self.device.deviceId])
        self.assertEqual((job_name in [job.name for job in jobs_list]), True)

    def assert_rosbag_blobs(self, blobs):
        for blob in blobs:
            self.config.client.download_rosbag_blob(blob.guid, filename=self.bag_filename)
            self.assert_bag_file_exists()
            self.config.client.delete_rosbag_blob(blob.guid)
            self.assert_rosbag_blob_deleted(blob.guid)

    def assert_rosbag_blobs_of_device(self, blobs):
        self.logger.info('checking if the blobs fetched based on device id are present in the uploaded blobs')
        blobs_based_on_device_id = self.config.client.list_rosbag_blobs(device_ids=[self.device.deviceId])
        guids_based_on_device_id = [blob.guid for blob in blobs_based_on_device_id]
        all_guids = [blob.guid for blob in blobs]
        self.assertEqual(all(guid in all_guids for guid in guids_based_on_device_id), True)

    def assert_bag_file_exists(self):
        self.assertTrue(os.path.exists(self.bag_filename))

    def assert_rosbag_blob_deleted(self, blob_guid):
        blobs = self.config.client.list_rosbag_blobs(guids=[blob_guid])
        self.assertEqual(len(blobs), 0)

    def create_rosbag_job(self, component_name, is_device=False):
        self.logger.info('creating rosbag job for {} component'.format(component_name))
        rosbag_job_name = generate_random_value()
        upload_options = None
        component_instance_id = self.deployment.get_component_instance_id(component_name)
        if is_device:
            upload_options = UploadOptions()
        rosbag_job = ROSBagJob(rosbag_job_name, ROSBagOptions(all_topics=True),
                               deployment_id=self.deployment.deploymentId,
                               component_instance_id=component_instance_id,
                               upload_options=upload_options)
        return self.config.client.create_rosbag_job(rosbag_job)

    def wait_till_jobs_are_running(self, deployment_id, guids=None, retry_limit=50, sleep_interval_in_sec=1):
        self.logger.info('waiting for rosbag jobs to start running')
        retry_count = 0
        while retry_count < retry_limit:
            jobs = self.config.client.list_rosbag_jobs(deployment_id,
                                                       guids=guids)
            running_jobs = [job for job in jobs if job.status == ROSBagJobStatus.RUNNING]
            if len(jobs) == len(running_jobs):
                self.logger.info('rosbag jobs are running')
                return
            sleep(sleep_interval_in_sec)
            retry_count += 1

        raise Exception('rosbag jobs are not running, waiting timed out')

    def wait_till_blobs_are_uploaded(self, jobs=None, retry_limit=50, sleep_interval_in_sec=1):
        if not jobs:
            jobs = [self.cloud_rosbag_job.guid, self.device_rosbag_job.guid]
        self.logger.info('waiting for rosbag blobs to finish uploading')
        blobs = self.config.client.list_rosbag_blobs(job_ids=jobs)
        for blob in blobs:
            blob.poll_till_ready(retry_count=retry_limit, sleep_interval=sleep_interval_in_sec)
        self.logger.info('rosbag blobs are uploaded')
        return blobs
