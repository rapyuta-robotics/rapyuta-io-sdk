from __future__ import absolute_import
import unittest

from rapyuta_io.utils.error import BadRequestError
from sdk_test.config import Configuration


class CreatePackage(unittest.TestCase):

    def setUp(self):
        self.config = Configuration()

    def test_create_package_fails_for_bad_request(self):
        invalid_manifest = {
            "apiVersion": "v1.0.0",
            "packageVersion": "v1.0.0",
            "plans": [
                {
                    "components": [
                        {
                            "name": "default",
                            "description": "",
                            "executables": [
                                {
                                    "name": "listenerExec",
                                    "cmd": [
                                        "roslaunch listener listener.launch"
                                    ]
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        with self.assertRaises(BadRequestError):
            self.config.client.create_package(invalid_manifest)


