from __future__ import absolute_import

import logging
from time import sleep

from rapyuta_io.clients.model import Command

_JSON_PATH = ''
_PACKAGE_MAP = dict()
_BUILD_MAP = dict()
_ROUTED_NETWORK_MAP = dict()
_NATIVE_NETWORK_MAP = dict()


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
