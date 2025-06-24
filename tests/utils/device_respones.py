# encoding: utf-8
from __future__ import absolute_import

from string import Template

from tests.utils.package_responses import merge_dicts

DEVICE_BASE = Template('''
{
    "status": "success",
    "response": {
        "data": {
            "status": "ONLINE",
            "username": "root",
            "uuid": "test_device_id",
            "saltversion": "2017.7.0",
            "registration_time": "2018-07-27T12:46:14.250756",
            "remote_update_script": "",
            "description": "",
            "labels": [
             {
        "value": "value1",
        "id": 100,
        "key": "label1"
      },
      {
        "value": "value2",
        "id": 101,
        "key": "label2"
      }
            ],
            "config_variables": [
                $runtime,
                {
                    "value": "config_key",
                    "id": 2134,
                    "key": "config_value"
                }
            ],
            "last_online": "2018-07-27T12:47:28.697053",
            "created_by": "299d4b46-7353-4111-abdb-2874419b5581",
            "deployments": [
                    {
                    "phase":"stopped",
                    "deployment_id":"inst-test-id",
                    "error_code":null,
                    "created_at":"2019-09-24T13:24:08.909954",
                    "io_deployment_id":"dep-test-id"
                    }
            ],
            "lsb_distrib_description": "Ubuntu 16.04.4 LTS",
            "host": "rapyuta-UP-CHT01",
            "remote_update_log": "",
            "ip_interfaces": {
                "enp1s0": [
                    "10.91.1.239",
                    "fe80::3f85:e8ac:138:e41c"
                ],
                "lo": [
                    "127.0.0.1",
                    "::1"
                ],
                "docker0": [
                    "172.17.0.1"
                ],
                "wlxec3dfde592bc": []
            },
            "name": "D239-Device"
        }
    }
}''')

PREINSTALL_RUNTIME_CONFIG = {
    "runtime": '''
    {
        "value": "preinstalled",
        "id": 2140,
        "key": "runtime"
    },
    {
        "value": "ros_workspace",
        "id": 2139,
        "key": "ros_workspace"
    },
    {
        "value": "ros_distro",
        "id": 2138,
        "key": "ros_distro"
    }
    '''
}

DOCKER_RUNTIME = {
    "runtime": '''
    {
        "value": "dockercompose",
        "id": 2140,
        "key": "runtime"
    },
    {
        "value": "ros_workspace",
        "id": 2139,
        "key": ""
    },
    {
        "value": "ros_distro",
        "id": 2138,
        "key": "ros_distro"
    }
    '''
}

PREINSTALLED_WITH_NEW_RUNTIME_CONFIG = {
    "runtime": '''
    {
        "value": "True",
        "id": 2140,
        "key": "runtime_preinstalled"
    },
    {
        "value": "ros_workspace",
        "id": 2139,
        "key": ""
    },
    {
        "value": "ros_distro",
        "id": 2138,
        "key": "ros_distro"
    }
    '''
}

CREATE_PREINSTALLED_DEVICE_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": "sample-token",
        "device_id": "test-device-id",
        "script_command": "sudo bash start -r preinstalled -w test/path"
    }
}
'''

CREATE_DOCKERCOMPOSE_DEVICE_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": "sample-token",
        "device_id": "test-device-id",
        "script_command": "sudo bash start -r dockercompose -d melodic -b test/path"
    }
}
'''

CREATE_BOTH_RUNTIMES_DEVICE_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": "sample-token",
        "device_id": "test-device-id",
        "script_command": "sudo bash start -r dockercompose -d melodic -b test/path -r preinstalled"
    }
}
'''

UPGRADE_DOCKERCOMPOSE_DEVICE_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJkZXZpY2VfaWQiOiIxZjdiYzRkNi1hZmFiLTQwMzQtOThiOC01NDJmZjMxNjA1NDQiLCJleHAiOjE2MjU3NjIzMDMsInVzZXIiOiI2MTk1NmQ5Yi03NjNiLTQ4NjEtYmMzMS03M2EwZGFiODk4YjEiLCJwcm9qZWN0IjoicHJvamVjdC10bm9temFyZWNqc2N2Z3NnaW5uZGx6enMiLCJvcmdhbml6YXRpb24iOiJvcmcteG5nanh0dGx5aGRteWZoenVlandqcGxpIn0.8E4liRddQVV9VsQpZwH2zgn8tgZdoba4V_WR1yo9MzUtwm-Wx7wePFauWFbs8UdB",        
        "script_url": "https://qaapiserver.az39.rapyuta.io/start",
        "script_command": "sudo bash start -r dockercompose -d melodic -b test/path"
        }
    }
}
'''

GET_DOCKERCOMPOSE_DEVICE_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": {
                "status": "ONLINE", 
                "uuid": "test-device-id", 
                "registration_time": "2021-07-07T10:48:34.590267", 
                "last_online": null, 
                "name": "test-device", 
                "created_by": "32bf3238-34e0-46d5-ade0-3fc87f9721ea", 
                "description": "test-description", 
                "device_version": "3", 
                "labels": [], 
                "deployments": [], 
                "config_variables": [{"id": 2052, "key": "runtime", "value": "dockercompose", "type": null}, {"id": 2051, "key": "ros_workspace", "value": "", "type": null}, {"id": 2050, "key": "ros_distro", "value": "melodic", "type": null}]
        }
    }
}
'''

GET_PREINSTALLED_DEVICE_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": {
                "status": "REGISTERED", 
                "uuid": "test-device-id", 
                "registration_time": "2021-07-07T10:48:34.590267", 
                "last_online": null, 
                "name": "test-device", 
                "created_by": "32bf3238-34e0-46d5-ade0-3fc87f9721ea", 
                "description": "test-description", 
                "device_version": "3", 
                "labels": [], 
                "deployments": [], 
                "config_variables": [{"id": 2052, "key": "runtime", "value": "preinstalled", "type": null}, {"id": 2051, "key": "ros_workspace", "value": "test/path", "type": null}, {"id": 2050, "key": "ros_distro", "value": "melodic", "type": null}]
        }
    }
}
'''

DEVICE_INFO = DEVICE_BASE.substitute(merge_dicts(PREINSTALL_RUNTIME_CONFIG))
DOCKER_DEVICE = DEVICE_BASE.substitute(merge_dicts(DOCKER_RUNTIME))
PREINSTALLED_DEVICE_WITH_NEW_RUNTIME = DEVICE_BASE.substitute(merge_dicts(PREINSTALLED_WITH_NEW_RUNTIME_CONFIG))

DEVICE_LIST = '''
{
    "status": "success",
    "response": {
        "data": [
            {
                "status": "OFFLINE",
                "uuid": "ebec2ef0-b2e8-4001-b255-4b2dbaeb8520",
                "registration_time": "2018-07-25T13:36:45.373504",
                "description": "",
                "labels": [
                    {
                        "value": "value",
                        "id": 132,
                        "key": "label1"
                    }
                ],
                "config_variables": [
                    {
                        "value": "1917",
                        "id": 2137,
                        "key": "id"
                    },
                    {
                        "value": "key",
                        "id": 2136,
                        "key": "key"
                    },
                    {
                        "value": "value",
                        "id": 2135,
                        "key": "value"
                    },
                    {
                        "value": "preinstalled",
                        "id": 1976,
                        "key": "runtime"
                    },
                    {
                        "value": "/home/rapyuta/catkin_ws",
                        "id": 1975,
                        "key": "ros_workspace"
                    },
                    {
                        "value": "kinetic",
                        "id": 1974,
                        "key": "ros_distro"
                    }
                ],
                "deployments": [],
                "last_online": "2018-07-26T10:04:29.534407",
                "created_by": "299d4b46-7353-4111-abdb-2874419b5581",
                "fingerprint": "ef:b7:69:16:e8:60:17:52:6d:95:56:ed:42:ff:59:b9:fe:d8:57:cf:2c:a7:68:ab:be:ad:18:43:48:c8:23:be",
                "name": "D19-Device"
            },
            {
                "status": "ONLINE",
                "uuid": "3747b7d7-ac60-4109-90a5-3dc4c8097384",
                "registration_time": "2018-07-27T12:46:14.250756",
                "description": "",
                "labels": [],
                "config_variables": [
                    {
                        "value": "preinstalled",
                        "id": 2140,
                        "key": "runtime"
                    },
                    {
                        "value": "",
                        "id": 2139,
                        "key": "ros_workspace"
                    },
                    {
                        "value": "",
                        "id": 2138,
                        "key": "ros_distro"
                    }
                ],
                "deployments": [],
                "last_online": "2018-07-27T12:47:28.697053",
                "created_by": "299d4b46-7353-4111-abdb-2874419b5581",
                "fingerprint": "7a:3f:00:2a:d6:e7:eb:33:8a:95:5b:80:f2:06:21:c1:72:99:67:d5:08:9a:7f:77:21:4d:54:4f:df:91:8a:be",
                "name": "D239-Device"
            }
        ]
    }
}
'''

DEVICE_SELECTION = '''
{
  "status": "success",
  "response": {
    "data": [
      {
        "status": "ONLINE",
        "id": 2,
        "uuid": "3747b7d7-ac60-4109-90a5-3dc4c8097384",
        "name": "D239-Device"
      }
    ]
  }
}
'''

DEVICE_LIST_EMPTY = '''
        {
    "status": "success",
    "response": {
        "data": []}}'''

DEVICE_NOT_FOUND = ''' {
            "status": "error",
            "response": { "data": {}, "error": "device not found" } }'''

UPDATE_DEVICE_OK = ''' { "status": "success", "response": { "data": {
            "status": "ONLINE",
            "uuid": "test_device_id",
            "registration_time": "2018-07-27T12:46:14.250756",
            "description": "test device d19",
            "last_online": "2018-07-27T15:57:06.029273",
            "created_by": "299d4b46-7353-4111-abdb-2874419b5581",
            "name": "Test Device-19" } } }'''

UPDATE_DEVICE_BAD_REQUEST = ''' {
               "status": "error",
               "response": { "data": {}, "error": "device_id parameter missing" } }'''

DELETE_DEVICE_OK = ''' {
            "status": "success",
            "response": { "data": {} } }'''

DELETE_DEVICE_BAD_REQUEST = ''' {
            "status": "error",
            "response": { "data": {}, "error": [ "dep-ohdzzxouusiyxglmptljqccv" ] } }'''

UPGRADE_DEVICE_BAD_REQUEST = ''' {
            "status": "error",
            "response": { "data": {}, "error": [ "dep-ohdzzxouusiyxglmptljqccv" ] } }'''

CONFIG_VARIABLES_BASE = Template('''{
  "status": "success",
  "response": {
    "data": [
      {
        "value": "$runtime",
        "id": 2140,
        "key": "runtime"
      },
      {
        "value": "",
        "id": 2139,
        "key": "ros_workspace"
      },
      {
        "value": "ros_distro",
        "id": 2138,
        "key": "ros_distro"
      }
    ]
  }
}''')

PREINSTALL_RUNTIME = {"runtime": "preinstalled"}
DOCKER_COMPOSE_RUNTIME = {"runtime": "dockercompose"}


CONFIG_VARIABLES = CONFIG_VARIABLES_BASE.substitute(PREINSTALL_RUNTIME)
DOCKER_CONFIG_VARIABLES = CONFIG_VARIABLES_BASE.substitute(DOCKER_COMPOSE_RUNTIME)

DOCKER_EMPTY_ROSBAG_CONFIG_VARIABLES = ''' {
  "status": "success",
  "response": {
    "data": [
      {
        "value": "$runtime",
        "id": 2140,
        "key": "runtime"
      },
      {
        "value": "",
        "id": 2139,
        "key": "ros_workspace"
      },
      {
        "value": "ros_distro",
        "id": 2137,
        "key": "ros_distro"
      }
    ]
  }
}'''

DOCKER_CONFIG_VARIABLE_WITH_ROSBAG_VARIABLES = ''' {
  "status": "success",
  "response": {
    "data": [
      {
        "value": "dockercompose",
        "id": 2140,
        "key": "runtime"
      },
      {
        "value": "",
        "id": 2139,
        "key": "ros_workspace"
      },
      {
        "value": "ros_distro",
        "id": 2137,
        "key": "ros_distro"
      }
    ]
  }
}'''

ADD_CONFIG_VARIABLE_OK = ''' {
            "status": "success",
            "response": { "data": { "value": "value", "id": 100, "key": "testkey" } } } '''

ADD_CONFIG_VARIABLE_BAD_REQUEST = ''' {
                "status": "error",
                "response": { "data": {}, "error": "Database operation failed" } } '''

ADD_CONFIG_VARIABLE_INTERNAL_ERROR = ''' {
            "status": "error",
            "response": { "data": {}, "error": "Database operation failed" } } '''

UPDATE_CONFIG_VARIABLE_OK = ADD_CONFIG_VARIABLE_OK

UPDATE_CONFIG_VARIABLE_BAD_REQUEST = ''' {
                    "status": "error",
                    "response": { "data": {}, "error": "value parameter missing" } } '''

UPDATE_CONFIG_VARIABLE_INTERNAL_ERROR = ADD_CONFIG_VARIABLE_INTERNAL_ERROR

DELETE_CONFIG_VARIABLE_OK = ''' {
                "status": "success",
                "response": { "data": {  } } } '''

DELETE_CONFIG_VARIABLE_NOT_FOUND = ''' {
                    "status": "success",
                    "response": { "data": {  },  "error": "config_variable not found"} } '''

DEVICE_LABELS_LIST_OK = ''' {
            "status": "success",
            "response": {
                "data": [
                {
                    "value": "value1",
                    "id": 100,
                    "key": "label1"
                } ] } }'''

ADD_DEVICE_LABEL_OK = '''{
  "status":"success","response":{
    "data":[  {"value":"value","id":100,"key":"label"} ]}} '''

ADD_DEVICE_LABEL_ERROR = '''{
    "status": "error",
    "response": {
        "data": {},
        "error": "Database operation failed"
    }
       } '''

ADD_DEVICE_LABEL_BAD_REQUEST = '''
        {  "status": "error",  
            "response": {  "data": {}, "error": "labels parameter missing"  } 
        }  '''

UPDATE_DEVICE_LABEL_OK = '''{ "status": "success",  "response": {   "data": {}  } } '''

UPDATE_DEVICE_lABEL_NOT_FOUNT = '''{
            "status": "error", 
            "response": {  "data": {}, "error": "label not found" } } '''

UPDATE_DEVICE_LABEL_BAD_REQUEST = '''{
                "status": "error", 
                "response": {  "data": {}, "error": "label not found" } } '''

DELETE_LABEL_NOT_FOUNT = ''' {
            "status": "error",
            "response": { "data": {}, "error": "label not found" } }'''

EXECUTE_COMMAND_OK = ''' {
    "status": "success",
    "response": {
        "data": { "test_device_id":  "Linux rapyuta 4.9.80-v7+ #1098 SMP Fri Mar 9\
         19:11:42 GMT2018 armv7l armv7l armv7l GNU/Linux" } } } '''

EXECUTE_COMMAND_OK_BG = ''' {
    "status": "success",
    "response": {
        "data": { "test_device_id":  "SUCCESS" } } } '''

EXECUTE_COMMAND_BAD_REQUEST = ''' {
            "status": "error",
            "response": { "data": {}, "error": "device_ids parameter missing" } } '''

TOPIC_LIST = '''{
 "status": "success",
 "response": {
   "data": [
   200,{\"topics\": [\"/rrbridge9a9c343d/rr_cloud_bridge_heartbeat/__self__\", \"/telemetry\", \"/rosout\", \"/rrbridge9a9c343d/rr_cloud_bridge_heartbeat/59e96a60d26e43f0a2ebcf1ae606e2c1\", \"/rosout_agg\", \"/rrbridge04619a72/rr_cloud_bridge_heartbeat/__self__\"]}

      ] } }'''

SUBSCRIBE_TOPIC_OK = ''' {
            "status": "success",
            "response": {
                "data": [ 200, "{\\"master_up\\": true, \\"subscribed_success\\":\
                [\\"\\/rosout\\"],  \\"subscribed_error\\": []}" ] } }'''

SUBSCRIBE_TOPIC_ERROR = "{\n  \"status\":\"success\",\n  \"response\":{\n    \"data\":[\n" \
                        " 400,\n      \"{\\\"master_up\\\": true, \\\"subscribed_success\\\":" \
                        " [], \\\"subscribed_error\\\": [{\\\"\\/testTopic\\\": \\\"Unknown" \
                        " topic type: \\/testTopic\\\"}]}\"\n    ]\n  }\n}\n"

UNSUBSCRIBE_TOPIC_OK = "{\n  \"status\":\"success\",\n  \"response\":{\n    \"data\":[\n  " \
                       " 200,\n \"{\\\"unsubscribed_success\\\": [\\\"\\/inttopic\\\"]," \
                       " \\\"master_up\\\":" "true, \\\"unsubscribed_error\\\": []}\"\n]\n " \
                       "}\n}\n"

SUBSCRIBE_TOPIC_ERROR_INVALID_WHITELIST_TAG = "{\n  \"status\":\"success\",\n  \"response\":{\n    \"data\":[\n" \
                        " 400,\n      \"{\\\"master_up\\\": true, \\\"subscribed_success\\\":" \
                        " [], \\\"subscribed_error\\\": [{\\\"\\/testTopic\\\": \\\"invalid whitelist tag spec" \
                        " topic type: \\/testTopic\\\"}]}\"\n    ]\n  }\n}\n"

SUBSCRIBE_TOPIC_ERROR_INVALID_WHITELIST_FIELD = "{\n  \"status\":\"success\",\n  \"response\":{\n    \"data\":[\n" \
                        " 400,\n      \"{\\\"master_up\\\": true, \\\"subscribed_success\\\":" \
                        " [], \\\"subscribed_error\\\": [{\\\"\\/testTopic\\\": \\\"invalid whitelist field spec" \
                        " topic type: \\/testTopic\\\"}]}\"\n    ]\n  }\n}\n"

UNSUBSCRIBE_TOPIC_ERROR = '''  {
            "status": "success",
            "response": { "data": [ 200, "{\\"unsubscribed_success\\": [],\
             \\"master_up\\": true, \\"unsubscribed_error\\": [\\"\\/testTopic\\"]}" ] } }'''

TOPIC_LIST_EMPTY = '''{
    "status": "success",
    "response": {
        "data": [
   200,{\"topics\": []} ]
    }
}'''

TOPIC_LIST_EMPTY_DATA = '''{
    "status": "success",
    "response": {
        "data": false
    }
}'''

TOPICS_STATUS = ''' {
    "status": "success",
    "response": {
        "data": [
            200, 
            {\"topics\": 
            { \"Unsubscribed\" : [\"/rosout\", \"/rosout_agg\", \"/rrbridge04619a72/rr_cloud_bridge_heartbeat/__self__\"], 
            \"Subscribed\": {
            \"metric\": [], \"log\": [\"/telemetry\"]}}, \"master_up\": true
            
            } ] } }'''


METRIC_STATUS = '''
{
    "status": "success",
    "response": {
        "data": [
            {
                "status": "unsubscribed",
                "kind": "metric",
                "config": {
                    "interval": "30s",
                    "name": "net"
                },
                "name": "network"
            },
            {
                "status": "unsubscribed",
                "kind": "metric",
                "config": {
                    "interval": "30s",
                    "name": "disk"
                },
                "name": "disk"
            },
            {
                "status": "unsubscribed",
                "kind": "metric",
                "config": {
                    "interval": "30s",
                    "name": "diskio"
                },
                "name": "diskio"
            },
            {
                "status": "unsubscribed",
                "kind": "metric",
                "config": {
                    "collect_cpu_time": false,
                    "name": "cpu",
                    "report_active": false,
                    "percpu": true,
                    "interval": "30s",
                    "totalcpu": true
                },
                "name": "cpu"
            },
            {
                "status": "unsubscribed",
                "kind": "metric",
                "config": {
                    "interval": "30s",
                    "name": "mem"
                },
                "name": "memory"
            }
        ]
    }
}
'''

METRIC_SUBSCRIPTION_STATUS_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": {}
    }
}
'''

METRIC_SUBSCRIPTION_STATUS_ERROR = '''
{
    "status": "error",
    "response": {
        "data": {}
    }
}'''

LOGS_UPLOAD_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": {
            "request_uuid": "skjfhkshflsjfoisjfsjfkjshfoij"
        }
    }
    }

'''

LOGS_UPLOAD_STATUS_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": {
            "status": "COMPLETED",
            "error_message": "",
            "creator": "abcd-efgh-higj-87866",
            "request_uuid": "file-uuid",
            "filename": "minion" 
        }
    }

}
'''

LOGS_UPLOAD_STATUS_WITH_SHARED_URL_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": {
            "status": "COMPLETED",
            "error_message": "",
            "creator": "abcd-efgh-higj-87866",
            "request_uuid": "file-uuid",
            "filename": "minion",
            "shared_urls": [
                {
                    "created_at": "2020-11-24T06:17:49.805781",
                    "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
                    "expiry_time": "2020-12-01T06:17:46",
                    "id": 331,
                    "url_uuid": "UMo2tcfa1c"
                },
                {
                    "created_at": "2020-11-23T11:33:06.232781",
                    "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
                    "expiry_time": "2020-11-30T11:33:04.835000",
                    "id": 326,
                    "url_uuid": "GjEPJ02MaZ"
                }
            ]
        }
    }

}
'''

LIST_LOGS_UPLOAD_STATUS_SUCCESS = '''
{
    "status": "success",
    "response": {
        "data": [{
            "status": "COMPLETED",
            "error_message": "",
            "creator": "abcd-efgh-higj-87866",
            "request_uuid": "file-uuid",
            "filename": "minion" 
        },
        {
            "status": "COMPLETED",
            "error_message": "",
            "creator": "abcd-efgh-higj-87866",
            "request_uuid": "file-uuid-1",
            "filename": "minion-1.log" 
        }
        ]
    }

}
'''

LIST_LOGS_UPLOAD_STATUS_FAILURE_INVALID_OPTIONAL_PARAMETERS = '''
{
    "status":"error",
    "response":{
        "data":{},
        "error":"Invalid pagination parameters. Page size should be greater than 1."
    }
}
'''

LOGS_DOWNLOAD_FILE = '''
{
    "status": "success",
    "response": {
        "data": {
            "signed_url": "https://blob.azure.com/blob/upload/file-uuid"
        }
    }

}
'''

LOGS_GENERIC_RESPONSE = '''
{
    "status": "success",
    "response": {
        "data": {
            "success": "true"
        }
    }

}
'''

APPLY_PARAMETERS_SUCCESS_RESPONSE = '''
{
  "status":"success",
  "response":{
    "data":[
      {
        "success": true,
        "device_id": "device-id-1"
      },
      {
        "success": false,
        "device_id": "device-id-2"
      }
    ]
  }
}
'''

CREATE_DIRECT_LINK_SUCCESS_RESPONSE = '''
{
    "status":"success",
    "response":{
        "data":{
            "url_uuid":"testurluuid"
        }
    }
}
'''

PATCH_DAEMONS_SUCCESS = '''
{
    "success": true
}
'''
