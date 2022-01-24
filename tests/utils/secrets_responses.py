SECRET_CREATE_SUCCESS = '''
{
    "ID": 4823,
    "CreatedAt": "2020-10-19T13:22:18.446113565Z",
    "UpdatedAt": "2020-10-19T13:22:18.446113565Z",
    "DeletedAt": null,
    "guid": "secret-guid",
    "name": "test-secret",
    "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
    "projectGUID": "project-guid",
    "data": {
        "password": "YXNkYXNk",
        "username": "YXNkYXNk"
    },
    "type":"kubernetes.io/basic-auth"
}
'''

SECRET_LIST_SUCCESS = '''
[
    {
        "ID": 4823,
        "CreatedAt": "2020-10-19T13:22:18.446113565Z",
        "UpdatedAt": "2020-10-19T13:22:18.446113565Z",
        "DeletedAt": null,
        "guid": "secret-guid",
        "name": "test-secret-1",
        "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
        "projectGUID": "project-guid",
        "data": {
            "password": "YXNkYXNk",
            "username": "YXNkYXNk"
        },
        "type":"kubernetes.io/basic-auth"
    },
    {
        "ID": 4824,
        "CreatedAt": "2020-10-19T13:22:18.446113565Z",
        "UpdatedAt": "2020-10-19T13:22:18.446113565Z",
        "DeletedAt": null,
        "guid": "secret-guid",
        "name": "test-secret-2",
        "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
        "projectGUID": "project-guid",
        "data": {
            "password": "YXNkYXNk",
            "username": "YXNkYXNk"
        },
        "type":"kubernetes.io/basic-auth"
    }
]
'''
