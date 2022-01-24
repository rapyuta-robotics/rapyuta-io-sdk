# Changelog
**Note:** If you're creating a release, ensure VERSION has been bumped in `setup.py`.

## [0.39.0] - 2022-01-19
### Fixed
- Added validation for component parameter types in ProvisionConfig
### Changed
- Deprecated: `Device.metrics()`, `Device.subscribe_metric()`, `Device.unsubscribe_metric()`
- Deprecated: Local communication pkg removal

## [0.38.0] - 2021-12-29
### Fixed
- Added backward compatibility fixes to persistent volumes.
- Added mount path device volume feature

## [0.37.0] - 2021-12-08
### Fixed
- Docstring fixes for create_rosbag_jobs, query_metrics and RosbagJob class.
### Added
- Support for adding user to a project, removing user from a project.

## [0.36.0] - 2021-11-17
### Fixed
- Fixed validations for secret name length and pattern.
- Added isInstance validation for create methods of build, project, secret and rosbag job.
### Added
- Added rosbag blob object delete method plus docstring fixes for other object delete methods.
- `retry_upload()` and `poll_blob_till_ready()` methods to `ROSBagBlob`

## [0.35.0] - 2021-10-27
### Added
- Support for subpath corresponding to specific executable while mounting volumes

## [0.34.0] - 2021-10-24
### Added
- Support for OKD4 cluster


## [0.33.0] - 2021-09-14
### Fixed
- Fixed delete method inconsistency for native and routed network.
- Documentation for poll native network and poll routed network.

## [0.32.0] - 2021-08-25
### Fixed
- Fixed variables and parameters of Project and User class.
- Fixed broken link for deployment error codes used in poll deployment.
- Fixed rosbag job definitions not getting picked while provisioning.
### Added
- Support for get authenticated user details
- Support to filter by name and version in get all packages.
- Support for printing the bash command required to onboard a device

## [0.31.0] - 2021-08-11
### Added
- Support for device native network

## [0.30.0] - 2021-08-04
### Added
- Support for ROS noetic
- Support for querying metrics

## [0.29.0] - 2021-07-20
### Added
- Added device onboard features in SDK
- Added device upgrade, support for selecting python version during device creation

## [0.28.0] - 2021-07-07
- Added concurrency to sdk tests, support for running selected test files, uploading coverage file, fixed build timeouts happening in tests.

## [0.27.0] - 2021-06-23
### Added
- Added trigger-name tag-name to create build

## [0.26.1] - 2021-06-09
### Changed
- Updated sdkdocs to use Pypi for installation

## [0.26.0] - 2021-05-26
### Fixed
- Fixed the X_SMALL limits configuration of native network, sdk documentation of native networks, builds, rio_client
### Added
- Support for `refresh()` and `is_partial` + multiple fixes to sdkdocs
- Added implementation of delete static routes in core api client.
- Added searching, filtering, sorting and pagination facilities in device list logs.


## [0.25.0] - 2021-05-12
### Added
- Added support for additional cloud volume disk capacity sizes in SDK.
- Added check to not allow component alias name set up without user knowledge
- Added support for setting ros namespace for native network deployments

### Changed
- Removed references of Include Packages in SDK.


## [0.24.0] - 2021-04-21
### Added
- Added support for device id in listing rosbag jobs and blobs
- Add dockerfile to upload to PyPi.

## [0.23.0] - 2021-04-07
### Added
- Introduced build update feature in SDK
### Fixed
- `create_volume_instance()` sdkdocs example

## [0.22.1] - 2021-03-24
- Fixed build trigger from failing

## [0.22.0] - 2021-03-24
- Introduced trigger name and tag name parameters for builds in SDK
- Introduced sizing limits for cloud routed network in SDK


## [0.21.0] - 2021-03-16
### Added
- Added support for Native Network in SDK

## [0.20.2] - 2021-03-03
### Changed
- sdkdocs theme, documentation fixes

## [0.20.1] - 2021-02-20
### Fixed
- Fixed Limits in Test package manifest

## [0.20.0] - 2021-02-17
### Added
- Added support for Rosbag on Device

## [0.19.1] - 2021-02-02
### Added
- Integration test for device id in list deployment.

## [0.19.0] - 2021-01-13
### Added
- Added device id as filter argument in deployment list api.
- Added support for both Python 3.9 and Python 2.7

## [0.18.1] - 2020-12-30
### Fixed
- Fixed retry_limit parameter in ProvisionClient
- Fixed error message when re-using same provision config for provisioning

## [0.18.0] - 2020-12-09
### Fixed
- docs not working

## [0.18.0] - 2020-12-09
### Added
- Added support for Push/Pull Secrets for Builds
- Added support for creating direct links for Log files
- Added Project, Secret and Auth token generation support
### Fixed
- Added retries for calls that result in Internal Server Error.
### Changed
- Revamped the Integration Tests to automate some parts and run cases in isolation.

## [0.17.2] - 2020-11-4
### Added
- support for rosbags

## [0.17.1] - 2020-10-21
### Fixed
- Added a method in sdk to fetch static route using user's url prefix as a query param.

## [0.17.0] - 2020-09-22
### Fixed
- Added support for both pwd and cwd for creating command to be executed on device.
### Added
- Added delete package functionality in sdk.
- Added support for uploading and downloading binary configurations files

## [0.16.1] - 2020-08-26
### Fixed
- sdkdocs docker build failing because python2 no longer part of alpine

##[0.16.0] - 2020-08-26
### Added
- Added BuildEndpoints and BuildOperation SDK methods
- Added integration test for inbound incoming scoped and targeted

##[0.15.0] - 2020-07-29
### Added
- Added network interface in routed network sdk method
### Fixed
- Fixed integration test for log upload

##[0.14.0] - 2020-05-29
### Added
- Added routed network SDK methods

## [0.13.0] - 2020-03-25
### Added
- Added static routes SDK methods

## [0.12.0] - 2020-02-18
### Fixed
- Fixed typo in sdk docs.
### Added
- Added Wireless option to the SDK.

## [0.11.0] - 2020-02-05
### Added
- Add method to add restart policy for component

## [0.10.2] - 2020-01-16
### Fixed
- sdkdocs: add example for ignore_device_config in add_device function
- _poll_deployment_or_volume_till_ready raises DeploymentNotRunningException in invalid cases

## [0.10.1] - 2019-12-19
### Fixed
- sdkdocs: not compiling due to missing rapyuta_io dependency (futures)

## [0.10.0] - 2019-12-18
### Added
- Methods to work with parameters

## [0.9.1] - 2019-11-27
### Added
- Added deployment status object attribute to DeploymentNotRunningException class
### Fixed
- Automated start and stop of roscore for cloud_scoped_targeted_test and topic_test
- Fixed scoped-targeted.json to clone io_test_scenarios
### Changed
- Updated README for mulitple pinpong package issue

## [0.9.0] - 2019-11-06
### Fixed
- Update sdk test to handle conflict error propagation
- Refactor the get_deployments function in device class
### Added
- Added functionality to propagate error from rest_client
- Added packageVersion  field to Package class
- bind to multiple interfaces of local communication broker as dependent deployment
- Added functionality to create package from manifest file and manifest dict
### Changed
- Rename mission to selection api

## [0.8.0] - 2019-10-15
### Added
- Added support for fields, tags override in subscribe topics api
- Added support for logs API

## [0.7.0] - 2019-09-25
### Added
- Added suuport for system metrics APIs in sdk
- Add function to get deployments for a device

## [0.6.0] - 2019-09-10
### Fixed
- Failing integration test: invalid network endpoint check
### Added
- Added phase filtering for deployment list API
- Integration test for local communication broker

## [0.5.0] - 2019-07-11
### Added
- QoS changes for ROS topics

## [0.4.0] - 2019-03-14
### Fixed
- default settings for client should point to ga cluster

## [0.3.2] - 2019-01-29
### Fixed
- Documentation for DeviceArch class
- Fix setup.py version... again

## [0.3.1] - 2019-01-29
### Fixed
- Fix setup.py version

## [0.3.0] - 2019-01-29
### Added
- Support for device filter-by-architecture
- error_code and error_message for device class
- Unit tests

## [0.2.0] - 2018-10-04
### Added
- Integration Test
- Enum for deployment phase and status
- Blocking method to wait for deployment

### Removed
- Poll last operation method from deployment class

## [0.1.0] - 2018-09-05
### Added
- First version of rio-sdk
- Classes for Package, Deployment, Volumes
