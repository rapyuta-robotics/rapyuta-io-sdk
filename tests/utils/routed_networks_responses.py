ROUTED_NETWORK_CREATE_SUCCESS = '''
{
    "name": "test-network",
    "guid": "net-testguid"
}
'''

ROUTED_NETWORK_GET_SUCCESS = '''
{
    "ID": 15,
    "CreatedAt": "2020-04-28T04:18:06.940902Z",
    "UpdatedAt": "2020-04-28T04:18:06.940902Z",
    "DeletedAt": null,
    "name": "test-network",
    "guid": "net-testguid",
    "ownerProject": "test_project",
    "creator": "test_user",
    "runtime": "cloud",
    "rosDistro": "",
    "shared": true,
    "internalDeploymentGUID": "dep-nxmssipisiyqyidpmmmmhszk",
    "internalDeploymentStatus": {
        "error_code": [],
        "phase": "Succeeded",
        "status": "Running"
    },
    "parameters": {
        "cpu": 1,
        "device_id": "284f8d22-9cbe-457e-89b5-41f1d07d0657"
    }
}
'''

ROUTED_NETWORK_LIST_SUCCESS = '''
[{
    "ID": 15,
    "CreatedAt": "2020-04-28T04:18:06.940902Z",
    "UpdatedAt": "2020-04-28T04:18:06.940902Z",
    "DeletedAt": null,
    "name": "test-network",
    "guid": "net-testguid",
    "ownerProject": "test_project",
    "creator": "test_user",
    "runtime": "cloud",
    "rosDistro": "",
    "shared": true,
    "internalDeploymentGUID": "dep-nxmssipisiyqyidpmmmmhszk",
    "internalDeploymentStatus": {
        "error_code": [],
        "phase": "Succeeded"
    },
    "parameters": {
        "cpu": 1,
        "device_id": "284f8d22-9cbe-457e-89b5-41f1d07d0657"
    }
}]
'''

ROUTED_NETWORK_NOT_FOUND = '''
    {
        "error": "routed network not found in db"
    }
'''