from __future__ import absolute_import

import json
import logging
import os
from time import sleep

from rapyuta_io import Build, BuildOptions, CatkinOption, SimulationOptions, ROSDistro
from rapyuta_io.clients.model import Command
from rapyuta_io.clients.native_network import NativeNetwork
from rapyuta_io.clients.package import Runtime
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import get_api_response_data
from sdk_test.config import Configuration

_JSON_PATH = ''
_PACKAGE_MAP = dict()
_BUILD_MAP = dict()
_ROUTED_NETWORK_MAP = dict()
_NATIVE_NETWORK_MAP = dict()


def get_manifest_file(manifest_name, manifest_type):
    """
    get_manifest_file generates the filepath relative to the current executable for the Manifest (JSON files).

    manifest_name: Name of the manifest file (Package/Build) with the extension
    manifest_type: Type of the manifest. Possible Values: Package, Build
    """
    global _JSON_PATH
    if _JSON_PATH == '':
        dir_path = os.path.dirname(os.path.realpath(__file__))
        _JSON_PATH = os.path.join(dir_path, 'jsons')

    if manifest_type == 'Package':
        path = os.path.join(_JSON_PATH, 'packages')
    elif manifest_type == 'Build':
        path = os.path.join(_JSON_PATH, 'builds')
    else:
        raise Exception('Invalid manifest type')

    return '{}/{}'.format(path, manifest_name)


def get_build(build_name):
    """
    get_build is the utility function to fetch the Build using its *Manifest* name. The latest Build object is fetched
    using the API.

    build_name: Name of the Build Manifest (JSON file) without the extension
    """
    global _BUILD_MAP
    config = Configuration()
    build_id = _BUILD_MAP[build_name]['guid']
    return config.client.get_build(build_id)


def _get_build_from_manifest(manifest):
    """
    _get_build_from_manifest translates the JSON manifest for Build into the Build Object that can be used to interact
    with the API.

    It supports partial manifests, i.e., the value of Secret field only needs to have the type of the Secret instead of
    the actual Secret GUID. It will populate the fields based on the actual Secret GUID automatically. For more
    information check the `create_secrets` and `get_secret` method on the Configuration.
    Possible types of Secret: git, docker.

    manifest: Parsed JSON payload in the form of Dictionary with all the required fields for Build. Check the Golang
    Model for reference.
    """
    config = Configuration()
    secret_guid = ''
    simulation_options = None
    build_options = None

    if manifest.get('secret') is not None:
        secret = config.get_secret(manifest.get('secret'))
        secret_guid = secret.guid

    if manifest.get('buildOptions') is not None:
        catkin_options = []
        for opt in manifest['buildOptions']['catkinOptions']:
            catkin_options.append(CatkinOption(
                rosPkgs=opt.get('rosPkgs'),
                cmakeArgs=opt.get('cmakeArgs'),
                makeArgs=opt.get('makeArgs'),
                blacklist=opt.get('blacklist'),
                catkinMakeArgs=opt.get('catkinMakeArgs')
            ))
        build_options = BuildOptions(catkin_options)

    if manifest.get('simulationOptions') is not None:
        value = manifest['simulationOptions']['simulation']
        simulation_options = SimulationOptions(value)

    return Build(
        branch=manifest.get('branch', ''),
        buildName=manifest['buildName'],
        strategyType=manifest['strategyType'],
        repository=manifest['repository'],
        architecture=manifest['architecture'],
        rosDistro=manifest.get('rosDistro', ''),
        isRos=manifest.get('isRos', False),
        contextDir=manifest.get('contextDir', ''),
        dockerFilePath=manifest.get('dockerFilePath', ''),
        secret=secret_guid,
        simulationOptions=simulation_options,
        buildOptions=build_options,
    )


def add_build(manifest_name, build_name=None, wait=True, modify_func=None):
    """
    add_build is a utility function that creates the Build from the JSON manifest.

    manifest_name: Name of the Build Manifest (JSON file) with the extension
    [optional] build_name: Name of the build
    [optional] wait: Flag to enable waiting for the Build to complete
    Default: True
    [optional] modify_func: This utility provides a hook function that gets called after loading and parsing the
    Manifest. It can be used to perform arbitrary runtime manipulations on the Payload. Only use it for advanced use
    cases that are not directly supported by the utility directly.
    """
    global _BUILD_MAP
    config = Configuration()
    logger = get_logger()
    path = get_manifest_file(manifest_name, 'Build')
    with open(path, 'r') as f:
        build_payload = json.load(f)
    if build_name is not None:
        build_payload['buildName'] = build_name

    if modify_func is not None:
        modify_func(build_payload)

    logger.info('Creating the build: %s', build_name)
    build = config.client.create_build(_get_build_from_manifest(build_payload))
    _BUILD_MAP[build_name] = build
    if wait:
        logger.debug('Waiting for the build %s to complete', build_name)
        build.poll_build_till_ready(sleep_interval=10)
    return build


def delete_build(build_name):
    """
    delete_build is a utility function that deletes the Build using the Manifest Name. This function is idempotent and
    it can be safely called multiple times for the same Build.

    build_name: Name of the Build Manifest (JSON file) without the extension
    """
    global _BUILD_MAP
    if build_name in _BUILD_MAP:
        _BUILD_MAP[build_name].delete()
        del _BUILD_MAP[build_name]


def get_package(package_name):
    """
    get_package is the utility function to fetch the Package using its *Manifest* name. The latest Package object is
    fetched using the API.

    package_name: Name of the Package Manifest (JSON file) without the extension
    """
    global _PACKAGE_MAP
    config = Configuration()
    package_id = _PACKAGE_MAP[package_name]['packageId']
    return config.client.get_package(package_id)


def add_package(manifest_name, package_name=None, wait=True, build_map=None, modify_func=None):
    """
    add_package is a utility function to create new packages using there *Manifest* name. It loads the Manifest file and
    creates the Package based on it. It supports partials, i.e., Package templates without Build information can also be
    used. You can use the build_map option to provide Builds information at runtime.

    manifest_name: Name of the Package Manifest (JSON file) with the extension
    [optional] package_name: Name of the Package
    [optional] wait: Flag to enable waiting for all the Builds to complete for the Package. It is compatible with older
    and newer package versions.
    Default: True
    [optional] build_map: Build Map can be used to inject Builds information (like BuildGUID) at runtime. It accepts a
    dictionary that maps Components to Executable-BuildGUID Map.
    Example: {
        "comp1": {
            "exec1": "build-guid"
        }
    }
    [optional] modify_func: This utility provides a hook function that gets called after loading and parsing the
    Manifest. It can be used to perform arbitrary runtime manipulations on the Manifest. Only use it for advanced use
    cases that are not directly supported by the utility directly.
    """
    global _PACKAGE_MAP
    config = Configuration()
    logger = get_logger()

    def wait_for_package(pkg_id):
        logger.debug('Waiting for the Package (and its Builds) to finish...')
        max_poll_count = 60
        poll_count = 0
        while poll_count < max_poll_count:
            ready = True
            url = '{}/serviceclass/status'.format(config.catalog_server)
            params = {'package_uid': pkg_id, 'builds': 'true'}
            response = config.client._catalog_client._execute(url, HttpMethod.GET, query_params=params)
            new_package = get_api_response_data(response, parse_full=True)
            package_info = new_package['packageInfo']
            if package_info['status'] != 'Complete':
                ready = False
            if 'buildInfo' in new_package:
                for build in new_package['buildInfo']:
                    if build['status'] != 'Complete':
                        ready = False
            if ready:
                break
            sleep(20)
            poll_count += 1

    path = get_manifest_file(manifest_name, 'Package')
    with open(path, 'r') as f:
        package_payload = json.load(f)
    if package_name is not None:
        package_payload['name'] = package_name

    if build_map is not None:
        _apply_build_on_package(package_payload, build_map)

    if modify_func is not None:
        modify_func(package_payload)

    logger.info('Creating the package: %s', package_name)
    package = config.client.create_package(manifest=package_payload, retry_limit=2)
    _PACKAGE_MAP[package_name] = package
    if wait:
        wait_for_package(package['packageId'])
    return package


def _apply_build_on_package(manifest, build_map):
    """
    _apply_build_on_package implements the logic of injecting the Build Map into the Package Manifest.

    manifest: Parsed JSON payload in the form of Dictionary of the Package.
    build_map: Dictionary with the Build Information. Check docstring of `add_package` for more information.
    """
    global _BUILD_MAP
    if build_map is None:
        return

    for component in manifest['plans'][0]['components']:
        if component['name'] in build_map:
            component_name = component['name']
            for executable in component['executables']:
                exec_name = executable['name']
                if exec_name in build_map[component_name]:
                    build_name = build_map[component_name][exec_name][0]
                    build_manifest = build_map[component_name][exec_name][1]
                    if _BUILD_MAP.get(build_name) is None:
                        add_build(build_manifest, build_name)
                    build = get_build(build_name)
                    executable['buildGUID'] = build['guid']


def delete_package(package_name, delete_builds=True):
    """
    delete_package is a utility function that deletes the Packages using there *Manifest* name. It is idempotent and can
    be safely called multiple times for the same package.

    package_name: Name of the Package Manifest (JSON file) without the extension
    [optional] delete_builds: Flag to enable/disable the cleanup of Builds associated with the Package.
    Default: True
    """
    global _PACKAGE_MAP
    config = Configuration()
    logger = get_logger()

    if package_name not in _PACKAGE_MAP:
        return

    package_data = _PACKAGE_MAP[package_name]

    url = '{}/serviceclass/status'.format(config.catalog_server)
    params = {'package_uid': package_data['packageId'], 'builds': 'true'}
    response = config.client._catalog_client._execute(url, HttpMethod.GET, query_params=params)
    package = get_api_response_data(response, parse_full=True)
    builds = []
    if 'buildInfo' in package:
        for build in package['buildInfo']:
            builds.append(build['guid'])

    url = '{}/{}?package_uid={}'.format(config.catalog_server, '/serviceclass/delete', package_data['packageId'])
    logger.info('Deleting the package: %s', package_name)
    config.client._catalog_client._execute(url, HttpMethod.DELETE, 2)

    if delete_builds:
        for build in builds:
            config.client.delete_build(build)


def get_routed_network(network_name):
    """
    get_routed_network is the utility function to fetch the Routed Network by its name. The latest
    RoutedNetwork object is fetched using the API.

    network_name: Name of the Routed Network
    """
    global _ROUTED_NETWORK_MAP
    config = Configuration()
    network_id = _ROUTED_NETWORK_MAP[network_name]['guid']
    return config.client.get_routed_network(network_id)


def add_cloud_routed_network(network_name, ros_distro=ROSDistro.KINETIC, wait=True):
    """
    add_cloud_routed_network is a utility function that provisions a Cloud Routed Network.

    network_name: Name of the Routed Network
    [optional] ros_distro: ROS Distribution for the Routed Network
    Default: Kinetic
    [optional] wait: Flag to enable waiting for the Routed Network to succeed
    Default: True
    """
    global _ROUTED_NETWORK_MAP
    config = Configuration()
    logger = get_logger()
    logger.info('Provisioning the cloud routed network: %s', network_name)
    routed_network = config.client.create_cloud_routed_network(network_name, ros_distro, True)
    _ROUTED_NETWORK_MAP[network_name] = routed_network
    if wait:
        logger.debug('Waiting for the routed network %s to succeed', network_name)
        routed_network.poll_routed_network_till_ready(sleep_interval=10)
    return routed_network


def delete_routed_network(network_name):
    """
    delete_routed_network is a utility function that deletes the Routed Network by its name. This
    function is idempotent and it can be safely called multiple times for the same Network.

    network_name: Name of the Routed Network
    """
    global _ROUTED_NETWORK_MAP
    if network_name in _ROUTED_NETWORK_MAP:
        _ROUTED_NETWORK_MAP[network_name].delete()
        del _ROUTED_NETWORK_MAP[network_name]


def get_logger():
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('RIO_SDK Logger')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.handler_set = True
        logger.addHandler(console_handler)
    return logger


def start_roscore(device, bg=True):
    command = Command(cmd='source /opt/ros/melodic/setup.bash && roscore', shell='/bin/bash', bg=bg)
    device.execute_command(command, retry_limit=10)
    sleep(10)


def stop_roscore(device, bg=True):
    command = Command(cmd='pkill roscore', shell='/bin/bash', bg=bg)
    device.execute_command(command, retry_limit=10)


def add_cloud_native_network(network_name, ros_distro=ROSDistro.KINETIC, wait=True):
    """
    add_cloud_native_network is a utility function that provisions a Cloud Native Network.

    network_name: Name of the Native Network
    [optional] ros_distro: ROS Distribution for the Native Network
    Default: Kinetic
    [optional] wait: Flag to enable waiting for the Native Network to succeed
    Default: True
    """
    global _NATIVE_NETWORK_MAP
    config = Configuration()
    logger = get_logger()
    logger.info('Provisioning the cloud native network: %s', network_name)
    native_network_payload = NativeNetwork(network_name, Runtime.CLOUD, ros_distro)
    native_network = config.client.create_native_network(native_network_payload)
    _NATIVE_NETWORK_MAP[network_name] = native_network
    if wait:
        logger.debug('Waiting for the native network %s to succeed', network_name)
        native_network.poll_native_network_till_ready(sleep_interval=10)
    return native_network


def delete_native_network(network_name):
    """
    delete_native_network is a utility function that deletes the Native Network by its name. This
    function is idempotent and it can be safely called multiple times for the same Network.

    network_name: Name of the Native Network
    """
    global _NATIVE_NETWORK_MAP
    if network_name in _NATIVE_NETWORK_MAP:
        config = Configuration()
        network_id = _NATIVE_NETWORK_MAP[network_name].guid
        config.client.delete_native_network(network_id)
        del _NATIVE_NETWORK_MAP[network_name]


def get_native_network(network_name):
    """
    get_routed_network is the utility function to fetch the Native Network by its name. The latest
    NativeNetwork object is fetched using the API.

    network_name: Name of the Native Network
    """
    global _NATIVE_NETWORK_MAP
    config = Configuration()
    network_id = _NATIVE_NETWORK_MAP[network_name].guid
    return config.client.get_native_network(network_id)
