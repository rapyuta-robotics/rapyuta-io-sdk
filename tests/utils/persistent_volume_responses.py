GET_PACKAGE_SUCCESS = '''
{
   "packageInfo":{
      "ID":1,
      "CreatedAt":"2020-06-05T12:11:44.795342Z",
      "UpdatedAt":"2020-06-05T12:11:44.795342Z",
      "DeletedAt":"None",
      "guid":"io-public-persistent-volume",
      "packageVersion":"v0.1.0",
      "description":"Persistent Volume for Rapyuta IO",
      "packageName":"Rapyuta IO Persistent Volume",
      "creator":"",
      "ownerProject":"",
      "tags":"None",
      "plans":[
         {
            "ID":1,
            "CreatedAt":"2020-06-05T12:11:44.808649Z",
            "UpdatedAt":"2020-06-05T12:11:44.808649Z",
            "DeletedAt":"None",
            "planId":"default",
            "packageId":1,
            "planName":"Default plan",
            "internalComponents":[
               {
                  "componentId":"io-pv",
                  "componentName":"volumeComponent",
                  "runtime":"cloud"
               }
            ],
            "dependentDeployments":[
               
            ],
            "components":{
               "components":[
                  {
                     "architecture":"",
                     "cloudInfra":{
                        "endpoints":"None",
                        "replicas":1
                     },
                     "description":"",
                     "executables":"None",
                     "labels":"None",
                     "name":"volumeComponent",
                     "parameters":[
                        {
                           "description":"The disk type",
                           "name":"diskType"
                        },
                        {
                           "description":"Capacity",
                           "name":"capacity"
                        }
                     ],
                     "requiredRuntime":"cloud",
                     "restart_policy":"",
                     "ros":{
                        "isROS":false,
                        "ros_distro":""
                     }
                  }
               ]
            },
            "metadata":"None",
            "singleton":false,
            "description":"",
            "inboundROSInterfaces":"None"
         }
      ],
      "buildGeneration":0,
      "status":"Complete",
      "isPublic":true,
      "category":"Storage",
      "bindable":true,
      "apiVersion":"2.0.0"
   },
   "packageUrl":""
}
'''
GET_PERSISTENT_VOLUME_SUCCESS = '''
{
   "packageVersion":"v0.1.0",
   "description":"Persistent Volume for Rapyuta IO",
   "packageName":"Rapyuta IO Persistent Volume",
   "creator":"",
   "tags":"None",
   "plans":[
      {
         "planId":"default",
         "packageId":3,
         "planName":"Default plan",
         "internalComponents":[
            {
               "componentId":"io-pv",
               "componentName":"volumeComponent",
               "runtime":"cloud"
            }
         ],
         "dependentDeployments":[

         ],
         "components":{
            "components":[
               {
                  "architecture":"",
                  "cloudInfra":{
                     "endpoints":"None",
                     "replicas":1
                  },
                  "description":"",
                  "executables":"None",
                  "labels":"None",
                  "name":"volumeComponent",
                  "parameters":[
                     {
                        "description":"The disk type",
                        "name":"diskType"
                     },
                     {
                        "description":"Capacity",
                        "name":"capacity"
                     }
                  ],
                  "requiredRuntime":"cloud",
                  "restart_policy":"",
                  "ros":{
                     "isROS":false,
                     "ros_distro":""
                  }
               }
            ]
         },
         "metadata":"None",
         "singleton":false,
         "description":"",
         "inboundROSInterfaces":"None",
         "_component_id_map":{
            "volumeComponent":"io-pv"
         },
         "_needs_alias":"None"
      }
   ],
   "buildGeneration":0,
   "status":"Complete",
   "isPublic":true,
   "category":"Storage",
   "bindable":true,
   "apiVersion":"2.0.0",
   "planId":"default",
   "packageId":"io-public-persistent-volume",
   "is_refreshed":true,
   "_host":"https://v11catalog.az39.rapyuta.io",
   "_auth_token":"Bearer XsFLxsQ0r2iTZ2FhOs38rNpcUYmOzPCzJzGI1Af8",
   "_project":"project-ioelcvlcczsujuouuhcktvcc"
}
'''
PROVISION_CLIENT_SUCCESS = '''
{
    "name": "test-volume",
    "guid": "disk-guid"
}
'''
GET_DISK_SUCCESS = '''
{
    "createdAt": "2021-12-16T12:12:03.390407Z",
    "name": "test-volume",
    "guid": "disk-guid",
    "diskType": "ssd",
    "capacity": 32,
    "runtime": "cloud",
    "status": "Released",
    "errors": [],
    "internalDeploymentGUID": "dep-guid",
    "usedBy": "",
    "usedByDeploymentName": "",
    "labels": {}
}
'''
GET_DISK_LIST_SUCCESS = '''
[{
    "createdAt": "2021-12-16T12:12:03.390407Z",
    "name": "test-volume",
    "guid": "disk-guid",
    "diskType": "ssd",
    "capacity": 32,
    "runtime": "cloud",
    "status": "Released",
    "errors": [],
    "internalDeploymentGUID": "dep-lblpkngqrhdrefhvnvulaioq",
    "usedBy": "",
    "usedByDeploymentName": "",
    "labels": {}
}]
'''
GET_VOLUME_INSTANCE_SUCCESS = '''
{
   "ID":1974,
   "CreatedAt":"2021-04-14T19:22:35.891321Z",
   "UpdatedAt":"2021-04-14T19:22:35.891321Z",
   "DeletedAt":"None",
   "packageId":"io-public-persistent-volume",
   "packageName":"Rapyuta IO Persistent Volume",
   "packageAPIVersion":"2.0.0",
   "ownerProject":"project-ioelcvlcczsujuouuhcktvcc",
   "creator":"0b90803b-220f-4291-ae72-38dbfb58810c",
   "planId":"default",
   "deploymentId":"dep-lblpkngqrhdrefhvnvulaioq",
   "currentGeneration":1,
   "bindable":true,
   "name":"test-volume",
   "parameters":{
      "global":{

      },
      "io-pv":{
         "bridge_params":{
            "alias":"volumeComponent"
         },
         "capacity":32,
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
      "name":"test-volume3",
      "nativeNetworks":[

      ],
      "routedNetworks":[

      ]
   },
   "componentInstanceIds":[

   ],
   "dependentDeployments":[

   ],
   "labels":[

   ],
   "inUse":false,
   "usedBy":"",
   "phase":"In progress",
   "status":"Deployment not running",
   "componentInfo":[
      {
         "componentID":"io-pv",
         "componentInstanceID":"",
         "name":"volumeComponent",
         "runtime":"cloud",
         "status":"",
         "phase":"",
         "errorCode":"None",
         "executablesStatusInfo":"None",
         "executableMetaData":"None",
         "isDeprovisioned":false
      }
   ],
   "dependentDeploymentStatus":{

   },
   "errors":"None",
   "packageDependencyStatus":{

   }
}
'''
