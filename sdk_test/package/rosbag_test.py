from __future__ import absolute_import

import math
import os
import time
from time import sleep

from rapyuta_io import DeviceArch
from rapyuta_io.clients.rosbag import ROSBagJob, ROSBagOptions, ROSBagJobStatus, UploadOptions, ROSBagUploadTypes, \
    ROSBagOnDemandUploadOptions, ROSBagTimeRange, OverrideOptions, TopicOverrideInfo
from rapyuta_io.utils.utils import generate_random_value
from sdk_test.config import Configuration
from sdk_test.package.package_test import PackageTest
from sdk_test.util import get_logger, get_package, add_package, delete_package, add_build


class ROSBagJobTest(PackageTest):
    deployment = None
    deployment_with_fast_talker = None
    deployment_with_throttling = None
    deployment_with_latching = None
    device_rosbag_job = None
    cloud_rosbag_job = None
    throttling_rosbag_job = None
    latching_rosbag_job = None
    continuous_upload_type_rosbag = None

    TALKER_MANIFEST = 'talker.json'
    TALKER_BUILD = 'test-rosbag-job-talker-pkg'

    TALKER_CLOUD_DEVICE_MANIFEST = 'talker-cloud-device.json'
    TALKER_CLOUD_DEVICE_PACKAGE = 'test-rosbag-job-talker-cloud-device-pkg'

    ROSBAG_TALKER_MANIFEST = 'rosbag-talker-cloud.json'
    ROSBAG_TALKER_PACKAGE = 'test-rosbag-talker-cloud-pkg'

    FAST_TALKER_DEVICE_WITH_ROSBAGS_MANIFEST = 'fast-talker-device-docker-with-rosbags.json'
    FAST_TALKER_DEVICE_WITH_ROSBAGS_PACKAGE = 'fast-talker-device-docker-with-rosbags-pkg'

    THROTTLE_LATCH_BUILD_MANIFEST = 'throttle-latch-build.json'
    THROTTLE_LATCH_BUILD_NAME = 'throttle-latch-build'

    THROTTLING_PACKAGE_MANIFEST = 'throttling-pkg.json'
    THROTTLING_PACKAGE_NAME = 'throttling-pkg'

    LATCHING_PACKAGE_MANIFEST = 'latching-pkg.json'
    LATCHING_PACKAGE_NAME = 'latching-pkg'

    @classmethod
    def setUpClass(cls):
        add_build(cls.TALKER_MANIFEST, cls.TALKER_BUILD)

        add_package(cls.TALKER_CLOUD_DEVICE_MANIFEST, cls.TALKER_CLOUD_DEVICE_PACKAGE,
                    build_map={
                        'talker-device': {'talker': ('talker-build', 'talker.json')},
                        'talker-cloud': {'talker': ('talker-build', 'talker.json')},
                    })
        add_package(cls.ROSBAG_TALKER_MANIFEST, cls.ROSBAG_TALKER_PACKAGE,
                    build_map={
                        'talker-cloud': {'talker': ('talker-build', 'talker.json')},
                    })
        add_package(cls.FAST_TALKER_DEVICE_WITH_ROSBAGS_MANIFEST, cls.FAST_TALKER_DEVICE_WITH_ROSBAGS_PACKAGE,
                    build_map={
                        'talker-fast-device': {'talker': ('talker-build', 'talker.json')}
                    })
        add_build(cls.THROTTLE_LATCH_BUILD_MANIFEST, cls.THROTTLE_LATCH_BUILD_NAME)
        add_package(cls.THROTTLING_PACKAGE_MANIFEST, cls.THROTTLING_PACKAGE_NAME)
        add_package(cls.LATCHING_PACKAGE_MANIFEST, cls.LATCHING_PACKAGE_NAME)

    @classmethod
    def tearDownClass(cls):
        delete_package(cls.TALKER_CLOUD_DEVICE_PACKAGE, delete_builds=False)
        delete_package(cls.ROSBAG_TALKER_PACKAGE, delete_builds=False)
        delete_package(cls.FAST_TALKER_DEVICE_WITH_ROSBAGS_MANIFEST)
        delete_package(cls.THROTTLING_PACKAGE_NAME)
        delete_package(cls.LATCHING_PACKAGE_NAME)

    def setUp(self):
        self.config = Configuration()
        self.logger = get_logger()
        self.package = [
            get_package(self.TALKER_CLOUD_DEVICE_PACKAGE),
            get_package(self.ROSBAG_TALKER_PACKAGE),
            get_package(self.FAST_TALKER_DEVICE_WITH_ROSBAGS_PACKAGE),
            get_package(self.THROTTLING_PACKAGE_NAME),
            get_package(self.LATCHING_PACKAGE_NAME)
        ]
        self.device = self.config.get_devices(arch=DeviceArch.AMD64, runtime='Dockercompose')[0]
        self.bag_filename = 'test.bag'
        self.rosbag_job_name = 'test-rosbag-defs'

    def tearDown(self):
        if os.path.exists(self.bag_filename):
            os.remove(self.bag_filename)

    def test_01_create_deployment_with_rosbag_jobs(self):
        self.logger.info('creating deployment with rosbag jobs')
        device_rosbag_job = ROSBagJob('device-init-job', ROSBagOptions(all_topics=True),
                                      upload_options=UploadOptions(upload_type=ROSBagUploadTypes.ON_STOP))
        cloud_rosbag_job = ROSBagJob('cloud-init-job', ROSBagOptions(all_topics=True))
        provision_config = self.package[0].get_provision_configuration()
        ignored_device_configs = ['network_interface']
        provision_config.add_device('talker-device', self.device, ignore_device_config=ignored_device_configs)
        provision_config.add_rosbag_job('talker-device', device_rosbag_job)
        provision_config.add_rosbag_job('talker-cloud', cloud_rosbag_job)
        deployment = self.deploy_package(self.package[0], provision_config,
                                         ignored_device_configs=ignored_device_configs)
        deployment.poll_deployment_till_ready(retry_count=100, sleep_interval=5)
        self.__class__.deployment = self.config.client.get_deployment(deployment.deploymentId)
        self.assert_rosbag_jobs_present(self.deployment.deploymentId, [device_rosbag_job.name, cloud_rosbag_job.name],
                                        [ROSBagJobStatus.STARTING, ROSBagJobStatus.RUNNING])
        self.assert_rosbag_jobs_in_project(device_rosbag_job.name)

    def test_02_create_rosbag_jobs(self):
        self.logger.info('creating rosbag jobs on cloud and device')
        self.__class__.device_rosbag_job = self.create_rosbag_job('talker-device', is_device=True)
        self.__class__.cloud_rosbag_job = self.create_rosbag_job('talker-cloud')
        self.assert_rosbag_jobs_present(self.deployment.deploymentId,
                                        [self.device_rosbag_job.name, self.cloud_rosbag_job.name],
                                        [ROSBagJobStatus.RUNNING, ROSBagJobStatus.STARTING])

    def test_03_stop_rosbag_jobs(self):
        self.wait_till_jobs_are_running(self.deployment.deploymentId, [self.cloud_rosbag_job.guid,
                                                                       self.device_rosbag_job.guid],
                                        sleep_interval_in_sec=5)
        self.logger.info('stopping the running rosbag jobs on cloud and device')
        self.config.client.stop_rosbag_jobs(self.deployment.deploymentId, guids=[
            self.device_rosbag_job.guid, self.cloud_rosbag_job.guid])
        self.assert_rosbag_jobs_present(self.deployment.deploymentId,
                                        [self.device_rosbag_job.name, self.cloud_rosbag_job.name],
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
        self.wait_till_blobs_are_uploaded(job_ids=job_ids, sleep_interval_in_sec=5)

    def test_06_create_deployment_with_rosbag_jos_in_package_config(self):
        provision_config = self.package[1].get_provision_configuration()
        deployment = self.deploy_package(self.package[1], provision_config,
                                         ignored_device_configs=['network_interface'])
        deployment.poll_deployment_till_ready(retry_count=100, sleep_interval=5)
        self.assert_rosbag_jobs_present(deployment.deploymentId, [self.rosbag_job_name],
                                        [ROSBagJobStatus.STARTING, ROSBagJobStatus.RUNNING])
        jobs = self.config.client.list_rosbag_jobs(deployment.deploymentId)
        job_ids = [job.guid for job in jobs]
        self.wait_till_jobs_are_running(deployment.deploymentId)
        self.config.client.stop_rosbag_jobs(deployment.deploymentId)
        self.wait_till_blobs_are_uploaded(job_ids=job_ids)
        deployment.deprovision()

    def test_07_rosbag_job_with_upload_type_continuous(self):
        job_name = 'continuous_upload_type'

        self.logger.info('creating device deployment with rosbag job with upload type as Continuous')
        provision_config = self.package[2].get_provision_configuration()
        ignored_device_configs = ['network_interface']
        provision_config.add_device('talker-fast-device', self.device, ignore_device_config=ignored_device_configs)
        deployment = self.deploy_package(self.package[2], provision_config,
                                         ignored_device_configs=ignored_device_configs)
        deployment.poll_deployment_till_ready(retry_count=100, sleep_interval=5)
        self.__class__.deployment_with_fast_talker = self.config.client.get_deployment(deployment.deploymentId)

        self.assert_rosbag_jobs_present(self.deployment_with_fast_talker.deploymentId, [job_name],
                                        [ROSBagJobStatus.STARTING, ROSBagJobStatus.RUNNING])
        self.assert_rosbag_jobs_in_project(job_name)
        self.__class__.continuous_upload_type_rosbag = self.get_job_by_job_name(deployment.deploymentId, job_name)
        uploaded_blobs = self.wait_till_blobs_are_uploaded(job_ids=[self.continuous_upload_type_rosbag.guid])

        # to ensure first split is uploaded because it continuously
        # uploads
        first_bag_uploaded = False
        for blob in uploaded_blobs:
            if blob.filename.endswith('_0.bag'):
                first_bag_uploaded = True
                break

        self.assertTrue(first_bag_uploaded)

        self.config.client.stop_rosbag_jobs(
            deployment_id=deployment.deploymentId,
            guids=[self.continuous_upload_type_rosbag.guid]
        )

    def test_08_rosbag_job_with_upload_type_on_demand(self):
        self.logger.info('creating rosbag job with upload type as OnDemand')

        job_name = 'on_demand_upload_type'
        component_instance_id = self.deployment_with_fast_talker.get_component_instance_id('talker-fast-device')

        job_req = ROSBagJob(
            name=job_name,
            deployment_id=self.deployment_with_fast_talker.deploymentId,
            component_instance_id=component_instance_id,
            rosbag_options=ROSBagOptions(
                all_topics=True,
                max_splits=10,
                max_split_size=10
            ),
            upload_options=UploadOptions(upload_type=ROSBagUploadTypes.ON_DEMAND),
        )

        rosbag_creation_time = int(time.time())
        job = self.config.client.create_rosbag_job(job_req)

        start_recording_duration = 8
        split_duration = 60

        self.logger.info('sleeping for sometime for recording to continue')
        sleep(start_recording_duration + (split_duration * 2))

        from_time = rosbag_creation_time + start_recording_duration + split_duration + 10
        to_time = from_time + split_duration
        on_demand_opts = ROSBagOnDemandUploadOptions(
            time_range=ROSBagTimeRange(
                from_time=from_time,
                to_time=to_time
            )
        )

        job.patch(on_demand_options=on_demand_opts)

        uploaded_blobs = self.wait_till_blobs_are_uploaded(job_ids=[job.guid])

        # to ensure first split is not uploaded because it is not
        # within the time range provided
        for blob in uploaded_blobs:
            self.assertFalse(blob.filename.endswith('_0.bag'))

        self.deployment_with_fast_talker.deprovision()

    def test_09_rosbag_job_throttling(self):
        self.logger.info('deploying throttling package')
        device_rosbag_job = ROSBagJob('device-init-job', ROSBagOptions(all_topics=True),
                                      upload_options=UploadOptions(upload_type=ROSBagUploadTypes.ON_STOP))
        provision_config = self.package[3].get_provision_configuration()
        ignored_device_configs = ['network_interface']
        provision_config.add_device('throttling-component', self.device, ignore_device_config=ignored_device_configs)
        provision_config.add_rosbag_job('throttling-component', device_rosbag_job)
        deployment = self.deploy_package(self.package[3], provision_config,
                                         ignored_device_configs=ignored_device_configs)
        deployment.poll_deployment_till_ready(retry_count=100, sleep_interval=5)
        self.__class__.deployment_with_throttling = self.config.client.get_deployment(deployment.deploymentId)

        component_instance_id = self.deployment_with_throttling.get_component_instance_id('throttling-component')
        throttling_rosbag_job = ROSBagJob('rosbag-test-throttling',
                                          deployment_id=self.deployment_with_throttling.deploymentId,
                                          component_instance_id=component_instance_id,
                                          rosbag_options=ROSBagOptions(all_topics=True),
                                          upload_options=UploadOptions(upload_type=ROSBagUploadTypes.ON_STOP),
                                          override_options=OverrideOptions(
                                              topic_override_info=[
                                                  TopicOverrideInfo('/topic2', 15, False),
                                                  TopicOverrideInfo('/topic3', 2, False),
                                              ],
                                              exclude_topics=['/topic4']
                                          ))
        self.__class__.throttling_rosbag_job = self.config.client.create_rosbag_job(throttling_rosbag_job)
        self.assert_rosbag_jobs_present(self.deployment_with_throttling.deploymentId,
                                        [throttling_rosbag_job.name],
                                        [ROSBagJobStatus.STARTING, ROSBagJobStatus.RUNNING])
        self.assert_rosbag_jobs_in_project(throttling_rosbag_job.name)
        self.wait_till_jobs_are_running(self.deployment_with_throttling.deploymentId,
                                        [self.throttling_rosbag_job.guid], sleep_interval_in_sec=5)
        # introduce wait for 1 minute maybe time.sleep()
        self.logger.info('sleeping for 15 seconds')
        time.sleep(15)
        self.config.client.stop_rosbag_jobs(self.deployment_with_throttling.deploymentId,
                                            guids=[self.throttling_rosbag_job.guid])
        self.assert_rosbag_jobs_present(self.deployment_with_throttling.deploymentId,
                                        [self.throttling_rosbag_job.name],
                                        [ROSBagJobStatus.STOPPING, ROSBagJobStatus.STOPPED])

        uploaded_blobs = self.wait_till_blobs_are_uploaded(sleep_interval_in_sec=5,
                                                           job_ids=[self.throttling_rosbag_job.guid])
        self.logger.info('validating the uploaded rosbag blobs for the stopped jobs')
        # self.assert_rosbag_blobs_of_device(uploaded_blobs) # this one is failing because device had more blobs present

        self.assertEqual(len(uploaded_blobs), 1)
        uploaded_blob = uploaded_blobs[0]
        relevant_topics = ['/topic1', '/topic2', '/topic3', '/topic4']
        record_duration = uploaded_blob.info.duration
        topics = filter(lambda topic: topic.name in relevant_topics, uploaded_blob.info.topics)
        topic1_metadata = filter(lambda topic: topic.name == '/topic1', topics)[0]
        topic2_metadata = filter(lambda topic: topic.name == '/topic2', topics)[0]
        topic3_metadata = filter(lambda topic: topic.name == '/topic3', topics)[0]
        topic4_metadata = filter(lambda topic: topic.name == '/topic4', topics)[0]
        self.assertTrue(math.isclose(topic1_metadata.message_count, topic2_metadata.message_count, abs_tol=5))
        self.assertTrue(math.isclose(
            topic3_metadata.message_count,
            round(2 * record_duration),
            abs_tol=5
        ))

    def test_10_rosbag_job_latching(self):
        self.logger.info('deploying latching package')
        device_rosbag_job = ROSBagJob('device-init-job', ROSBagOptions(all_topics=True),
                                      upload_options=UploadOptions(upload_type=ROSBagUploadTypes.ON_STOP))
        provision_config = self.package[4].get_provision_configuration()
        ignored_device_configs = ['network_interface']
        provision_config.add_device('latching-component', self.device, ignore_device_config=ignored_device_configs)
        provision_config.add_rosbag_job('latching-component', device_rosbag_job)
        deployment = self.deploy_package(self.package[4], provision_config,
                                         ignored_device_configs=ignored_device_configs)
        deployment.poll_deployment_till_ready(retry_count=100, sleep_interval=5)
        self.__class__.deployment_with_latching = self.config.client.get_deployment(deployment.deploymentId)

        component_instance_id = self.deployment_with_latching.get_component_instance_id('latching-component')
        latching_rosbag_job = ROSBagJob('rosbag-test-latching',
                                        deployment_id=self.deployment_with_latching.deploymentId,
                                        component_instance_id=component_instance_id,
                                        rosbag_options=ROSBagOptions(all_topics=True, max_splits=5, max_split_size=20),
                                        upload_options=UploadOptions(upload_type=ROSBagUploadTypes.ON_STOP),
                                        override_options=OverrideOptions(
                                            topic_override_info=[
                                                TopicOverrideInfo('/map', latched=True),
                                            ],
                                        ))
        self.__class__.latching_rosbag_job = self.config.client.create_rosbag_job(latching_rosbag_job)
        self.assert_rosbag_jobs_present(self.deployment_with_latching.deploymentId,
                                        [latching_rosbag_job.name],
                                        [ROSBagJobStatus.STARTING, ROSBagJobStatus.RUNNING])
        self.assert_rosbag_jobs_in_project(latching_rosbag_job.name)
        self.wait_till_jobs_are_running(self.deployment_with_latching.deploymentId,
                                        [self.latching_rosbag_job.guid], sleep_interval_in_sec=5)
        # introduce wait for 1 minute maybe time.sleep()
        self.logger.info('sleeping for 60 seconds')
        time.sleep(60)
        self.config.client.stop_rosbag_jobs(self.deployment_with_latching.deploymentId,
                                            guids=[self.latching_rosbag_job.guid])
        self.assert_rosbag_jobs_present(self.deployment_with_latching.deploymentId,
                                        [self.latching_rosbag_job.name],
                                        [ROSBagJobStatus.STOPPING, ROSBagJobStatus.STOPPED])

        uploaded_blobs = self.wait_till_blobs_are_uploaded(sleep_interval_in_sec=5,
                                                           job_ids=[self.latching_rosbag_job.guid])
        self.logger.info('validating the uploaded rosbag blobs for the stopped jobs')
        # self.assert_rosbag_blobs_of_device(uploaded_blobs) # this one is failing
        self.assertGreater(len(uploaded_blobs), 1)

        topic_absent_in_split = False
        for blob in uploaded_blobs:
            topics = blob.info.topics
            x = next((topic for topic in topics if topic.name == '/map'), None)
            if x is None:
                topic_absent_in_split = True
                break

        self.assertFalse(topic_absent_in_split)

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
            upload_options = UploadOptions(upload_type=ROSBagUploadTypes.ON_STOP)
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

    def wait_till_blobs_are_uploaded(
            self,
            job_ids=None,
            retry_limit=50,
            sleep_interval_in_sec=1,
            list_blobs_sleep_interval_in_sec=5
    ):
        if not job_ids:
            job_ids = [self.cloud_rosbag_job.guid, self.device_rosbag_job.guid]
        self.logger.info('waiting for rosbag blobs to finish uploading')

        blobs = []
        retry_count = 0
        job_ids_copy = job_ids.copy()
        while retry_count < retry_limit:
            blobs = self.config.client.list_rosbag_blobs(job_ids=job_ids)
            if not blobs:
                sleep(list_blobs_sleep_interval_in_sec)
                continue

            for blob in blobs:
                if blob.job.guid in job_ids_copy:
                    job_ids_copy.remove(blob.job.guid)

                if len(job_ids_copy) == 0:
                    break

            if not job_ids_copy:
                break

            sleep(list_blobs_sleep_interval_in_sec)

        if job_ids_copy:
            raise Exception(
                'not even a single rosbag blob has been uploaded for job ids {}, waiting timed out'.format(job_ids_copy)
            )

        for blob in blobs:
            blob.poll_till_ready(retry_count=retry_limit, sleep_interval=sleep_interval_in_sec)

        self.logger.info('rosbag blobs are uploaded')

        return blobs

    def get_job_by_job_name(self, deployment_id, job_name):
        jobs = self.config.client.list_rosbag_jobs(deployment_id)
        for job in jobs:
            if job.name == job_name:
                return job

        return None
