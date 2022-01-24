BUILD_CREATE_SUCCESS = '''
    {
        "buildName": "test_build",
        "guid": "build-guid"
    }
'''

BUILD_GET_SUCCESS = '''
    {
        "ID": 90,
        "CreatedAt": "2020-07-03T14:47:36.73862Z",
        "UpdatedAt": "2020-07-03T14:50:58.81315Z",
        "DeletedAt": null,
        "guid": "build-guid",
        "buildGeneration": 1,
        "buildName": "test_build",
        "buildInfo": {
            "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
            "branch": "",
            "buildOptions": null,
            "simulationOptions": null,
            "strategyType": "Source",
            "dockerFilePath": "",
            "contextDir": "",
            "architecture": "amd64",
            "isRos": true,
            "rosDistro": "melodic"
        },
        "status": "Complete",
        "ownerProject": "project-uwlzvnyirczyqbpezodmkcxq",
        "creator": "17a0a030-041f-4f11-8f3d-2d682f77f1b5",
        "secret": "",
        "dockerPushSecret" : "",
        "dockerPushRepository" : ""
    }
'''

BUILD_GET_SUCCESS_WITH_BUILD_REQUESTS = '''
    {
    "ID": 271,
    "CreatedAt": "2020-07-11T19:45:43.115488Z",
    "UpdatedAt": "2020-07-11T19:47:56.754122Z",
    "DeletedAt": null,
    "guid": "build-guid",
    "buildGeneration": 1,
    "buildName": "test-build",
    "buildInfo": {
        "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
        "strategyType": "Source",
        "dockerFilePath": "",
        "contextDir": "",
        "architecture": "amd64",
        "isRos": true,
        "rosDistro": "melodic",
        "buildOptions": {
            "catkinOptions": [
                {
                    "rosPkgs": "talker",
                    "cmakeArgs": "",
                    "makeArgs": "",
                    "blacklist": "",
                    "catkinMakeArgs": ""
                }
            ]
        }
    },
    "status": "Complete",
    "ownerProject": "project-uwlzvnyirczyqbpezodmkcxq",
    "creator": "17a0a030-041f-4f11-8f3d-2d682f77f1b5",
    "secret": "",
    "dockerPushSecret" : "",
    "dockerPushRepository" : "",
    "triggerName" : "",
    "tagName" : "",
    "buildRequests": [
        {
            "ID": 403,
            "CreatedAt": "2020-07-11T19:45:43.240767Z",
            "UpdatedAt": "2020-07-11T19:47:56.74891Z",
            "DeletedAt": null,
            "requestId": "IOREQ-ntwpcyqopxvxtpiuoitcaxje",
            "isComplete": true,
            "errorString": "",
            "ownerProject": "project-uwlzvnyirczyqbpezodmkcxq",
            "creator": "17a0a030-041f-4f11-8f3d-2d682f77f1b5",
            "buildGeneration": 1,
            "gitMetadata": {
                "build-cyhunyzbehrkyurbhsfjgdbc": {
                    "author": {
                        "email": "shivamMg@users.noreply.github.com",
                        "name": "Shivam Mamgain"
                    },
                    "commit": "2304d7d279d6bb552ef1928fb73563fc90d700b2",
                    "committer": {
                        "email": "noreply@github.com",
                        "name": "GitHub"
                    },
                    "message": "Merge pull request #28 from pramodhkp/master"
                }
            },
            "executableImageInfo": {
                "imageInfo": [
                    {
                        "artifactID": "build-cyhunyzbehrkyurbhsfjgdbc",
                        "imageName": "rio-project-uwlzvnyirczyqbpezodmkcxq/is-416@sha256:8dbb4ac217ab51224ce074eaf5e8e8ea2bf8b248ed72270831015b4909c3e8f9"
                    }
                ]
            }
        }
    ]
}
'''

BUILD_LIST_SUCCESS = '''
    [
        {
            "ID": 89,
            "CreatedAt": "2020-07-03T14:29:53.501491Z",
            "UpdatedAt": "2020-07-03T14:34:58.829229Z",
            "DeletedAt": null,
            "guid": "build-guid",
            "buildGeneration": 1,
            "buildName": "test_build",
            "buildInfo": {
                "repository": "https://github.com/rapyuta-robotics/io_tutorials.git",
                "branch": "",
                "buildOptions": null,
                "simulationOptions": null,
                "strategyType": "Source",
                "dockerFilePath": "",
                "contextDir": "",
                "architecture": "amd64",
                "isRos": true,
                "rosDistro": "melodic"
            },
            "status": "Complete",
            "ownerProject": "project-uwlzvnyirczyqbpezodmkcxq",
            "creator": "17a0a030-041f-4f11-8f3d-2d682f77f1b5",
            "secret": "",
            "dockerPushSecret" : "",
            "dockerPushRepository" : ""
        }
    ]
'''

BUILD_NOT_FOUND = '''
    {
        "error": "build guid not found"
    }
'''

TRIGGER_BUILD_RESPONSE = '''
    {
    "buildOperationResponse": [
        {
            "buildGUID": "build-guid",
            "buildGenerationNumber": 2,
            "success": true
        }
    ]
}
'''

ROLLBACK_BUILD_RESPONSE = '''
    {
    "buildOperationResponse": [
        {
            "buildGUID": "build-guid",
            "buildGenerationNumber": 1,
            "success": true
        }
    ]
}
'''

BUILD_GUID_NOT_FOUND = '''
    {
    "buildOperationResponse": [
        {
            "buildGUID": "build-guid-1",
            "success": false,
            "error": "build guid not found"
        }
    ]
}
'''

BUILD_IN_PROGRESS_ERROR = '''
    {
    "buildOperationResponse": [
        {
            "buildGUID": "build-guid",
            "success": false,
            "error": "build is in BuildInProgress state"
        }
    ]
}
'''
