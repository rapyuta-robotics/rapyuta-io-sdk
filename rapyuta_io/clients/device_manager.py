# encoding: utf-8
from __future__ import absolute_import

import time
import typing
from enum import Enum

import requests

from rapyuta_io.clients.device import Device, DeviceStatus
from rapyuta_io.clients.model import Command
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.error import ParameterMissingException
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.settings import DAEMONS_PATH, DEVICE_API_ADD_DEVICE_PATH, DEVICE_API_PATH, \
    DEVICE_COMMAND_API_PATH, DEVICE_SELECTION_API_PATH, PARAMETERS_API_PATH
from rapyuta_io.utils.utils import create_auth_header, get_api_response_data, get_error, prepend_bearer_to_auth_token, \
    validate_list_of_strings


class DeviceArch(str, Enum):
    """
    DeviceArch enumeration represents supported device architectures.
    Device architecture can be any of the below types \n
    DeviceArch.ARM32V7 \n
    DeviceArch.ARM64V8 \n
    DeviceArch.AMD64 \n
    """
    ARM32V7 = 'arm32v7'
    ARM64V8 = 'arm64v8'
    AMD64 = 'amd64'


class DeviceManagerClient:

    def __init__(self, auth_token, project, device_api_host):
        self._device_api_host = device_api_host
        self._auth_token = prepend_bearer_to_auth_token(auth_token)
        self._project = project

    def _add_auth_token_to_devices(self, devices):
        for device in devices:
            setattr(device, '_device_api_host', self._device_api_host)
            setattr(device, '_auth_token', self._auth_token)
            setattr(device, '_project', self._project)

    def _get_device(self, device_id=None, retry_limit=0, device_name=None):
        url = self._device_api_host + DEVICE_API_PATH
        if device_id:
            url = url + device_id

        query = {}
        if device_name is not None:
            query = {"name": device_name}

        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).retry(retry_limit).headers(headers).query_param(query_param=query).execute()
        return get_api_response_data(response)

    @staticmethod
    def _get_specs_cpuarch_query(arch_list):
        args = []
        if DeviceArch.ARM32V7 in arch_list:
            args.append({"operator": "$in", "args": ["cpuarch", "armv7"]})
        if DeviceArch.ARM64V8 in arch_list:
            args.append({"operator": "$in", "args": ["cpuarch", "aarch64"]})
        if DeviceArch.AMD64 in arch_list:
            args.append({"operator": "$eq", "args": ["cpuarch", "x86_64"]})
            args.append({"operator": "$eq", "args": ["cpuarch", "amd64"]})
        return {"operator": "$or", "specs": {"operator": "$or", "args": args}}

    def _device_selection_by_arch(self, arch_list, retry_limit):
        url = self._device_api_host + DEVICE_SELECTION_API_PATH
        headers = create_auth_header(self._auth_token, self._project)
        payload = self._get_specs_cpuarch_query(arch_list)
        response = RestClient(url).method(HttpMethod.POST).retry(retry_limit) \
            .headers(headers).execute(payload=payload)
        return get_api_response_data(response)

    def set_project(self, project):
        self._project = project

    def device_list(self, online_device=False, arch_list=None, retry_limit=0, device_name=None):
        arch_filtered_uuids = set()
        if arch_list:
            for device in self._device_selection_by_arch(arch_list, retry_limit):
                arch_filtered_uuids.add(device['uuid'])

        # TODO(shivam): if arch_list is set there's no need for _get_device all
        device_list = self._get_device(retry_limit=retry_limit, device_name=device_name)
        devices = []
        # todo: add a generic filter like status, name etc
        for device in device_list:
            device = Device._deserialize(device)
            if online_device and device.status != DeviceStatus.ONLINE.value:
                continue
            if arch_list and device.uuid not in arch_filtered_uuids:
                continue
            devices.append(device)
        self._add_auth_token_to_devices(devices)
        return devices

    def get_device(self, device_id, retry_limit):
        device_data = self._get_device(device_id, retry_limit)
        device = Device._deserialize(device_data)
        self._add_auth_token_to_devices([device])
        device.is_partial = False
        return device

    def apply_parameters(self, device_list, tree_names=None, retry_limit=0):
        validate_list_of_strings(device_list, 'device_list')
        if tree_names:
            validate_list_of_strings(tree_names, 'tree_names')

        url = self._device_api_host + PARAMETERS_API_PATH
        headers = create_auth_header(self._auth_token, self._project)
        payload = {'device_list': device_list}
        if tree_names:
            payload['tree_names'] = tree_names
        response = RestClient(url).method(HttpMethod.POST).retry(retry_limit) \
            .headers(headers).execute(payload=payload)
        return get_api_response_data(response)

    def create_device(self, device):
        url = self._device_api_host + DEVICE_API_ADD_DEVICE_PATH
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.POST).headers(headers).execute(payload=device._serialize())
        return get_api_response_data(response, parse_full=True)

    def delete_device(self, device_id):
        url = self._device_api_host + DEVICE_API_PATH + device_id
        headers = create_auth_header(self._auth_token, self._project)
        return RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()

    def patch_daemons(self, device_id, payload):
        url = self._device_api_host + DEVICE_API_PATH + device_id + DAEMONS_PATH
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.PATCH).headers(headers).execute(payload=payload)
        return get_api_response_data(response, parse_full=True)

    def execute_command(
            self,
            device_ids: typing.List[str],
            command: Command,
            retry_limit: int = 0,
            retry_interval: int = 10,
            timeout: int = 300,
    ):
        """Execute a command on the specified devices.

        Args:
            device_ids: List of device IDs on which the command should be executed.
            command: Command object to be executed.
            retry_limit: Number of retries in case of API failure.
            retry_interval: Interval between retries.
            timeout: Maximum time to wait for the background command to finish.

        Returns:
            dict: Output of the command execution.

        Raises:
            ValueError: If device_ids is empty.
            TimeoutError: If command execution takes longer than the specified timeout.
            ParameterMissingException: If the command is missing required parameters.
        """
        if not device_ids:
            raise ValueError("device_ids cannot be empty")

        command.validate()
        command.device_ids = device_ids

        url = self._device_api_host + DEVICE_COMMAND_API_PATH
        rc = RestClient(url).method(HttpMethod.POST).headers(
            create_auth_header(self._auth_token, self._project))
        response = rc.retry(retry_limit).execute(payload=command.to_json())
        if response.status_code == requests.codes.BAD_REQUEST:
            raise ParameterMissingException(get_error(response.text))

        execution_result = get_api_response_data(response)

        if not command.run_async:
            return execution_result

        jid = execution_result.get('jid')
        if not jid:
            raise ValueError("job id not found in the response")

        url = self._device_api_host + DEVICE_COMMAND_API_PATH + jid
        query = {"jid": jid, "device_id": device_ids}
        time_elapsed = 0
        wait_interval = retry_interval
        while time_elapsed < timeout:
            response = RestClient(url).method(HttpMethod.GET).headers(
                create_auth_header(self._auth_token, self._project)).query_param(query_param=query).execute()
            if response.status_code == requests.codes.OK:
                result = get_api_response_data(response)
                return result
            time.sleep(wait_interval)
            time_elapsed += wait_interval

        raise TimeoutError(f"command result not available after {timeout} seconds")
