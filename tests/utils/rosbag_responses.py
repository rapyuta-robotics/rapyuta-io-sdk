ROSBAG_JOB_SUCCESS = '''
{
    "ID": 108,
    "CreatedAt": "2020-09-16T05:52:41.350403481Z",
    "UpdatedAt": "2020-09-16T05:52:41.350403481Z",
    "DeletedAt": null,
    "guid": "job-guid",
    "name": "job_name",
    "deploymentID": "dep-id",
    "componentInstanceID": "comp-inst-id",
    "packageID": "pkg-id",
    "componentID": "comp-id",
    "recordOptions": {
        "allTopics": true,
        "compression": "",
        "maxSplits": 5,
        "maxSplitSize": 1024,
        "chunkSize": 100,
        "prefix": "next-job"
    },
    "status": "Starting",
    "creator": "user-id",
    "project": "project-id",
    "Deprovisioned": false
}
'''

ROSBAG_JOB_LIST_SUCCESS = '''
[
    {
        "ID": 108,
        "CreatedAt": "2020-09-16T05:52:41.350403481Z",
        "UpdatedAt": "2020-09-16T05:52:41.350403481Z",
        "DeletedAt": null,
        "guid": "job-guid",
        "name": "job_name",
        "deploymentID": "dep-id",
        "componentInstanceID": "comp-inst-id",
        "packageID": "pkg-id",
        "componentID": "comp-id",
        "recordOptions": {
            "allTopics": true,
            "compression": "",
            "maxSplits": 5,
            "maxSplitSize": 1024,
            "chunkSize": 100,
            "prefix": "next-job"
        },
        "status": "Starting",
        "creator": "user-id",
        "project": "project-id",
        "Deprovisioned": false
    }
]
'''

ROSBAG_BLOB_LIST_SUCCESS = '''
[
    {
        "CreatedAt": "2020-09-11T11:28:18.931011Z",
        "DeletedAt": null,
        "ID": 1,
        "UpdatedAt": "2020-09-11T11:28:24.753525Z",
        "blobRefID": 1,
        "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
        "errorMessage": "",
        "filename": "zwfhu_2020-09-11-10-33-12_0.bag",
        "guid": "blob-id",
        "info": {
            "bagVersion": "2.0",
            "compressedSize": 1254923,
            "compression": "bz2",
            "duration": 3224.911953,
            "endTime": 1599823618.628718,
            "indexed": true,
            "messageCount": 117171,
            "messageTypes": [
                {
                    "md5": "992ce8a1687cec8c8bd883ec73ca41d1",
                    "type": "std_msgs/String"
                }
            ],
            "size": 2685732,
            "startTime": 1599820393.716765,
            "topics": [
                {
                    "frequency": 3.9902,
                    "messageCount": 6,
                    "messageType": "std_msgs/String",
                    "name": "/rapyuta_io_peers"
                }
            ],
            "uncompressedSize": 13927913
        },
        "job": {
            "CreatedAt": "2020-09-10T15:00:21.82102Z",
            "DeletedAt": null,
            "Deprovisioned": false,
            "ID": 74,
            "UpdatedAt": "2020-09-11T11:28:24.747798Z",
            "componentID": "fabdmvqbxwrwpjnuygqjjwle",
            "componentInstanceID": "inst-ttnbrdshjqkhhrvgxwvyuaua",
            "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
            "deploymentID": "dep-otflcqpggktnfpljrliimcxu",
            "guid": "job-id",
            "name": "clock",
            "packageID": "pkg-tfmkgibxnutfsjnvzzwicfcg",
            "project": "project-coxqhybvhaaeteaqdwvkstpr",
            "recordOptions": {
                "allTopics": true,
                "chunkSize": 100,
                "compression": "BZ2",
                "maxSplitSize": 1024,
                "maxSplits": 5
            },
            "status": "Stopped"
        },
        "jobID": 74,
        "project": "project-id",
        "status": "Uploaded"
    }
]
'''

ROSBAG_BLOB_LIST_WITH_DEVICE_BLOB_SUCCESS = '''
[
    {
        "CreatedAt": "2020-09-11T11:28:18.931011Z",
        "DeletedAt": null,
        "ID": 1,
        "UpdatedAt": "2020-09-11T11:28:24.753525Z",
        "blobRefID": 1,
        "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
        "errorMessage": "",
        "filename": "zwfhu_2020-09-11-10-33-12_0.bag",
        "guid": "blob-id",
        "info": {
            "bagVersion": "2.0",
            "compressedSize": 1254923,
            "compression": "bz2",
            "duration": 3224.911953,
            "endTime": 1599823618.628718,
            "indexed": true,
            "messageCount": 117171,
            "messageTypes": [
                {
                    "md5": "992ce8a1687cec8c8bd883ec73ca41d1",
                    "type": "std_msgs/String"
                }
            ],
            "size": 2685732,
            "startTime": 1599820393.716765,
            "topics": [
                {
                    "frequency": 3.9902,
                    "messageCount": 6,
                    "messageType": "std_msgs/String",
                    "name": "/rapyuta_io_peers"
                }
            ],
            "uncompressedSize": 13927913
        },
        "job": {
            "CreatedAt": "2020-09-10T15:00:21.82102Z",
            "DeletedAt": null,
            "Deprovisioned": false,
            "ID": 74,
            "UpdatedAt": "2020-09-11T11:28:24.747798Z",
            "componentID": "fabdmvqbxwrwpjnuygqjjwle",
            "componentInstanceID": "inst-ttnbrdshjqkhhrvgxwvyuaua",
            "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
            "deploymentID": "dep-otflcqpggktnfpljrliimcxu",
            "guid": "job-id",
            "name": "clock",
            "packageID": "pkg-tfmkgibxnutfsjnvzzwicfcg",
            "project": "project-coxqhybvhaaeteaqdwvkstpr",
            "recordOptions": {
                "allTopics": true,
                "chunkSize": 100,
                "compression": "BZ2",
                "maxSplitSize": 1024,
                "maxSplits": 5
            },
            "status": "Stopped"
        },
        "jobID": 74,
        "project": "project-id",
        "status": "Uploading",
        "componentType": "Device"
    }
]
'''

ROSBAG_BLOB_GET_SUCCESS = '''
    {
        "CreatedAt": "2020-09-11T11:28:18.931011Z",
        "DeletedAt": null,
        "ID": 1,
        "UpdatedAt": "2020-09-11T11:28:24.753525Z",
        "blobRefID": 1,
        "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
        "errorMessage": "",
        "filename": "zwfhu_2020-09-11-10-33-12_0.bag",
        "guid": "blob-id",
        "info": {
            "bagVersion": "2.0",
            "compressedSize": 1254923,
            "compression": "bz2",
            "duration": 3224.911953,
            "endTime": 1599823618.628718,
            "indexed": true,
            "messageCount": 117171,
            "messageTypes": [
                {
                    "md5": "992ce8a1687cec8c8bd883ec73ca41d1",
                    "type": "std_msgs/String"
                }
            ],
            "size": 2685732,
            "startTime": 1599820393.716765,
            "topics": [
                {
                    "frequency": 3.9902,
                    "messageCount": 6,
                    "messageType": "std_msgs/String",
                    "name": "/rapyuta_io_peers"
                }
            ],
            "uncompressedSize": 13927913
        },
        "job": {
            "CreatedAt": "2020-09-10T15:00:21.82102Z",
            "DeletedAt": null,
            "Deprovisioned": false,
            "ID": 74,
            "UpdatedAt": "2020-09-11T11:28:24.747798Z",
            "componentID": "fabdmvqbxwrwpjnuygqjjwle",
            "componentInstanceID": "inst-ttnbrdshjqkhhrvgxwvyuaua",
            "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
            "deploymentID": "dep-otflcqpggktnfpljrliimcxu",
            "guid": "job-id",
            "name": "clock",
            "packageID": "pkg-tfmkgibxnutfsjnvzzwicfcg",
            "project": "project-coxqhybvhaaeteaqdwvkstpr",
            "recordOptions": {
                "allTopics": true,
                "chunkSize": 100,
                "compression": "BZ2",
                "maxSplitSize": 1024,
                "maxSplits": 5
            },
            "status": "Stopped"
        },
        "jobID": 74,
        "project": "project-id",
        "status": "Uploading"
    }
'''

ROSBAG_BLOB_GET_WITH_UPLOADED_SUCCESS = '''
    {
        "CreatedAt": "2020-09-11T11:28:18.931011Z",
        "DeletedAt": null,
        "ID": 1,
        "UpdatedAt": "2020-09-11T11:28:24.753525Z",
        "blobRefID": 1,
        "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
        "errorMessage": "",
        "filename": "zwfhu_2020-09-11-10-33-12_0.bag",
        "guid": "blob-id",
        "info": {
            "bagVersion": "2.0",
            "compressedSize": 1254923,
            "compression": "bz2",
            "duration": 3224.911953,
            "endTime": 1599823618.628718,
            "indexed": true,
            "messageCount": 117171,
            "messageTypes": [
                {
                    "md5": "992ce8a1687cec8c8bd883ec73ca41d1",
                    "type": "std_msgs/String"
                }
            ],
            "size": 2685732,
            "startTime": 1599820393.716765,
            "topics": [
                {
                    "frequency": 3.9902,
                    "messageCount": 6,
                    "messageType": "std_msgs/String",
                    "name": "/rapyuta_io_peers"
                }
            ],
            "uncompressedSize": 13927913
        },
        "job": {
            "CreatedAt": "2020-09-10T15:00:21.82102Z",
            "DeletedAt": null,
            "Deprovisioned": false,
            "ID": 74,
            "UpdatedAt": "2020-09-11T11:28:24.747798Z",
            "componentID": "fabdmvqbxwrwpjnuygqjjwle",
            "componentInstanceID": "inst-ttnbrdshjqkhhrvgxwvyuaua",
            "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
            "deploymentID": "dep-otflcqpggktnfpljrliimcxu",
            "guid": "job-id",
            "name": "clock",
            "packageID": "pkg-tfmkgibxnutfsjnvzzwicfcg",
            "project": "project-coxqhybvhaaeteaqdwvkstpr",
            "recordOptions": {
                "allTopics": true,
                "chunkSize": 100,
                "compression": "BZ2",
                "maxSplitSize": 1024,
                "maxSplits": 5
            },
            "status": "Stopped"
        },
        "jobID": 74,
        "project": "project-id",
        "status": "Uploaded"
    }
'''

ROSBAG_BLOB_GET_WITH_ERROR = '''
    {
        "CreatedAt": "2020-09-11T11:28:18.931011Z",
        "DeletedAt": null,
        "ID": 1,
        "UpdatedAt": "2020-09-11T11:28:24.753525Z",
        "blobRefID": 1,
        "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
        "filename": "zwfhu_2020-09-11-10-33-12_0.bag",
        "guid": "blob-id",
        "info": {
            "bagVersion": "2.0",
            "compressedSize": 1254923,
            "compression": "bz2",
            "duration": 3224.911953,
            "endTime": 1599823618.628718,
            "indexed": true,
            "messageCount": 117171,
            "messageTypes": [
                {
                    "md5": "992ce8a1687cec8c8bd883ec73ca41d1",
                    "type": "std_msgs/String"
                }
            ],
            "size": 2685732,
            "startTime": 1599820393.716765,
            "topics": [
                {
                    "frequency": 3.9902,
                    "messageCount": 6,
                    "messageType": "std_msgs/String",
                    "name": "/rapyuta_io_peers"
                }
            ],
            "uncompressedSize": 13927913
        },
        "job": {
            "CreatedAt": "2020-09-10T15:00:21.82102Z",
            "DeletedAt": null,
            "Deprovisioned": false,
            "ID": 74,
            "UpdatedAt": "2020-09-11T11:28:24.747798Z",
            "componentID": "fabdmvqbxwrwpjnuygqjjwle",
            "componentInstanceID": "inst-ttnbrdshjqkhhrvgxwvyuaua",
            "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
            "deploymentID": "dep-otflcqpggktnfpljrliimcxu",
            "guid": "job-id",
            "name": "clock",
            "packageID": "pkg-tfmkgibxnutfsjnvzzwicfcg",
            "project": "project-coxqhybvhaaeteaqdwvkstpr",
            "recordOptions": {
                "allTopics": true,
                "chunkSize": 100,
                "compression": "BZ2",
                "maxSplitSize": 1024,
                "maxSplits": 5
            },
            "status": "Stopped"
        },
        "jobID": 74,
        "project": "project-id",
        "status": "Error",
        "errorMessage": "device offline"
    }
'''

ROSBAG_BLOB_LIST_WITH_UPLOADING_BLOB_SUCCESS = '''
[
    {
        "CreatedAt": "2020-09-11T11:28:18.931011Z",
        "DeletedAt": null,
        "ID": 1,
        "UpdatedAt": "2020-09-11T11:28:24.753525Z",
        "blobRefID": 1,
        "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
        "errorMessage": "",
        "filename": "zwfhu_2020-09-11-10-33-12_0.bag",
        "guid": "blob-id",
        "info": {
            "bagVersion": "2.0",
            "compressedSize": 1254923,
            "compression": "bz2",
            "duration": 3224.911953,
            "endTime": 1599823618.628718,
            "indexed": true,
            "messageCount": 117171,
            "messageTypes": [
                {
                    "md5": "992ce8a1687cec8c8bd883ec73ca41d1",
                    "type": "std_msgs/String"
                }
            ],
            "size": 2685732,
            "startTime": 1599820393.716765,
            "topics": [
                {
                    "frequency": 3.9902,
                    "messageCount": 6,
                    "messageType": "std_msgs/String",
                    "name": "/rapyuta_io_peers"
                }
            ],
            "uncompressedSize": 13927913
        },
        "job": {
            "CreatedAt": "2020-09-10T15:00:21.82102Z",
            "DeletedAt": null,
            "Deprovisioned": false,
            "ID": 74,
            "UpdatedAt": "2020-09-11T11:28:24.747798Z",
            "componentID": "fabdmvqbxwrwpjnuygqjjwle",
            "componentInstanceID": "inst-ttnbrdshjqkhhrvgxwvyuaua",
            "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
            "deploymentID": "dep-otflcqpggktnfpljrliimcxu",
            "guid": "job-id",
            "name": "clock",
            "packageID": "pkg-tfmkgibxnutfsjnvzzwicfcg",
            "project": "project-coxqhybvhaaeteaqdwvkstpr",
            "recordOptions": {
                "allTopics": true,
                "chunkSize": 100,
                "compression": "BZ2",
                "maxSplitSize": 1024,
                "maxSplits": 5
            },
            "status": "Stopped"
        },
        "jobID": 74,
        "project": "project-id",
        "status": "Uploading"
    }
]
'''

ROSBAG_BLOB_LIST_WITH_ERROR_BLOB_SUCCESS = '''
[
    {
        "CreatedAt": "2020-09-11T11:28:18.931011Z",
        "DeletedAt": null,
        "ID": 1,
        "UpdatedAt": "2020-09-11T11:28:24.753525Z",
        "blobRefID": 1,
        "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
        "errorMessage": "",
        "filename": "zwfhu_2020-09-11-10-33-12_0.bag",
        "guid": "blob-id",
        "info": {
            "bagVersion": "2.0",
            "compressedSize": 1254923,
            "compression": "bz2",
            "duration": 3224.911953,
            "endTime": 1599823618.628718,
            "indexed": true,
            "messageCount": 117171,
            "messageTypes": [
                {
                    "md5": "992ce8a1687cec8c8bd883ec73ca41d1",
                    "type": "std_msgs/String"
                }
            ],
            "size": 2685732,
            "startTime": 1599820393.716765,
            "topics": [
                {
                    "frequency": 3.9902,
                    "messageCount": 6,
                    "messageType": "std_msgs/String",
                    "name": "/rapyuta_io_peers"
                }
            ],
            "uncompressedSize": 13927913
        },
        "job": {
            "CreatedAt": "2020-09-10T15:00:21.82102Z",
            "DeletedAt": null,
            "Deprovisioned": false,
            "ID": 74,
            "UpdatedAt": "2020-09-11T11:28:24.747798Z",
            "componentID": "fabdmvqbxwrwpjnuygqjjwle",
            "componentInstanceID": "inst-ttnbrdshjqkhhrvgxwvyuaua",
            "creator": "c08c0d12-23f5-4d3a-b951-14de6d0ff43a",
            "deploymentID": "dep-otflcqpggktnfpljrliimcxu",
            "guid": "job-id",
            "name": "clock",
            "packageID": "pkg-tfmkgibxnutfsjnvzzwicfcg",
            "project": "project-coxqhybvhaaeteaqdwvkstpr",
            "recordOptions": {
                "allTopics": true,
                "chunkSize": 100,
                "compression": "BZ2",
                "maxSplitSize": 1024,
                "maxSplits": 5
            },
            "status": "Stopped"
        },
        "jobID": 74,
        "project": "project-id",
        "status": "Error",
        "componentType": "Device"
    }
]
'''

ROSBAG_BLOB_RETRY_SUCCESS = '''
{
    "status": "Starting"
}
'''

ROSBAG_PATCH_RESPONSE = '''
{
    "ID": 591,
    "CreatedAt": "2022-10-04T11:12:56.080625Z",
    "UpdatedAt": "2022-10-04T12:49:05.629647Z",
    "DeletedAt": null,
    "guid": "job-guid",
    "name": "name",
    "deploymentID": "dep-id",
    "componentInstanceID": "comp-inst-id",
    "packageID": "package-id",
    "deploymentName": "talker",
    "componentID": "comp-id",
    "componentType": "Device",
    "deviceID": "device-id",
    "recordOptions": {
        "allTopics": true,
        "compression": "",
        "maxSplits": 5,
        "maxSplitSize": 1024,
        "chunkSize": 100,
        "prefix": "prefix"
    },
    "uploadOptions": {
        "maxUploadRate": 1048576,
        "uploadType": "Continuous",
        "onDemandOpts": {
            "timeRange": {
                "from": 0,
                "to": 0
            }
        }
    },
    "status": "Running",
    "creator": "creator-id",
    "project": "project-id",
    "deprovisioned": false
}
'''