NATIVE_NETWORK_CREATE_SUCCESS = '''
{
        "name": "native_network_name",
        "guid": "net-guid"
    }
'''

NATIVE_NETWORK_GET_SUCCESS = '''
    {
        "ID": 1,
        "CreatedAt": "2021-02-05T13:16:08.736362Z",
        "UpdatedAt": "2021-02-05T13:16:08.736362Z",
        "DeletedAt": null,
        "name": "native_network_name",
        "guid": "net-guid",
        "ownerProject": "project-id",
        "creator": "creator-id",
        "runtime": "cloud",
        "rosDistro": "kinetic",
        "internalDeploymentGUID": "dep-id",
        "internalDeploymentStatus": {
            "phase": "Succeeded",
            "status": "Running"
        },
        "parameters": {
            "limits": {
                "cpu": 1,
                "memory": 4096
            }
        }
    }
'''

NATIVE_NETWORK_LIST_SUCCESS = '''
[	
    {
        "ID": 1,
        "CreatedAt": "2021-02-05T13:16:08.736362Z",
        "UpdatedAt": "2021-02-05T13:16:08.736362Z",
        "DeletedAt": null,
        "name": "native_network_name",
        "guid": "net-guid",
        "ownerProject": "project-id",
        "creator": "creator-id",
        "runtime": "cloud",
        "rosDistro": "kinetic",
        "internalDeploymentGUID": "dep-id",
        "internalDeploymentStatus": {
            "phase": "Succeeded"
        },
        "parameters": {
            "limits": {
                "cpu": 1,
                "memory": 4096
            }
        }
    }
]
'''

NATIVE_NETWORK_FAILURE = '''
    {
        "ID": 1,
        "CreatedAt": null,
        "UpdatedAt": null,
        "DeletedAt": null,
        "name": "native_network_name",
        "guid": "net-guid",
        "ownerProject": "project-id",
        "creator": "creator-id",
        "runtime": "cloud",
        "rosDistro": "kinetic",
        "internalDeploymentGUID": "dep-id",
        "internalDeploymentStatus": {
            "error_code": ["DEP_E209"],
            "phase": "Failed to start"
        },
        "parameters": {
            "limits": {
                "cpu": 1,
                "memory": 4096
            }
        }
    }
'''

NATIVE_NETWORK_NOT_FOUND = '''
    {
        "error": "native network not found in db"
    }
'''