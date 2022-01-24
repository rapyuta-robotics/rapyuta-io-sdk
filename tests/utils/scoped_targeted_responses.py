SCOPED_TARGETED_PACKAGE = '''
{
    "packageInfo": {
        "ID": 1301,
        "CreatedAt": "2019-01-23T14:17:53.779808Z",
        "UpdatedAt": "2019-01-23T14:30:52.646725Z",
        "DeletedAt": null,
        "guid": "pkg-uxpnzkxtpjzuumykpcvjtmws",
        "packageVersion": "v1.0.0",
        "description": "test scoped and targeted",
        "packageName": "C2DPingMaxST2",
        "creator": "124649aa-a6d5-413f-82a6-fd7607c9ef9c",
        "ownerProject": "test_project",
        "tags": null,
        "plans": [
            {
                "ID": 1227,
                "CreatedAt": "2019-01-23T14:17:53.784866Z",
                "UpdatedAt": "2019-01-23T14:17:53.784866Z",
                "DeletedAt": null,
                "planId": "basicplan",
                "packageId": 1301,
                "planName": "default",
                "internalComponents": [
                    {
                        "componentId": "cloud-comp",
                        "componentName": "cloudping",
                        "runtime": "cloud"
                    },
                    {
                        "componentId": "dev-comp",
                        "componentName": "devicepong",
                        "runtime": "device"
                    }
                ],
                "dependentDeployments": [],
                "components": {
                    "components": [
                        {
                            "architecture": "amd64",
                            "cloudInfra": {
                                "endpoints": [],
                                "replicas": 1
                            },
                            "description": "",
                            "executables": [
                                {
                                    "args": null,
                                    "buildOptions": {
                                        "catkinOptions": [
                                            {
                                                "blacklist": "",
                                                "catkinMakeArgs": "",
                                                "cmakeArgs": "",
                                                "makeArgs": "",
                                                "rosPkgs": "pingpong"
                                            }
                                        ]
                                    },
                                    "env": null,
                                    "gitExecutable": {
                                        "contextDir": "",
                                        "dockerFilePath": "",
                                        "repository": "ssh://bitbucket.org/rapyutians/io_test_scenarios.git#feature/scoped_targeted",
                                        "strategyType": "Source"
                                    },
                                    "id": "exec-trelpvdeotddzitpyvxfafva",
                                    "name": "cloudy"
                                }
                            ],
                            "labels": null,
                            "name": "cloudping",
                            "parameters": [
                                {
                                    "default": "pingpong",
                                    "name": "ROS_PKG"
                                },
                                {
                                    "default": "pingst.launch",
                                    "name": "ROS_LAUNCH_FILE"
                                }
                            ],
                            "requiredRuntime": "cloud",
                            "ros": {
                                "isROS": true,
                                "topics": [
                                    {
                                        "name": "ping",
                                        "qos": "low",
                                        "scoped": true
                                    }
                                ]
                            }
                        },
                        {
                            "architecture": "amd64",
                            "cloudInfra": {
                                "endpoints": null,
                                "replicas": 1
                            },
                            "description": "",
                            "executables": [
                                {
                                    "args": null,
                                    "cmd": [
                                        "roslaunch pingpong pongst.launch"
                                    ],
                                    "env": null,
                                    "id": "exec-wctqfzfkcffjlpfnqsdcuwxf",
                                    "name": "divvy"
                                }
                            ],
                            "labels": null,
                            "name": "devicepong",
                            "parameters": [],
                            "requiredRuntime": "device",
                            "ros": {
                                "isROS": true,
                                "topics": [
                                    {
                                        "name": "pong",
                                        "qos": "low",
                                        "targeted": true
                                    }
                                ]
                            }
                        }
                    ]
                },
                "metadata": {
                    "exposedParameters": []
                },
                "singleton": false,
                "description": "",
                "inboundROSInterfaces": {
                    "inboundROSInterfaces": {
                        "isROS": true
                    }
                }
            }
        ],
        "buildGeneration": 1,
        "status": "Complete",
        "isPublic": false,
        "category": "Default",
        "bindable": true
    },
    "packageUrl": "https://storage.googleapis.com/v7-eta-manifest-bucket/pkg-uxpnzkxtpjzuumykpcvjtmws-manifest.json?Expires=1548934928&GoogleAccessId=rio-bucket-devs%40rapyuta-io.iam.gserviceaccount.com&Signature=X1R9NYtYh9N9phCA%2BCD%2BQUlZVVK89Th7F1IL5cw4IeahAo7gmBNnsT2riIwm%2FDtrcEuuav4FoRzwIImeanl%2F6AfDMdKp7ojAaSVKPNnK0IoBVmBE79xAwfDhvn6Tfdf0FyIAFwectkj23%2Fm28MjTI73fS9LoLJczLv6kz%2FYnuq%2BpXo6c%2F2YtUTq8Fajk8UzQGuZMzNRBbGw138fDyw6K2296FejZMpSPA%2BRgOm8pWD%2FtZHMZ5oVz06fnDrjpmP6zcBcKmDiRz4wpXYeG%2BwU8oat8%2B8fWpKu17tVBOmJPsqptX9YrIUa%2FyruDo0gznW0%2FqMy00RCKAzWEajoivhZdpA%3D%3D"
}
'''

SCOPED_CLOUD_PACKAGE = '''
{
    "packageInfo": {
        "ID": 1301,
        "CreatedAt": "2019-01-23T14:17:53.779808Z",
        "UpdatedAt": "2019-01-23T14:30:52.646725Z",
        "DeletedAt": null,
        "guid": "pkg-uxpnzkxtpjzuumykpcvjtmws",
        "packageVersion": "v1.0.0",
        "description": "test scoped and targeted",
        "packageName": "C2DPingMaxST2",
        "creator": "124649aa-a6d5-413f-82a6-fd7607c9ef9c",
        "ownerProject": "test_project",
        "tags": null,
        "plans": [
            {
                "ID": 1227,
                "CreatedAt": "2019-01-23T14:17:53.784866Z",
                "UpdatedAt": "2019-01-23T14:17:53.784866Z",
                "DeletedAt": null,
                "planId": "basicplan",
                "packageId": 1301,
                "planName": "default",
                "includePackages": [],
                "internalComponents": [
                    {
                        "componentId": "cloud-comp",
                        "componentName": "cloudping",
                        "runtime": "cloud"
                    }
                ],
                "dependentDeployments": [],
                "components": {
                    "components": [
                        {
                            "architecture": "amd64",
                            "cloudInfra": {
                                "endpoints": [],
                                "replicas": 1
                            },
                            "description": "",
                            "executables": [
                                {
                                    "args": null,
                                    "buildOptions": {
                                        "catkinOptions": [
                                            {
                                                "blacklist": "",
                                                "catkinMakeArgs": "",
                                                "cmakeArgs": "",
                                                "makeArgs": "",
                                                "rosPkgs": "pingpong"
                                            }
                                        ]
                                    },
                                    "env": null,
                                    "gitExecutable": {
                                        "contextDir": "",
                                        "dockerFilePath": "",
                                        "repository": "ssh://bitbucket.org/rapyutians/io_test_scenarios.git#feature/scoped_targeted",
                                        "strategyType": "Source"
                                    },
                                    "id": "exec-trelpvdeotddzitpyvxfafva",
                                    "name": "cloudy"
                                }
                            ],
                            "labels": null,
                            "name": "cloudping",
                            "parameters": [
                                {
                                    "default": "pingpong",
                                    "name": "ROS_PKG"
                                },
                                {
                                    "default": "pingst.launch",
                                    "name": "ROS_LAUNCH_FILE"
                                }
                            ],
                            "requiredRuntime": "cloud",
                            "ros": {
                                "isROS": true,
                                "topics": [
                                    {
                                        "name": "ping",
                                        "qos": "low",
                                        "scoped": true
                                    }
                                ]
                            }
                        }
                    ]
                },
                "metadata": {
                    "exposedParameters": []
                },
                "singleton": false,
                "description": "",
                "inboundROSInterfaces": {
                    "inboundROSInterfaces": {
                        "isROS": true
                    }
                }
            }
        ],
        "buildGeneration": 1,
        "status": "Complete",
        "isPublic": false,
        "category": "Default",
        "bindable": true
    },
    "packageUrl": "https://storage.googleapis.com/v7-eta-manifest-bucket/pkg-uxpnzkxtpjzuumykpcvjtmws-manifest.json?Expires=1548934928&GoogleAccessId=rio-bucket-devs%40rapyuta-io.iam.gserviceaccount.com&Signature=X1R9NYtYh9N9phCA%2BCD%2BQUlZVVK89Th7F1IL5cw4IeahAo7gmBNnsT2riIwm%2FDtrcEuuav4FoRzwIImeanl%2F6AfDMdKp7ojAaSVKPNnK0IoBVmBE79xAwfDhvn6Tfdf0FyIAFwectkj23%2Fm28MjTI73fS9LoLJczLv6kz%2FYnuq%2BpXo6c%2F2YtUTq8Fajk8UzQGuZMzNRBbGw138fDyw6K2296FejZMpSPA%2BRgOm8pWD%2FtZHMZ5oVz06fnDrjpmP6zcBcKmDiRz4wpXYeG%2BwU8oat8%2B8fWpKu17tVBOmJPsqptX9YrIUa%2FyruDo0gznW0%2FqMy00RCKAzWEajoivhZdpA%3D%3D"
}
'''

CAN_BE_TARGETED = '''
{
    "packageInfo": {
        "ID": 1304,
        "CreatedAt": "2019-01-25T18:07:32.847148Z",
        "UpdatedAt": "2019-01-25T18:07:33.157591Z",
        "DeletedAt": null,
        "guid": "pkg-lvpqspjbkjaqlvgrxpsbaczs",
        "packageVersion": "v1.0.0",
        "description": "asas",
        "packageName": "canbetargeted",
        "creator": "124649aa-a6d5-413f-82a6-fd7607c9ef9c",
        "ownerProject": "test_project",
        "tags": null,
        "plans": [
            {
                "ID": 1230,
                "CreatedAt": "2019-01-25T18:07:32.852205Z",
                "UpdatedAt": "2019-01-25T18:07:32.852205Z",
                "DeletedAt": null,
                "planId": "basicplan",
                "packageId": 1304,
                "planName": "default",
                "internalComponents": [
                    {
                        "componentId": "compid",
                        "componentName": "comp",
                        "runtime": "cloud"
                    }
                ],
                "dependentDeployments": [],
                "components": {
                    "components": [
                        {
                            "architecture": "amd64",
                            "cloudInfra": {
                                "endpoints": [],
                                "replicas": 1
                            },
                            "description": "",
                            "executables": [
                                {
                                    "args": null,
                                    "cmd": [
                                        "/bin/bash",
                                        "-c",
                                        "vaaa"
                                    ],
                                    "docker": "xaaaa",
                                    "env": null,
                                    "id": "exec-saljwxoswnmppvbssxnxgurh",
                                    "name": "aaaa"
                                }
                            ],
                            "labels": null,
                            "name": "comp",
                            "parameters": [],
                            "requiredRuntime": "cloud",
                            "ros": {
                                "isROS": true
                            }
                        }
                    ]
                },
                "metadata": {
                    "exposedParameters": []
                },
                "singleton": false,
                "description": "",
                "inboundROSInterfaces": {
                    "inboundROSInterfaces": {
                        "isROS": true,
                        "topics": [
                            {
                                "name": "hello",
                                "targeted": true
                            }
                        ]
                    }
                }
            }
        ],
        "buildGeneration": 0,
        "status": "Complete",
        "isPublic": false,
        "category": "Default",
        "bindable": true
    },
    "packageUrl": "https://storage.googleapis.com/v7-eta-manifest-bucket/pkg-lvpqspjbkjaqlvgrxpsbaczs-manifest.json?Expires=1548942529&GoogleAccessId=rio-bucket-devs%40rapyuta-io.iam.gserviceaccount.com&Signature=IV4jxZzvWvUil%2BluTxG2zH9cXJSTRj9oGOzIhnN88bScFkeY97vODCf4aSX%2B3oflKUmgULkSGW3HshfxhchKtFrqbCny4blMP9l08kQbVprmYB93%2Bp3siUZWTpmwkPfDC7dYbx6Cc1B37%2FcLlqwzY0P%2BeWwk8vmyMxZJ1zBHn%2B9960YrJFEkc1%2BAVNGiT%2FeYwa8Ir6wbt9few%2FMT8vr9yb9%2FcxQHjKsBg9%2BFTE%2B%2Fidor7IbS0vDvTXxAv%2BhaMTskHnpg%2B7R9cIF7rYgjnt%2BMa0Hv70DTiDyx8w4XTaFLOH59Ta9RV2RF5Q0jxsip9UfDoOgIp8Cg6wNQVvRGrrp4ZQ%3D%3D"
}
'''

SCOPED_TARGETABLE_DEPEPNDANT_DEPLOY = """
{
    "ID": 1391,
    "CreatedAt": "2019-01-31T13:10:18.807303Z",
    "UpdatedAt": "2019-01-31T13:11:43.559441Z",
    "DeletedAt": null,
    "packageId": "pkg-lvpqspjbkjaqlvgrxpsbaczs",
    "packageName": "canbetargeted",
    "ownerProject": "test_project",
    "creator": "124649aa-a6d5-413f-82a6-fd7607c9ef9c",
    "planId": "plan-pzqlmdodqpwkruoiochsrllq",
    "deploymentId": "deployment_id",
    "name": "targetableboo",
    "parameters": {
        "global": {},
        "sszyzwycqdgsnmgezoyaqydy": {
            "bridge_params": {
                "alias": "parent",
                "setROSNamespace": true
            },
            "brokerConfig": {
                "host": "inst-ojlsdxgmwarqfszwaglmvtuv-broker.apps.v39.rapyuta.io",
                "name": "broker-inst-ojlsdxgmwarqfszwaglmvtuv",
                "password": "zjatsmwpag",
                "port": 443,
                "user": "user-ygcmu"
            },
            "component_id": "sszyzwycqdgsnmgezoyaqydy",
            "inClusterBrokerConfig": {
                "host": "broker.dep-ns-inst-ojlsdxgmwarqfszwaglmvtuv",
                "name": "broker-inst-ojlsdxgmwarqfszwaglmvtuv",
                "password": "zjatsmwpag",
                "user": "user-ygcmu"
            }
        }
    },
    "componentInstanceIds": [
        {
            "packageId": "helm-ewthjqzxjjulbgiiufnoxdct",
            "planId": "plan-alcdyzdlhbmsnymymnogikhp",
            "componentInstanceId": "inst-xpohdwouzmxrwleqcxlbzxmf",
            "source": "helm",
            "errorCode": ""
        },
        {
            "packageId": "helm-io-amqp-broker",
            "planId": "standalone",
            "componentInstanceId": "inst-ojlsdxgmwarqfszwaglmvtuv",
            "source": "helm",
            "errorCode": ""
        }
    ],
    "dependentDeployments": [],
    "labels": [],
    "inUse": false,
    "usedBy": "",
    "phase": "Succeeded",
    "status": "Error",
    "componentInfo": [
        {
            "componentID": "sszyzwycqdgsnmgezoyaqydy",
            "name": "kkkk",
            "runtime": "cloud",
            "status": "Error",
            "phase": "Succeeded",
            "errorCode": [
                "DEP_E153"
            ],
            "executablesStatusInfo": [
                {
                    "id": "cloud-bridge",
                    "status": "Running",
                    "metadata": [
                        {
                            "containerDetail": {
                                "containerID": "docker://a53e5e4c5c43596a4c270e507a631f7019d7252863bb446ee47b7d13d1ed0714",
                                "image": "docker-registry.default.svc:5000/v7-eta-rapyuta-images/cloud-bridge:prod",
                                "imageID": "docker-pullable://docker-registry.default.svc:5000/v7-eta-rapyuta-images/cloud-bridge@sha256:6bea4e9c12a13fccb3743fdcc2d48bb8ae2c815d7b4f9d0dd3c0dd7cc5cb1524",
                                "lastState": {},
                                "name": "cloud-bridge",
                                "ready": true,
                                "restartCount": 0,
                                "state": {
                                    "running": {
                                        "startedAt": "2019-01-31T13:11:37Z"
                                    }
                                }
                            },
                            "podName": "cloud-bridge-548bcc755b-554pt",
                            "podStatus": "Running"
                        }
                    ]
                },
                {
                    "id": "exec-saljwxoswnmppvbssxnxgurh",
                    "status": "Error ErrImagePull",
                    "reason": "ErrImagePull",
                    "errorCode": "DEP_E153",
                    "metadata": [
                        {
                            "containerDetail": {
                                "image": "xaaaa",
                                "imageID": "",
                                "lastState": {},
                                "name": "container-exec-saljwxoswnmppvbssxnxgurh",
                                "ready": false,
                                "restartCount": 0,
                                "state": {
                                    "waiting": {
                                        "message": "rpc error: code = Unknown desc = repository docker.io/xaaaa not found: does not exist or no pull access",
                                        "reason": "ErrImagePull"
                                    }
                                }
                            },
                            "podName": "inst-xpohdwouzmxrwleqcxlbzxmf-cwpdkl-6c94cd7469-j7kk7",
                            "podStatus": "Error ErrImagePull"
                        }
                    ]
                },
                {
                    "id": "rosmaster",
                    "status": "Running",
                    "metadata": [
                        {
                            "containerDetail": {
                                "containerID": "docker://f07334bb40017460bddd4e18a38b2356b5b0abd4ec51b83c36cdd4adc8b7907f",
                                "image": "docker-registry.default.svc:5000/v7-eta-rapyuta-images/cloud-master:prod",
                                "imageID": "docker-pullable://docker-registry.default.svc:5000/v7-eta-rapyuta-images/cloud-master@sha256:f7d22685da6642ed51e08123e0d816cba149ff2160508077ec5f8fedf7e8c310",
                                "lastState": {},
                                "name": "rosmaster",
                                "ready": true,
                                "restartCount": 0,
                                "state": {
                                    "running": {
                                        "startedAt": "2019-01-31T13:11:21Z"
                                    }
                                }
                            },
                            "podName": "rosmaster-deployment-757f6677d7-hwkt9",
                            "podStatus": "Running"
                        }
                    ]
                }
            ],
            "executableMetaData": [
                {
                    "id": "exec-saljwxoswnmppvbssxnxgurh",
                    "name": "aaaa",
                    "docker": "xaaaa",
                    "cmd": [
                        "/bin/bash",
                        "-c",
                        "vaaa"
                    ],
                    "args": null,
                    "env": null
                }
            ],
            "isDeprovisioned": false
        },
        {
            "componentID": "io-amqp-broker",
            "name": "io-amqp-broker",
            "runtime": "cloud",
            "status": "Running",
            "phase": "Succeeded",
            "errorCode": null,
            "executablesStatusInfo": [
                {
                    "id": "broker",
                    "status": "Running",
                    "metadata": [
                        {
                            "containerDetail": {
                                "containerID": "docker://cd01a7b4db97f85447bc02b7dcf82d5445988a0989be156d1cf313632e3ab330",
                                "image": "docker-registry.default.svc:5000/rapyuta-images/broker:latest",
                                "imageID": "docker-pullable://docker-registry.default.svc:5000/rapyuta-images/broker@sha256:dd2d05b6a63a7d1d883679b50f62db735189e9fb36a5c9c620335c234392344c",
                                "lastState": {},
                                "name": "broker",
                                "ready": true,
                                "restartCount": 0,
                                "state": {
                                    "running": {
                                        "startedAt": "2019-01-31T13:10:35Z"
                                    }
                                }
                            },
                            "podName": "broker-1-6xhpd",
                            "podStatus": "Running"
                        }
                    ]
                }
            ],
            "executableMetaData": null,
            "isDeprovisioned": false
        }
    ],
    "dependentDeploymentStatus": {},
    "errors": [
        "DEP_E153"
    ],
    "packageDependencyStatus": {},
    "bindable": true
}
"""
