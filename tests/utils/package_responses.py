# encoding: utf-8
from __future__ import absolute_import
from string import Template
import json


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


PACKAGE_ADD = Template('''
{
  "apiVersion": "v1.0.0",
  "name": "PingerTest",
  "packageVersion": "v1.0",
  "description": "",
  "plans": [
    {
      "name": "default",
      "metadata": {
        
      },
      "singleton": true,
      "components": [
        {
          "name": "PingComponent",
          "description": "",
          "ros": {
            "topics": [
              
            ],
            "services": [
              
            ],
            "actions": [
              
            ],
            "isROS": true
          },
          "requiredRuntime": "device",
          "architecture": "amd64",
          "executables": [
            {
              "name": "pingExec",
              "cmd": [
                "roslaunch pingpong ping.launch"
              ]
            }
          ],
          "parameters": [
            
          ]
        }
      ],
      "dependentDeployments": [
        
      ],
      "exposedParameters": [
        
      ],
      "inboundROSInterfaces": {
        "topics": [
          
        ],
        "services": [
          
        ],
        "actions": [
          
        ]
      }
    }
  ]
}
''')

PACKAGE_BASE = Template('''
{
    "packageInfo":{
        "bindable":$bindable,
        "CreatedAt":"2017-11-17T09:29:31.619788Z",
        "DeletedAt":null,
        "ID":191,
        "UpdatedAt":"2017-11-17T09:29:31.619788Z",
        "buildGeneration":1,
        "creator":"cdeep2",
        "description":"Package publishes to /chatter",
        "guid":"pkg-xlhpyvigqoorhnomeryjfjqx",
        "ownerProject":"test_project",
        "packageName":"test-1.0",
        "packageVersion":"v1.0.0",
        "plans":[  
            {  
                "CreatedAt":"2017-11-17T09:29:31.622455Z",
                "DeletedAt":null,
                "ID":167,
                "UpdatedAt":"2017-11-17T09:29:31.622455Z",
                "catalogComponents":[  

                ],
                "components":{  
                    "components":[  
                        {  
                            "cloudInfra":{  
                                "endpoints": [
                                    {
                                        "targetPort": 80,
                                        "proto": "HTTPS",
                                        "exposeExternally": true,
                                        "name": "test",
                                        "port": 443
                                    }
                                ],
                                "replicas": 0
                            },
                            "description":"",
                            "executables":[  
                                {  
                                    "args":null,
                                    "cmd":[  
                                        "source /install/setup.bash \u0026\u0026 roslaunch talker talker.launch"
                                    ],
                                    "env":null,
                                    $gitExe
                                    "id":"ros-talker"
                                }
                            ],
                            "labels":null,
                            "name":"ros-talker",
                            $params
                            "requiredRuntime":"$runtime",
                            "ros":{  
                                "isROS":$isROS,
                                "topics":[  
                                    {  
                                        "topicName":"/chatter"
                                    }
                                ]
                            }
                        }
                    ]
                },
                "dependentDeployments":[  

                ],
                "description":"",
                "internalComponents":[  
                    {  
                        "componentId":"jakmybngjupwdjjdqztmcrjq",
                        "componentName":"ros-talker",
                        "planId":"plan-uebhkxkblbjphdqtupfsqsya",
                        "runtime":"$runtime"
                    }
                ],
                "metadata":{  
                    "exposedParameters":null
                },
                "packageId":191,
                "planId":"test-plan",
                "planName":"default",
                "shared":false

            }
        ],
        "status":"New",
        "tags":null
    },
    "packageUrl":"https://storage.googleapis.com/io-rapyuta-pkg-manifests/pkg-xlhpyvigqoorhnomeryjfjqx-manifest.json?Expires=1510915554\u0026GoogleAccessId=io-service-account%40rapyuta-io.iam.gserviceaccount.com\u0026Signature=nobckJTlsX2qj0zZqKsbpZIDvLXz7O3Dcjvp1PYjwQy39FWQIhx6osy0r%2FZe6q39BPhhSCELSwXA5bcCCLM8yXye74B3HtIeyu6uaJzIPFddqDsTrVyvvS2Mgpy9xBVxx8LsTaVO2IdQLkFMWZzFb1eLkQ2yzmXwU2stfGQnTTniSE4iqBucWp5jiPL7KvikEz9hi425lGUp8FQMGs5eS0ToZ0sgoo29uvmXNRBYf1wm2v1o%2Ba85QVWwRkpaVl9A3iI3E5rNhpEXkEablgp3q9TVd4oSPZjizbOCH%2BUf3Fx8%2BDiLE7iaKLmI1vWU3K%2FUaSfWJXJCH6h2GqbYcevS1Q%3D%3D"
}
''')

PACKAGES_LIST = '''{
    "services": [
        {
            "id": "package_id",
            "name": "test_package",
            "description": "test",
            "bindable": true,
            "plans": [
                {
                    "id": "test-plan",
                    "name": "default",
                    "description": "",
                    "free": true,
                    "metadata": {
                        "exposedParameters": [],
                        "singleton": true
                    }
                }
            ],
            "metadata": {
                "creationDate": "2018-08-14T07:43:18.833996Z",
                "creator": "299d4b46-7353-4111-abdb-2874419b5581",
                "isPublic": false,
                "ownerProject": "test_project",
                "packageVersion": "v1.0"
            }
        },
        {
            "id": "pkg-rncbbrzetsbsjwmvsgvmyoqm",
            "name": "Pinger",
            "description": "",
            "bindable": true,
            "plans": [
                {
                    "id": "test-plan",
                    "name": "default",
                    "description": "",
                    "free": true,
                    "metadata": {
                        "exposedParameters": [],
                        "singleton": true
                    }
                }
            ],
            "metadata": {
                "creationDate": "2018-08-13T11:09:32.276282Z",
                "creator": "299d4b46-7353-4111-abdb-2874419b5581",
                "isPublic": false,
                "ownerProject": "test_project",
                "packageVersion": "v1.0"
            }
        }
        
    ]
}
'''

PERSISTENT_VOLUME_INFO = '''
{
  "packageInfo": {
    "ID": 742,
    "CreatedAt": "2018-09-12T12:55:38.222302Z",
    "UpdatedAt": "2018-09-12T12:55:38.222302Z",
    "DeletedAt": null,
    "guid": "io-public-persistent-volume",
    "packageVersion": "v0.1.0",
    "description": "Persistent Volume for Rapyuta IO",
    "packageName": "Rapyuta IO Persistent Volume",
    "creator": "",
    "ownerProject": "test_project",
    "tags": null,
    "plans": [
      {
        "ID": 648,
        "CreatedAt": "2018-09-12T12:55:38.227132Z",
        "UpdatedAt": "2018-09-12T12:55:38.227132Z",
        "DeletedAt": null,
        "planId": "default",
        "packageId": 742,
        "planName": "Default plan",
        "internalComponents": [
          {
            "componentId": "io-pv",
            "planId": "default",
            "componentName": "volumeComponent",
            "runtime": "cloud"
          }
        ],
        "dependentDeployments": [
          
        ],
        "components": {
          "components": [
            {
              "architecture": "",
              "cloudInfra": {
                "endpoints": null,
                "replicas": 1
              },
              "description": "",
              "executables": null,
              "labels": null,
              "name": "volumeComponent",
              "parameters": [
                {
                  "description": "The disk type",
                  "name": "diskType"
                },
                {
                  "description": "Capacity",
                  "name": "capacity"
                }
              ],
              "requiredRuntime": "cloud",
              "ros": null
            }
          ]
        },
        "metadata": null,
        "singleton": false,
        "description": "",
        "inboundROSInterfaces": null
      }
    ],
    "buildGeneration": 0,
    "status": "",
    "isPublic": true,
    "category": "Storage"
  },
  "packageUrl": ""
}
'''

CREATE_PACKAGE = '''
{
  "planIds": [
    {
      "planId": "plan-test-id",
      "componentIds": [
        "comp-test-id"
      ]
    }
  ],
  "packageId": "pkg-test-id"
}
'''

MANIFEST = '''
{
    "name": "listener",
    "packageVersion": "v1.0.0",
    "plans": [
        {
            "name": "default",
            "components": [
                {
                    "name": "default",
                    "architecture": "arm32v7",
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
'''

PROVISION_OK = '''{"operation": "test-deployment"}'''

DEPLOYMENT_INFO = '''{  
      "CreatedAt":"2017-12-01T15:27:21.715594Z",
      "DeletedAt":null,
      "ID":1,
      "UpdatedAt":"2017-12-01T15:27:26.969307Z",
      "componentInfo":[  
         {  
            "componentID":"gpzxcgjynhulepjjcyglgepl",
            "errorCode":"",
            "executables":[  
               {  
                  "metadata":[  
                     {  
                        "containerID":"docker://f110de2579c0a566091c279ff25d9846df3d87935cac8f28ccef1bb7936e307b",
                        "image":"172.30.56.172:5000/rapyuta-images/cloud-bridge:prod",
                        "imageID":"docker-pullable://172.30.56.172:5000/rapyuta-images/cloud-bridge@sha256:c5c77abeb45b5d55edc84452386d53cea28079ea725208ac07a3eb65ded417f4",
                        "lastState":{  
                           "terminated":{  
                              "containerID":"docker://8dbe2dd38986fc36d5614751b2e14b46a0da5a37c5936f231ea072d4777e4061",
                              "exitCode":0,
                              "finishedAt":"2017-12-01T15:28:01Z",
                              "reason":"Completed",
                              "startedAt":"2017-12-01T15:27:54Z"
                           }
                        },
                        "name":"cloud-bridge",
                        "ready":true,
                        "restartCount":3,
                        "state":{  
                           "running":{  
                              "startedAt":"2017-12-01T15:28:30Z"
                           }
                        }
                     }
                  ],
                  "name":"cloud-bridge-3189002553-0z8f6",
                  "status":"Running"
               }
            ]
         }
      ],
      "componentInstanceIds":[  
         {  
            "componentInstanceId":"inst-vsoonlmiuimrjwaoxwmpaecb",
            "packageId":"gpzxcgjynhulepjjcyglgepl",
            "planId":"my_plan_id",
            "source":"helm"
         },
         {  
            "componentInstanceId":"inst-xpohugnuqkcntqozloumksqd",
            "packageId":"io-amqp-broker",
            "planId":"standalone",
            "source":"helm"
         }
      ],
      "creator":"cdeep2",
      "dependentDeployments":{  

      },
      "deploymentId":"dep-lpfeyvfooxgjvffxxicjtxpr",
      "errors":null,
      "ownerProject":"test_project",
      "packageId":"my_package",
      "packageName":"my_package_name",
      "parameters":{  
         "global":{  

         },
         "gpzxcgjynhulepjjcyglgepl":{  
            "ROS_DEVEL_SETUP_FILE":"/opt/rapyuta/catkin/devel/setup.bash",
            "ROS_SETUP_FILE":"/opt/ros/kinetic/setup.bash",
            "brokerConfig":{  
               "host":"inst-xpohugnuqkcntqozloumksqd-broker.ep.rapyuta.io",
               "name":"broker-inst-xpohugnuqkcntqozloumksqd",
               "password":"qesjlfeggq",
               "port":6000,
               "user":"user-euldb"
            },
            "component_id":"gpzxcgjynhulepjjcyglgepl",
            "dependencyBrokerExternalConfigs":[  
               {  
                  "host":"inst-tlyyifqehluaphppkhrjkupy-broker.ep.rapyuta.io",
                  "name":"broker-inst-tlyyifqehluaphppkhrjkupy",
                  "password":"avxovbfnmt",
                  "port":6000,
                  "user":"user-thnsa"
               }
            ],
            "dependencyBrokerInClusterConfigs":[  
               {  
                  "host":"broker.dep-ns-inst-tlyyifqehluaphppkhrjkupy",
                  "name":"broker-inst-tlyyifqehluaphppkhrjkupy",
                  "password":"avxovbfnmt",
                  "user":"user-thnsa"
               }
            ],
            "inClusterBrokerConfig":{  
               "host":"broker.dep-ns-inst-xpohugnuqkcntqozloumksqd",
               "name":"broker-inst-xpohugnuqkcntqozloumksqd",
               "password":"qesjlfeggq",
               "user":"user-euldb"
            }
         }
      },
      "phase":"succeeded",
      "planId":"test-plan",
      "status":"running"
   }'''

DEPLOYMENT_BINDING_OK = '''{
           "credentials": {
               "brokerConfig": {
                   "host": "brocker_host", "name": "brocker_name", "password": "test_password", 
                   "port": 443, "user": "test_user" },
               "inClusterBrokerConfig": {
                   "host": "brocker_name", "name": "test_name", "password": "test_password",
                   "user": "test_user" } 
           } }'''

DEPLOYMENT_STATUS_RUNNING = '''{
  "CreatedAt": "2018-09-07T11:11:28.908215Z",
  "DeletedAt": null,
  "ID": 14,
  "UpdatedAt": "2018-09-07T11:11:30.576511Z",
  "componentInfo": [
    {
      "componentID": "io-pv",
      "errorCode": "",
      "executableMetaData": null,
      "executablesStatusInfo": [
        {
          "id": "io-pv",
          "metadata": null,
          "status": "running"
        }
      ],
      "isDeprovisioned": false,
      "name": "volumeComponent",
      "planID": "default",
      "runtime": "cloud",
      "status": "running"
    },
    {
      "componentID": "io-amqp-broker",
      "errorCode": "",
      "executableMetaData": null,
      "executablesStatusInfo": null,
      "isDeprovisioned": false,
      "name": "io-amqp-broker",
      "planID": "standalone",
      "runtime": "cloud",
      "status": ""
    }
  ],
  "componentInstanceIds": [
    {
      "componentInstanceId": "inst-peviduhqofagnspalxvyfdrz",
      "errorCode": "",
      "packageId": "io-pv",
      "planId": "default",
      "source": "helm"
    }
  ],
  "creator": "d96f75bc-901c-448d-b82b-07ff457617b5",
  "dependentDeploymentStatus": {
    
  },
  "dependentDeployments": [
    
  ],
  "deploymentId": "dep-hdouboqiptstofqukippxysm",
  "errors": null,
  "inUse": false,
  "labels": [
    
  ],
  "name": "va",
  "ownerProject": "test_project",
  "packageDependencyStatus": {
    
  },
  "packageId": "package_id",
  "packageName": "package name",
  "parameters": {
    "global": {
      
    },
    "io-pv": {
      "capacity": 1,
      "component_id": "io-pv",
      "diskType": "default"
    }
  },
  "phase": "Succeeded",
  "planId": "test-plan",
  "status": "Running"
}'''

DEPLOYMENT_STATUS_PENDING = '''{
  "CreatedAt": "2018-09-07T11:11:28.908215Z",
  "DeletedAt": null,
  "ID": 14,
  "UpdatedAt": "2018-09-07T11:11:30.576511Z",
  "componentInfo": [
    {
      "componentID": "io-pv",
      "errorCode": "",
      "executableMetaData": null,
      "executablesStatusInfo": [
        {
          "id": "io-pv",
          "metadata": null,
          "status": "running"
        }
      ],
      "isDeprovisioned": false,
      "name": "volumeComponent",
      "planID": "default",
      "runtime": "cloud",
      "status": "running"
    },
    {
      "componentID": "io-amqp-broker",
      "errorCode": "",
      "executableMetaData": null,
      "executablesStatusInfo": null,
      "isDeprovisioned": false,
      "name": "io-amqp-broker",
      "planID": "standalone",
      "runtime": "cloud",
      "status": ""
    }
  ],
  "componentInstanceIds": [
    {
      "componentInstanceId": "inst-peviduhqofagnspalxvyfdrz",
      "errorCode": "",
      "packageId": "io-pv",
      "planId": "default",
      "source": "helm"
    }
  ],
  "creator": "d96f75bc-901c-448d-b82b-07ff457617b5",
  "dependentDeploymentStatus": {
    
  },
  "dependentDeployments": [
    
  ],
  "deploymentId": "dep-hdouboqiptstofqukippxysm",
  "errors": null,
  "inUse": false,
  "labels": [
    
  ],
  "name": "va",
  "ownerProject": "test_project",
  "packageDependencyStatus": {
    
  },
  "packageId": "package_id",
  "packageName": "package name",
  "parameters": {
    "global": {
      
    },
    "io-pv": {
      "capacity": 1,
      "component_id": "io-pv",
      "diskType": "default"
    }
  },
  "phase": "In progress",
  "planId": "test-plan",
  "status": "Pending"
}'''

DEPLOYMENT_STATUS_RUNNING_PHASE_PROVISIONING = '''{
  "CreatedAt": "2018-09-07T11:11:28.908215Z",
  "DeletedAt": null,
  "ID": 14,
  "UpdatedAt": "2018-09-07T11:11:30.576511Z",
  "componentInfo": [
    {
      "componentID": "io-pv",
      "errorCode": "",
      "executableMetaData": null,
      "executablesStatusInfo": [
        {
          "id": "io-pv",
          "metadata": null,
          "status": "running"
        }
      ],
      "isDeprovisioned": false,
      "name": "volumeComponent",
      "planID": "default",
      "runtime": "cloud",
      "status": "running"
    },
    {
      "componentID": "io-amqp-broker",
      "errorCode": "",
      "executableMetaData": null,
      "executablesStatusInfo": null,
      "isDeprovisioned": false,
      "name": "io-amqp-broker",
      "planID": "standalone",
      "runtime": "cloud",
      "status": ""
    }
  ],
  "componentInstanceIds": [
    {
      "componentInstanceId": "inst-peviduhqofagnspalxvyfdrz",
      "errorCode": "",
      "packageId": "io-pv",
      "planId": "default",
      "source": "helm"
    }
  ],
  "creator": "d96f75bc-901c-448d-b82b-07ff457617b5",
  "dependentDeploymentStatus": {

  },
  "dependentDeployments": [

  ],
  "deploymentId": "dep-hdouboqiptstofqukippxysm",
  "errors": null,
  "inUse": false,
  "labels": [

  ],
  "name": "va",
  "ownerProject": "test_project",
  "packageDependencyStatus": {

  },
  "packageId": "package_id",
  "packageName": "package name",
  "parameters": {
    "global": {

    },
    "io-pv": {
      "capacity": 1,
      "component_id": "io-pv",
      "diskType": "default"
    }
  },
  "phase": "Provisioning",
  "planId": "test-plan",
  "status": "Running"
}'''

DEPLOYMENT_STATUS_STOPPED = '''{
  "CreatedAt": "2018-09-07T11:11:28.908215Z",
  "DeletedAt": null,
  "ID": 14,
  "UpdatedAt": "2018-09-07T11:11:30.576511Z",
  "componentInfo": [
    {
      "componentID": "io-pv",
      "errorCode": "",
      "executableMetaData": null,
      "executablesStatusInfo": [
        {
          "id": "io-pv",
          "metadata": null,
          "status": "running"
        }
      ],
      "isDeprovisioned": false,
      "name": "volumeComponent",
      "planID": "default",
      "runtime": "cloud",
      "status": "running"
    },
    {
      "componentID": "io-amqp-broker",
      "errorCode": "",
      "executableMetaData": null,
      "executablesStatusInfo": null,
      "isDeprovisioned": false,
      "name": "io-amqp-broker",
      "planID": "standalone",
      "runtime": "cloud",
      "status": ""
    }
  ],
  "componentInstanceIds": [
    {
      "componentInstanceId": "inst-peviduhqofagnspalxvyfdrz",
      "errorCode": "",
      "packageId": "io-pv",
      "planId": "default",
      "source": "helm"
    }
  ],
  "creator": "d96f75bc-901c-448d-b82b-07ff457617b5",
  "dependentDeploymentStatus": {
    
  },
  "dependentDeployments": [
    
  ],
  "deploymentId": "dep-hdouboqiptstofqukippxysm",
  "errors": null,
  "inUse": false,
  "labels": [
    
  ],
  "name": "va",
  "ownerProject": "test_project",
  "packageDependencyStatus": {
    
  },
  "packageId": "io-public-persistent-volume",
  "packageName": "Rapyuta IO Persistent Volume",
  "parameters": {
    "global": {
      
    },
    "io-pv": {
      "capacity": 1,
      "component_id": "io-pv",
      "diskType": "default"
    }
  },
  "phase": "Deployment stopped",
  "planId": "default",
  "status": "Deployment not running"
}'''

UPDATE_DEPLOYMENT = '''{
    "deployment_id": "dep-xyiwwwfongcfhpkhqlohtbee",
    "service_id": "pkg-cuawbyybxongczkrmsccceru",
    "plan_id": "plan-tqzmxluchpahnhdaysvtnvxn",
    "context": {
        "component_context": {
            "nudqrokhjkxlqcqlzysrzsbj": {
                "update_deployment": true,
                "component": {  
                    "executables": [
                        {
                            "id": "exec-ghggywcxovmyklbovnhkxkrg",
                            "name": "exe",
                            "docker": "nginx"
                        }
                    ]
                }
            }
        }
    }
}'''

DEPLOYMENT_LIST = '''
[
  {
    "CreatedAt": "2018-08-14T11:48:36.231254Z",
    "DeletedAt": null,
    "ID": 1639,
    "UpdatedAt": "2018-08-29T09:49:58.728879Z",
    "componentInstanceIds": null,
    "creator": "299d4b46-7353-4111-abdb-2874419b5581",
    "dependentDeployments": null,
    "deploymentId": "dep-buowwruwdlhmcqsiczpretic",
    "inUse": false,
    "labels": null,
    "name": "PingerTest004",
    "ownerProject": "test_project",
    "packageId": "pkg-rncbbrzetsbsjwmvsgvmyoqm",
    "packageName": "Pinger",
    "parameters": {
      "dxbsocrkukoktgbnatvhctot": {
        "brokerConfig": {
          "host": "inst-ufrvgtuiregnpejisghngxpk-broker.apps.v39.rapyuta.io",
          "name": "broker-inst-ufrvgtuiregnpejisghngxpk",
          "password": "ebwkfllmgk",
          "port": 443,
          "user": "user-lvplm"
        },
        "component_id": "dxbsocrkukoktgbnatvhctot",
        "device_id": "9c67f2b1-04ac-4425-a426-e11e24f7774b",
        "inClusterBrokerConfig": {
          "host": "broker.dep-ns-inst-ufrvgtuiregnpejisghngxpk",
          "name": "broker-inst-ufrvgtuiregnpejisghngxpk",
          "password": "ebwkfllmgk",
          "user": "user-lvplm"
        },
        "key1": "value1",
        "key11": "value1",
        "key12": "value1",
        "ros_distro": "kinetic",
        "ros_workspace": "/home/hp/catkin_ws"
      },
      "global": {
        "device_ids": [
          "9c67f2b1-04ac-4425-a426-e11e24f7774b"
        ]
      }
    },
    "phase": "Partially deprovisioned",
    "planId": "plan-hqahmuejjksjkuhgkshrmctc"
  }
]
'''

GET_VOLUME_INSTANCE_OK = '''
{
   "ID":3188,
   "CreatedAt":"2021-08-19T08:07:32.236352Z",
   "UpdatedAt":"2021-08-19T08:52:03.338196Z",
   "DeletedAt":null,
   "packageId":"io-public-persistent-volume",
   "packageName":"Rapyuta IO Persistent Volume",
   "packageAPIVersion":"2.0.0",
   "ownerProject":"project-ioelcvlcczsujuouuhcktvcc",
   "creator":"0b90803b-220f-4291-ae72-38dbfb58810c",
   "planId":"default",
   "deploymentId":"test-id",
   "currentGeneration":1,
   "bindable":true,
   "name":"pv-1",
   "parameters":{
      "global":{
         
      },
      "io-pv":{
         "bridge_params":{
            "alias":"volumeComponent",
            "setROSNamespace":false
         },
         "capacity":8,
         "component_id":"io-pv",
         "diskType":"ssd"
      }
   },
   "provisionContext":{
      "component_context":{
         
      },
      "dependentDeployments":[
         
      ],
      "labels":[
         
      ],
      "name":"pv-1",
      "nativeNetworks":[
         
      ],
      "routedNetworks":[
         
      ]
   },
   "lastStatusUpdateTime":"2021-08-19T08:08:44.116352Z",
   "componentInstanceIds":[
      {
         "packageId":"helm-io-pv",
         "planId":"default",
         "componentInstanceId":"inst-nnhmjspaxlmsotrklvqlfkiz",
         "source":"helm",
         "errorCode":"",
         "executableInfo":{
            
         },
         "componentId":"io-pv"
      }
   ],
   "dependentDeployments":[
      
   ],
   "labels":[
      
   ],
   "inUse":true,
   "usedBy":"test-id",
   "phase":"Succeeded",
   "status":"Running",
   "componentInfo":[
      {
         "componentID":"io-pv",
         "componentInstanceID":"inst-nnhmjspaxlmsotrklvqlfkiz",
         "name":"volumeComponent",
         "runtime":"cloud",
         "status":"running",
         "phase":"Succeeded",
         "errorCode":null,
         "executablesStatusInfo":[
            {
               "id":"io-pv",
               "status":"running",
               "metadata":null
            }
         ],
         "executableMetaData":null,
         "isDeprovisioned":false
      }
   ],
   "dependentDeploymentStatus":{
      
   },
   "errors":null,
   "packageDependencyStatus":{
      
   }
}
'''

PARAMS_VALIDATE = {'params': '''
    "parameters":[  
        {  
            "name":"param1",
            "default":"default_val"
        },
        {  
            "name":"param2",
            "default":"value2"
        }
    ],
'''
                   }

PARAMS_NO_VALIDATE = {'params': '''
    "parameters":[  
        {  
            "name":"param1",
            "default":"default_val"
        },
        {  
            "name":"param2"
        }
    ],
'''
                      }

PACKAGE_NOT_FOUND = '''
    {
        "error": "Package not found"
    }
'''

CLOUD_RUNTIME = {'runtime': "cloud"}
DEVICE_RUNTIME = {'runtime': "device"}
BINDABLE = {'bindable': "true"}
NOT_BINDABLE = {'bindable': "false"}
IS_ROS = {'isROS': "true"}
IS_NOT_ROS = {'isROS': "false"}
GIT_EXEC_EMPTY = {"gitExe": ""}
GIT_EXEC_DOCKER = {"gitExe": '''
    "gitExecutable": {
    "repository": "https://github.com/rapyuta-robotics/io_tutorials",
    "strategyType": "Source",
    "dockerFilePath": "",
    "contextDir": "talk/param_talker"
},
'''}
ROSBAG_JOB_DEFS = {'rosBagJobDefs':
            [
                  {
                     "name":"rbag",
                     "recordOptions":{
                        "topics":[
                           "/telemetry"
                        ]
                     }
                  }
            ]
}

ROSBAG_JOB_DEFS_DEVICE = {'rosBagJobDefs':
            [
                  {
                     "name":"rbag",
                     "recordOptions":{
                        "topics":[
                           "/telemetry"
                        ]
                     },
                     "uploadOptions":{
                         "maxUploadRate": 1048576,
                         "purgeAfter": "false"
                     }
                  }
            ]
}

ROSBAG_PROVISION_CONTEXT = {
    'provisionContext': {
        'component_context': {
            'gpzxcgjynhulepjjcyglgepl': {
                'ros_bag_job_defs': [
                    {
                        'name': 'rbag',
                        'recordOptions': {
                            'chunkSize': 100,
                            'compression': '',
                            'maxSplitSize': 1024,
                            'maxSplits': 5,
                            'prefix': 'rbag',
                            'topics': [
                                '/telemetry'
                            ]
                        }
                    }
                ]
            }
        }
    }
}

ROSBAG_PROVISION_CONTEXT_DEVICE = {
    'provisionContext': {
        'component_context': {
            'gpzxcgjynhulepjjcyglgepl': {
                'ros_bag_job_defs': [
                    {
                        'name': 'rbag',
                        'recordOptions': {
                            'chunkSize': 100,
                            'compression': '',
                            'maxSplitSize': 1024,
                            'maxSplits': 5,
                            'prefix': 'rbag',
                            'topics': [
                                '/telemetry'
                            ]
                        },
                        'uploadOptions': {
                            'maxUploadRate': 1048576,
                            'purgeAfter': 'false'
                        }
                    }
                ]
            }
        }
    }
}

PACKAGE_OK_VALIDATE = PACKAGE_BASE.substitute(merge_dicts(
    PARAMS_VALIDATE, CLOUD_RUNTIME, BINDABLE, GIT_EXEC_EMPTY, IS_ROS))
PACKAGE_OK_NON_ROS_VALIDATE = PACKAGE_BASE.substitute(merge_dicts(
    PARAMS_VALIDATE, CLOUD_RUNTIME, BINDABLE, GIT_EXEC_EMPTY, IS_NOT_ROS))
PACKAGE_OK_VALIDATE_NOT_BINDABLE = PACKAGE_BASE.substitute(merge_dicts(
    PARAMS_VALIDATE, CLOUD_RUNTIME, NOT_BINDABLE, GIT_EXEC_EMPTY, IS_ROS))
PACKAGE_OK_NO_VALIDATE = PACKAGE_BASE.substitute(merge_dicts(
    PARAMS_NO_VALIDATE, CLOUD_RUNTIME, BINDABLE, GIT_EXEC_EMPTY, IS_ROS))
PACKAGE_OK_VALIDATE_DEVICE = PACKAGE_BASE.substitute(merge_dicts(
    PARAMS_VALIDATE, DEVICE_RUNTIME, BINDABLE, GIT_EXEC_EMPTY, IS_ROS))
PACKAGE_OK_VALIDATE_DEVICE_DOCKER = PACKAGE_BASE.substitute(merge_dicts(
    PARAMS_VALIDATE, DEVICE_RUNTIME, BINDABLE, GIT_EXEC_DOCKER, IS_ROS))

rosbag_pkg_str = PACKAGE_BASE.substitute(merge_dicts(
    PARAMS_VALIDATE, CLOUD_RUNTIME, BINDABLE, GIT_EXEC_EMPTY, IS_ROS))
rosbag_pkg = json.loads(rosbag_pkg_str)
rosbag_pkg['packageInfo']['plans'][0]['components']['components'][0].update(ROSBAG_JOB_DEFS)
PACKAGE_OK_VALIDATE_ROSBAG_JOB = json.dumps(rosbag_pkg)

rosbag_pkg_str_device = PACKAGE_BASE.substitute(merge_dicts(
    PARAMS_VALIDATE, DEVICE_RUNTIME, BINDABLE, GIT_EXEC_DOCKER, IS_ROS))
rosbag_pkg = json.loads(rosbag_pkg_str_device)
rosbag_pkg['packageInfo']['plans'][0]['components']['components'][0].update(ROSBAG_JOB_DEFS_DEVICE)
PACKAGE_OK_VALIDATE_DEVICE_ROSBAG_JOB = json.dumps(rosbag_pkg)

deployment_info_rosbag_jobs = json.loads(DEPLOYMENT_INFO)
deployment_info_rosbag_jobs.update(ROSBAG_PROVISION_CONTEXT)
DEPLOYMENT_INFO_ROSBAG_JOB = json.dumps(deployment_info_rosbag_jobs)

deployment_info_rosbag_jobs = json.loads(DEPLOYMENT_INFO)
deployment_info_rosbag_jobs.update(ROSBAG_PROVISION_CONTEXT_DEVICE)
DEPLOYMENT_INFO_DEVICE_ROSBAG_JOB = json.dumps(deployment_info_rosbag_jobs)
